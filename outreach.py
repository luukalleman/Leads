import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.database.supabase_functions import fetch_sent_contacts_from_supabase, fetch_contacts_from_supabase, update_contact_info
from app.gmail.send_email import GmailService
from app.linkedin.get_posts import LinkedInScraper
from app.websites.get_website_analysis import WebsiteAnalyzer
from app.ai.prompts import get_email_prompt


class EmailGenerator:
    def __init__(self, openai_api_key):
        """
        Initialize the EmailGenerator with an OpenAI API key.
        """
        load_dotenv()
        self.client = OpenAI(api_key=openai_api_key)

    def clean_email_content(self, content):
        """
        Removes unwanted characters or formatting artifacts from the email content,
        keeping only the HTML content.
        """
        import re
        # Use regex to extract content within the HTML code block
        match = re.search(r"```html(.*?)```", content, re.DOTALL)
        if match:
            # Strip any extra whitespace around the HTML content
            return match.group(1).strip()
        else:
            # If no HTML block is found, return the stripped content as a fallback
            return content.strip()

    def generate_email(self, contact, insights=None, first_line=None, language="NL", category=None):
        """
        Generates a personalized cold email based on contact information and insights.
        """
        retries = 0
        max_retries = 5  # Maximum number of retries
        wait_time = 10   # Initial wait time in seconds

        while retries < max_retries:
            try:
                first_name = contact.get("first_name", "")
                headline = contact.get("headline", "")

                # Generate the AI prompt
                prompt, sys_message = get_email_prompt(
                    first_name, first_line, insights, language, headline, category
                )

                completion = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": sys_message},
                        {"role": "user", "content": prompt}
                    ]
                )

                email_content = completion.choices[0].message.content

                # Clean the email content using the class's method
                clean_content = self.clean_email_content(email_content)
                return clean_content

            except Exception as e:
                error_message = str(e)
                print(f"Error generating email: {error_message}")

                # Check if it's a rate-limit error (429)
                if "429" in error_message or "rate limit" in error_message:
                    retries += 1
                    print(
                        f"Rate limit exceeded. Retrying in {wait_time} seconds... ({retries}/{max_retries})")
                    time.sleep(wait_time)
                    wait_time *= 2  # Exponential backoff
                else:
                    # For other errors, break and return an error message
                    break
        return None


class AIAutomation:
    def __init__(self, email_generator):
        self.email_generator = email_generator

    def generate_email_for_contact(self, contact):
        """
        Generates a personalized cold email based on company data and contact information.
        """
        company_url = contact.get("website", "")
        posts = contact.get("linkedin_posts", None)
        # Initialize the LinkedInScraper
        linkedin_scraper = LinkedInScraper(api_key=os.getenv(
            "OPENAI_API_KEY"), apify_token=os.getenv("APIFY_TOKEN"))

        # Scrape LinkedIn posts and generate insights
        if posts and posts != 'false':
            print("Analyzing LinkedIn content...")
            first_line, language, category = linkedin_scraper.generate_first_line(
                posts, f"{contact['first_name']} {contact['last_name']}")
        else:
            print("No LinkedIn URL provided.")
            first_line, language, category = None, "EN", None
        # Initialize the WebsiteAnalyzer
        website_analyzer = WebsiteAnalyzer()
        print(company_url)
        if company_url:
            print("Scraping website content...")
            website_content = website_analyzer.scrape_website(company_url)
        else:
            print("No company URL provided.")
            website_content = None
        if website_content and len(website_content) > 500:
            print("Analyzing website content...")
            insights = website_analyzer.analyze_website_content(
                website_content, language)
            print("insights: ", insights)
        else:
            insights = None

        email_content = self.email_generator.generate_email(
            contact=contact, insights=insights, first_line=first_line, language=language, category=category
        )

        return email_content, language


