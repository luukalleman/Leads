import os
import time
import requests
from dotenv import load_dotenv
from app.database.supabase_functions import (
    fetch_all_contacts,
    find_duplicate_email_ids,
    remove_duplicates_from_supabase,
    save_to_supabase,
    get_highest_page,
    contact_exists_in_supabase,
    fetch_all_contacts_linkedin,update_contact_linkedin
)
from app.linkedin.get_posts import LinkedInScraper

# Load environment variables
load_dotenv()


class ApolloContactManager:
    """
    A class to manage fetching, filtering, enriching, and saving contacts from Apollo API.
    """

    def __init__(self):
        self.api_key = os.getenv("APOLLO_API_KEY")
        self.api_url = os.getenv("APOLLO_API_URL")
        self.enrichment_url = os.getenv("APOLLO_ENRICHMENT_URL")
        self.headers = {
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

    def fetch_contacts(self, payload):
        """
        Fetch contacts from Apollo API.
        """

        response = requests.post(
            self.api_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json().get("people", [])
        else:
            print(
                f"Error during fetch_contacts: {response.status_code}, {response.text}")
            return []

    def filter_existing_contacts(self, contacts):
        """
        Filter out contacts that already exist in the Supabase database.
        """
        print("Filtering out existing contacts...")
        return [
            contact
            for contact in contacts
            if not contact_exists_in_supabase(
                contact.get("first_name"),
                contact.get("last_name"),
                contact.get("company_name")
            )
        ]

    def enrich_contacts_in_batches(self, contacts, batch_size=10):
        """
        Enrich contacts in batches using Apollo Enrichment API.
        """
        print("Starting enrich_contacts_in_batches...")
        enriched_results = []

        for i in range(0, len(contacts), batch_size):
            batch = contacts[i: i + batch_size]
            print(f"Enriching batch of {len(batch)} contacts...")

            payload = {
                "reveal_personal_emails": True,
                "details": [
                    {
                        key: value
                        for key, value in {
                            "first_name": contact.get("first_name"),
                            "last_name": contact.get("last_name"),
                            "organization_domain": contact.get("organization", {}).get("primary_domain"),
                            "linkedin_url": contact.get("linkedin_url"),
                            "title": contact.get("title"),
                        }.items()
                        if value is not None
                    }
                    for contact in batch
                ],
            }

            retries = 0
            max_retries = 3

            while retries < max_retries:
                response = requests.post(
                    self.enrichment_url, json=payload, headers=self.headers)

                if response.status_code == 200:
                    enriched_results.extend(response.json().get("matches", []))
                    break
                elif response.status_code == 429:
                    print("Rate limit exceeded. Waiting 60 seconds before retrying...")
                    time.sleep(60)
                    retries += 1
                else:
                    print(
                        f"Failed to enrich batch: {response.status_code}, {response.text}")
                    break

            if retries == max_retries:
                print("Max retries reached. Skipping this batch.")

        return enriched_results

    def update_linkedin_posts(self):
        """
        Fetch contacts with null LinkedIn posts, scrape posts using LinkedInScraper, and update the database.
        """
        print("Fetching contacts with missing LinkedIn posts...")

        # Fetch contacts from the database with null LinkedIn posts
        contacts = fetch_all_contacts_linkedin()

        if not contacts:
            print("No contacts found with missing LinkedIn posts.")
            return
        # Initialize the LinkedIn scraper
        linkedin_scraper = LinkedInScraper(
            api_key=os.getenv("OPENAI_API_KEY"),
            apify_token=os.getenv("APIFY_TOKEN")
        )

        # Loop through contacts and scrape LinkedIn posts
        count = 0
        for contact in contacts:
            if count == 0:
                linkedin_url = contact.get("linkedin_url")
                if linkedin_url:
                    print(
                        f"Scraping LinkedIn posts for {contact.get('first_name')} {contact.get('last_name')}...")
                    try:
                        posts = linkedin_scraper.scrape_linkedin_posts(
                            linkedin_url)

                        # Save the scraped data to the database
                        update_result = update_contact_linkedin(contact.get("id"),posts)
                        print(
                            f"Updated LinkedIn posts for {contact.get('first_name')} {contact.get('last_name')}.")
                    except Exception as e:
                        print(
                            f"Error scraping LinkedIn posts for {contact.get('first_name')} {contact.get('last_name')}: {e}")
                else:
                    print(
                        f"No LinkedIn URL for {contact.get('first_name')} {contact.get('last_name')}.")

    def remove_duplicates(self):
        """
        Remove duplicate emails from the Supabase database.
        """
        contacts = fetch_all_contacts()
        if not contacts:
            print("No contacts to process.")
            return

        print("\nChecking for duplicate emails...")
        duplicate_email_ids = find_duplicate_email_ids(contacts)
        if duplicate_email_ids:
            print(
                f"Found {len(duplicate_email_ids)} duplicate emails to remove.")
            remove_duplicates_from_supabase(duplicate_email_ids)
        else:
            print("No duplicate emails found.")

    def run(self, max_contacts=10, start_page=get_highest_page(), payload=None):
        """
        Main workflow to fetch, filter, enrich, and save contacts.
        """
        print("Starting Apollo Contact Manager...")
        if not payload:
            payload = {
                "person_titles": ["Manager", "Project Manager", "Founder", "Owner", "CEO", "Director", "Product Owner"],
                "person_locations": ["Netherlands"],
                "contact_email_status": "verified",
                "organization_num_employees_ranges": ["1,10", "11,20"],
                "per_page": min(25, max_contacts),
                "page": start_page,
            }
        total_fetched = 0

        print(
            f"Starting from page {start_page}, targeting {max_contacts} contacts...")
        while total_fetched < max_contacts:
            contacts = self.fetch_contacts(payload=payload)
            if not contacts:
                print("No more contacts available to fetch.")
                break

            contacts_to_enrich = self.filter_existing_contacts(contacts)
            remaining_contacts = max_contacts - total_fetched
            contacts_to_enrich = contacts_to_enrich[:remaining_contacts]

            print(f"Filtered down to {len(contacts_to_enrich)} new contacts.")
            total_fetched += len(contacts_to_enrich)

            print("Enriching contacts in batches...")
            enriched_contacts = self.enrich_contacts_in_batches(
                contacts_to_enrich)

            if enriched_contacts:
                print(
                    f"Enriched {len(enriched_contacts)} contacts. Saving to Supabase...")
                save_to_supabase(enriched_contacts, start_page)
            else:
                print("No contacts were enriched.")

            start_page += 1

        self.remove_duplicates()
        self.update_linkedin_posts()
        return enriched_contacts
if __name__ == "__main__":
    # Run the Apollo Contact Manager with a maximum of 88 contacts
    manager = ApolloContactManager()
    manager.run(max_contacts=1)
