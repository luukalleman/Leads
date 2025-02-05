
from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def fetch_contacts_from_supabase(limit=50):
    """
    Fetch contacts from the Supabase database where sent is false 
    and linkedin_posts is not null.

    Args:
        limit (int): The maximum number of contacts to fetch.

    Returns:
        list: A list of contacts that match the criteria.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        response = supabase.table("leads").select("*") \
            .eq("sent", False) \
            .is_("generated_content", None) \
            .neq("linkedin_posts", None) \
            .limit(limit) \
            .execute()

        print(response)
        if response.data:
            return response.data
        else:
            print("No matching contacts found in Supabase.")
            return []
    except Exception as e:
        print(f"Error fetching contacts from Supabase: {e}")
        return []


def save_to_supabase(contacts, page_number):
    """
    Save enriched contacts to Supabase with additional fields.
    """
    print("Starting save_to_supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    for contact in contacts:
        # Extract and clean the data
        data = {
            "first_name": contact.get("first_name"),
            "last_name": contact.get("last_name"),
            "email": contact.get("email"),
            "job_title": contact.get("title"),
            "company_name": contact.get("organization", {}).get("name"),
            "linkedin_url": contact.get("linkedin_url"),
            "website": contact.get("organization", {}).get("website_url"),
            "sent": False,  # Default to False
            "page_number": page_number,  # Store the page number
            "headline": contact.get("headline"),
        }

        # Remove any None values to ensure a clean payload
        data = {key: value for key, value in data.items() if value is not None}

        print(f"Attempting to save contact: {data}")

        try:
            # Send the data to the Supabase leads table
            response = supabase.table("leads").insert(data).execute()
        except Exception as e:
            print(
                f"An error occurred while saving contact: {contact.get('email')}, Error: {e}")


def update_contact_info(contact_id, body, language, subject, send_directly):
    """
    Update the 'sent' status of a contact in the Supabase database to True.

    Args:
        contact_id (int): The ID of the contact to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        if send_directly:
            # Update the 'sent' field to True for the specified contact
            response = supabase.table("leads").update(
                {
                    "sent": True,          # Set the sent field to True
                    "generated_content": body,    # Store the generated email body
                    "language": language,    # Store the language
                    "subject": subject
                }
            ).eq("id", contact_id).execute()
        else:
            response = supabase.table("leads").update(
                {
                    "generated_content": body,    # Store the generated email body
                    "language": language,    # Store the language
                    "subject": subject
                }
            ).eq("id", contact_id).execute()
    except Exception as e:
        print(f"Error updating sent status: {e}")
        return False


def update_contact_linkedin(contact_id, posts):
    """
    Update the 'sent' status of a contact in the Supabase database to True.

    Args:
        contact_id (int): The ID of the contact to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        # Update the 'sent' field to True for the specified contact
        response = supabase.table("leads").update(
            {
                "linkedin_posts": posts,    # Store the generated email body
            }
        ).eq("id", contact_id).execute()

    except Exception as e:
        print(f"Error updating sent status: {e}")
        return False


def get_highest_page():
    """
    Get the highest page number from the leads table in Supabase.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("leads").select("page_number").order(
            "page_number", desc=True).limit(1).execute()
        if response.data:
            highest_page = response.data[0]["page_number"]
            return highest_page
        else:
            print("No page numbers found in the leads table. Starting from page 1.")
            return 1
    except Exception as e:
        print(f"Error fetching highest page number: {e}")
        return 1


def contact_exists_in_supabase(first_name, last_name, company_name):
    """
    Check if a contact with the given first name, last name, and company name exists in the Supabase database.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        query = supabase.table("leads").select("*").eq("first_name", first_name)

        # Handle missing last name
        if last_name:
            query = query.eq("last_name", last_name)
        
        # Handle missing company name
        if company_name:
            query = query.eq("company_name", company_name)

        response = query.execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking contact existence: {e}")
        return False


def fetch_all_contacts():
    """
    Fetch all contacts from the Supabase leads table.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("leads").select("*").range(0, 2000).execute()
        if response.data:
            print(len(response.data))
            return response.data
        else:
            print("No data found in the leads table.")
            return []
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []


def fetch_all_contacts_linkedin():
    """
    Fetch all contacts from the Supabase leads table.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("leads").select("*") \
            .eq("sent", False) \
            .is_("linkedin_posts", None).execute()
        if response.data:
            print(response.data)
            return response.data
        else:
            print("No data found in the leads table.")
            return []
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []


def find_duplicate_email_ids(data):
    """
    Find duplicate email IDs, keeping the first occurrence.
    """
    df = pd.DataFrame(data)
    duplicate_ids = df[df.duplicated("email", keep="first")]["id"].tolist()
    return duplicate_ids


def remove_duplicates_from_supabase(duplicate_ids):
    """
    Remove duplicates from Supabase by ID.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    if not duplicate_ids:
        print("No duplicate emails to remove.")
        return

    print(f"Removing {len(duplicate_ids)} duplicate email records...")
    try:
        response = supabase.table("leads").delete().in_(
            "id", duplicate_ids).execute()
    except Exception as e:
        print(f"Error removing duplicate emails: {e}")


def fetch_sent_contacts_from_supabase():
    """
    Fetch contacts from Supabase where 'sent' is True.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("leads").select(
            "*").eq("sent", True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching sent contacts: {e}")
        return []

def update_contact_field(contact_id, updates):
    """
    Update one or more fields for a contact in the Supabase database.

    Args:
        contact_id (int): The ID of the contact to update.
        updates (dict): A dictionary of fields and values to update.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        response = supabase.table("leads").update(updates).eq("id", contact_id).execute()
    except Exception as e:
        print(f"Error updating contact {contact_id}: {e}")
        return False