class EmailAutomationApp:
    def __init__(self, email_generator, gmail_service):
        """
        Initialize the EmailAutomationApp with an email generator and Gmail service.

        Args:
            email_generator: An instance of a class responsible for generating emails.
            gmail_service: An instance of the GmailService class for managing Gmail interactions.
        """
        self.email_generator = email_generator
        self.gmail_service = gmail_service

    def check_for_responses(self, service):
        """
        Check for responses to sent emails and update the database.
        """
        print("Checking for email responses...")
        sent_emails = fetch_sent_contacts_from_supabase()  # Fetch sent emails

        if not sent_emails:
            print("No sent emails found to check for responses.")
            return

        # Logic to fetch responses from Gmail
        responded_emails = self.gmail_service.fetch_email_responses(
            service, sent_emails)

        for email_id in responded_emails:
            # Update the database
            update_contact_info(email_id, responded=True)

    def run(self, emails_to_send=5, send_directly=False):
        """
        Main function to fetch contacts, generate emails, and update contact info.

        Args:
            emails_to_send (int): The number of emails to process.
        """
        # Step 1: Fetch contacts from Supabase
        contacts = fetch_contacts_from_supabase(limit=emails_to_send)
        if not contacts:
            print("No contacts available in Supabase.")
            return

        # Limit to the specified number of emails
        contacts = contacts[:emails_to_send]

        # Step 2: Retrieve Gmail access token
        access_token = self.gmail_service.get_access_token()
        if not access_token:
            print("Error: Unable to get Gmail access token.")
            return

        # Step 3: Build the Gmail service
        service = self.gmail_service.build_service(access_token)

        # Step 4: Process each contact
        for index, contact in enumerate(contacts, start=1):
            print(f"Processing contact {index}/{emails_to_send}")
            contact_id = contact.get("id")
            recipient_email = contact.get("email")

            if recipient_email:
                # Generate AI-written email content
                ai_written_content, language = self.email_generator.generate_email_for_contact(
                    contact)
                subject = (
                    "Niet geschoten is altijd mis.. Kort vraagje!"
                    if language.lower() == "nl" else "Quick question!"
                )
                if ai_written_content:
                    # Determine email subject based on language
                    # Clean email content and add signature
                    clean_body = self.gmail_service.clean_email_content(
                        ai_written_content)
                    signature = """
                        <div>
                            Luuk Alleman<br>
                            <i>AI Developer | Founder at Everyman AI</i><br>
                            🌐 <a href="https://www.everyman.ai">www.everyman.ai</a><br>
                            📄 <a href="https://www.everyman.ai/Luuk">About Me</a><br>
                            📍 Korte Hogendijk 16, 1506 MA Zaandam, NL<br>
                        </div>
                        <div style="margin-top: 10px;">
                            <img src="https://drive.google.com/uc?id=1N8tyQq-5-auV8UGakyjXL0tszgbjs4gB" 
                                alt="Everyman AI Logo" style="width: 100px; height: auto;">
                        </div>
                        <div style="margin-top: 10px;">
                            <a href="https://www.everyman.ai/unsubscribe" style="text-decoration: none; color: #007bff;">
                                Unsubscribe
                            </a>
                        </div>
                    """
                    email_body = f"{clean_body}{signature}"
                    print(f"Generated this email: {email_body}")
                    # Send email
                    if send_directly:
                        send_response = self.gmail_service.send_email(
                            service, "luuk@everyman.ai", recipient_email, subject, email_body
                        )
                        if send_response:
                            print("Email successfully sent!")
                    #Update contact info in the database
                update_contact_info(
                    contact_id, ai_written_content, language, subject, send_directly)
            else:
                print(f"No email found for contact: {contact}")

            # Stop if the specified number of emails has been processed
            if index >= emails_to_send:
                print(f"Reached the limit of {emails_to_send} emails.")
                break
        self.check_for_responses(service)


if __name__ == "__main__":
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gmail_service = GmailService()
    email_generator = EmailGenerator(openai_api_key=openai_api_key)
    ai_automation = AIAutomation(email_generator=email_generator)
    app = EmailAutomationApp(
        email_generator=ai_automation, gmail_service=gmail_service)
    app.run()
