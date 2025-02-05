import streamlit as st
import pandas as pd
from app.database.supabase_functions import fetch_all_contacts, update_contact_info, update_contact_field
from supabase import create_client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import requests
from streamlit_modal import Modal
from outreach import EmailAutomationApp, EmailGenerator, AIAutomation, GmailService
from retrieve_contacts import ApolloContactManager
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Clear existing environment variables for debugging
# os.environ.pop("APIFY_TOKEN", None)


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.client = create_client(self.url, self.key)

    def fetch_unsent_emails(self):
        try:
            response = self.client.table("leads").select(
                "*").eq("sent", False).filter("generated_content", "neq", None).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching unsent emails: {e}")
            return []

    def update_sent_status(self, contact_id):
        try:
            # Get the current date in the desired format
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update the 'sent' field and add the 'sent_date' field with the current date
            self.client.table("leads").update(
                {
                    "sent": True,
                    "sent_at": current_date  # Add the current date as 'sent_date'
                }
            ).eq("id", contact_id).execute()
        except Exception as e:
            print(e)
            st.error(f"Error updating sent status: {e}")

    def update_generated_content(self, contact_id, new_content):
        try:
            self.client.table("leads").update(
                {"generated_content": new_content}).eq("id", contact_id).execute()
            st.success("Content updated successfully!")
        except Exception as e:
            st.error(f"Error updating content: {e}")

    def fetch_sent_emails(self):
        try:
            response = self.client.table("leads").select(
                "*").eq("sent", True).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching sent emails: {e}")
            return []


class GmailClient:
    def __init__(self):
        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
        self.access_token_url = "https://oauth2.googleapis.com/token"

    def get_access_token(self):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(self.access_token_url, data=payload)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            st.error(f"Failed to get Gmail access token: {response.json()}")
            return None

    def build_service(self, access_token):
        credentials = Credentials(access_token)
        return build("gmail", "v1", credentials=credentials)

    @staticmethod
    def create_email_message(sender, recipient, subject, body):
        """
        Create an email message.
        """
        message = MIMEText(body, "html")  # Email body is treated as HTML
        message["to"] = recipient
        message["from"] = sender
        message["subject"] = subject

        # Encode the message in base64
        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()).decode("utf-8")
        return {"raw": encoded_message}

    def send_email(self, service, sender, recipient, subject, body):
        """
        Send an email using the Gmail API.
        """
        try:
            message = self.create_email_message(
                sender, recipient, subject, body)
            send_message = service.users().messages().send(
                userId="me", body=message).execute()
            print("Email sent!")
            return send_message
        except Exception as e:
            print(f"Failed to send email: {e}")
            return None

    def check_email_responses(self, service, sent_emails):
        """
        Check the inbox for responses to sent emails.
        """
        try:
            response_ids = []

            for email in sent_emails:
                recipient = email.get("email")
                query = f"from:{recipient} is:unread"
                results = service.users().messages().list(userId="me", q=query).execute()
                messages = results.get("messages", [])

                if messages:
                    response_ids.append(email["id"])
            return response_ids
        except Exception as e:
            print(e)
            st.error(f"Error checking email responses: {e}")
            return []

# Check for responses and update database


def check_for_responses():
    supabase_client = SupabaseClient()
    gmail_client = GmailClient()

    sent_emails = supabase_client.fetch_sent_emails()
    if not sent_emails:
        st.info("No sent emails found to check for responses.")
        return

    access_token = gmail_client.get_access_token()
    if not access_token:
        st.error("Failed to get Gmail access token for checking responses.")
        return

    service = gmail_client.build_service(access_token)
    responded_emails = gmail_client.check_email_responses(service, sent_emails)

    for email_id in responded_emails:
        update_contact_info(email_id, responded=True)

# Dashboard tab


def dashboard_tab():
    supabase_client = SupabaseClient()

    st.title("Email Campaign Dashboard")
    st.write("Track your email campaigns with key metrics and insights.")

    if st.button("Refresh Dashboard Data"):
        st.cache_data.clear()  # Clear cached data to ensure fresh fetch
        st.experimental_rerun()

    @st.cache_data
    def load_data():
        data = fetch_all_contacts()
        return pd.DataFrame(data)

    data = load_data()
    if data.empty:
        st.warning("No data found in the database.")
    else:
        # Calculate metrics
        total_contacts = data.shape[0]
        total_emails_sent = data[data["sent"] == True].shape[0]
        total_responses = data[(data["sent"] == True) & (
            data["responded"] == True)].shape[0]
        unsent_emails = data[data["sent"] == False].shape[0]
        response_rate = (total_responses / total_emails_sent) * \
            100 if total_emails_sent > 0 else 0

        # Key Metrics Section
        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Contacts", total_contacts)
        with col2:
            st.metric("Total Emails Sent", total_emails_sent)
        with col3:
            st.metric("Response Rate", f"{response_rate:.2f}%")

        # Additional Metrics Section
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Emails Still to Send", unsent_emails)
        with col5:
            st.metric("Total Responses Received", total_responses)

        # Detailed Views Section
        st.subheader("Detailed Views")

        # Responded Emails View
        st.write("### Responded Emails")
        responded_emails = data[(data["sent"] == True)
                                & (data["responded"] == True)]
        st.dataframe(responded_emails)

        # Check if required columns exist
        if {"linkedin_clicked", "sent_at", "first_name", "last_name", "company_name", "linkedin_url"}.issubset(data.columns):
            pending_linkedin_clicks = data[data["linkedin_clicked"].isnull() & data["sent_at"].notnull()]

            if pending_linkedin_clicks.empty:
                st.info("No pending LinkedIn clicks found.")
            else:
                st.write("### Last 25 Pending LinkedIn Profiles")
                
                # Display a custom table with name, company, and LinkedIn button
                for _, row in pending_linkedin_clicks.tail(25).iterrows():
                    name = f"{row['first_name']} {row['last_name']}"
                    company = row["company_name"] or "N/A"
                    linkedin_url = row["linkedin_url"]
                    contact_id = row["id"]

                    col1, col2, col3 = st.columns([3, 3, 2])
                    with col1:
                        st.write(f"**{name}**")
                    with col2:
                        st.write(company)
                    with col3:
                        if st.button(f"Open LinkedIn", key=f"linkedin_{contact_id}"):
                            # Update the database field before opening the URL
                            supabase_client.client.table("leads").update({
                                "linkedin_clicked": datetime.now().isoformat()
                            }).eq("id", contact_id).execute()

                            # Trigger new tab opening for the LinkedIn profile
                            js_code = f"window.open('{linkedin_url}', '_blank')"
                            st.components.v1.html(f"<script>{js_code}</script>", height=0)
                            st.cache_data.clear()  # Clear cached data to force a fresh fetch
                            st.experimental_rerun()
        else:
            st.warning("Required columns ('linkedin_clicked', 'sent_at', 'first_name', 'last_name', 'company_name', or 'linkedin_url') are missing.")

def log_responses_tab():
    st.title("Log Responses")
    st.write("Search for contacts and update their status.")

    # Fetch all contacts and convert to DataFrame
    @st.cache_data
    def load_contact_data():
        data = fetch_all_contacts()
        return pd.DataFrame(data)

    contacts_df = load_contact_data()

    if contacts_df.empty:
        st.warning("No contacts found in the database.")
        return

    # Search functionality with condition to prevent immediate display
    search_query = st.text_input("Search by name or email")

    if not search_query.strip():
        st.info("Please enter a search term to display contacts.")
        return

    # Filter contacts based on search input
    filtered_contacts = contacts_df[
        contacts_df["email"].str.contains(search_query, case=False, na=False) |
        contacts_df["first_name"].str.contains(search_query, case=False, na=False) |
        contacts_df["last_name"].str.contains(
            search_query, case=False, na=False)
    ]

    if filtered_contacts.empty:
        st.info("No contacts match your search.")
    else:
        for _, contact in filtered_contacts.iterrows():
            name = f"{contact['first_name']} {contact['last_name']}"
            email = contact["email"]
            responded = contact["responded"]
            follow_up = contact.get("follow_up", True)

            st.write(f"### {name} ({email})")

            # Create two columns for the checkboxes
            col1, col2 = st.columns(2)

            with col1:
                # Checkbox for marking as responded
                response_checkbox = st.checkbox(
                    "Mark as responded", value=responded, key=f"response_{contact['id']}"
                )

            with col2:
                # Checkbox for marking as "don't follow up"
                follow_up_checkbox = st.checkbox(
                    "Mark as don't follow up", value=not follow_up, key=f"follow_up_{contact['id']}"
                )

            # Update 'responded' status
            if response_checkbox and not responded:
                update_contact_field(contact["id"], {"responded": True})
                st.success(f"Response status updated for {name}.")
                st.experimental_rerun()

            # Update 'follow_up' status
            if follow_up_checkbox and follow_up:
                update_contact_field(contact["id"], {"followup": False})
                st.success(f"Follow-up status updated for {name}.")
                st.experimental_rerun()
            # Add a divider to separate each contact visually
            st.divider()


def email_automation_and_sending_tab():
    st.title("Email Automation & Sending Dashboard")

    # Initialize services and clients
    supabase_client = SupabaseClient()
    gmail_client = GmailService()
    email_generator = EmailGenerator(
        openai_api_key=os.getenv("OPENAI_API_KEY"))
    ai_automation = AIAutomation(email_generator=email_generator)
    automation_app = EmailAutomationApp(
        email_generator=ai_automation, gmail_service=gmail_client)

    # New Button to Send All Emails Ready for Review
    if st.button("Send All Emails Ready for Review"):
        contacts = supabase_client.fetch_unsent_emails()
        if not contacts:
            st.info("No emails to send.")
        else:
            access_token = gmail_client.get_access_token()
            if access_token:
                service = gmail_client.build_service(access_token)
                for contact in contacts:
                    email = contact["email"]
                    generated_content = contact.get("generated_content", "No content available")
                    subject = contact.get("subject", "Quick question!")
                    name = contact.get("first_name")

                    signature = """
                        <div>
                            Luuk Alleman<br>
                            <i>AI Developer | Founder at Everyman AI</i><br>
                            🌐 <a href="https://www.everyman.ai">www.everyman.ai</a><br>
                            📄 <a href="https://www.everyman.ai/luuk">You are probably wondering who I am, here's everything you need to know about me.</a><br>
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
                    email_body = f"<p>{generated_content}{signature}</p>"
                    response = gmail_client.send_email(service, "hi@everyman.ai", email, subject, email_body)
                    supabase_client.update_sent_status(contact["id"])

                st.success("All emails ready for review have been sent!")
            else:
                st.error("Failed to authenticate with Gmail. Please check your credentials.")
    # Input for batch size and action selection
    emails_to_send = st.selectbox(
        "Number of emails to process in this batch",
        options=[1, 5, 10, 20, 50, 100],
        index=0
    )

    email_action = st.radio(
        "What would you like to do?",
        options=["Save emails for review", "Send emails directly"],
        index=0
    )

    # Automation process button
    if st.button("Run Email Automation"):
        with st.spinner("Processing emails..."):
            automation_app.run(emails_to_send=emails_to_send, send_directly=(
                email_action == "Send emails directly"))
        st.success("Email automation process completed!")
        st.experimental_rerun()

    # Section for reviewing unsent emails
    st.subheader("Emails Needing Review")
    if email_action == "Save emails for review":
        contacts = supabase_client.fetch_unsent_emails()

        if not contacts:
            st.info("No emails needing review.")
        else:
            for contact in contacts:
                email = contact["email"]
                linkedin_url = contact.get("linkedin_url", None)
                generated_content = contact.get(
                    "generated_content", "No content available")
                contact_id = contact["id"]
                subject = contact.get("subject", "Quick question!")
                name = contact.get("first_name")

                modal = Modal(
                    title=f"Edit Email for {name}", key=f"edit_modal_{contact_id}")

                with st.expander(f"Email for {name} ({email})"):
                    st.write(f"### Subject: {subject}")
                    st.markdown(
                        f"<div>{generated_content}</div>", unsafe_allow_html=True)
                 
                    # Example part inside your contacts handling loop
                    if linkedin_url:
                        # Use a button to trigger database update and redirect via Markdown
                        if st.button(f"Open LinkedIn Profile for {name}", key=f"linkedin_button_{contact_id}"):
                            # Update the database field before opening the URL
                            supabase_client.client.table("leads").update({
                                "linkedin_clicked": datetime.now().isoformat()  # Update timestamp
                            }).eq("id", contact_id).execute()

                            # Create a clickable link that opens in a new tab
                            js_code = f"window.open('{linkedin_url}', '_blank')"
                            st.components.v1.html(f"<script>{js_code}</script>", height=0)
                    # Edit Email Modal
                    if st.button(f"Edit Email", key=f"open_modal_{contact_id}"):
                        modal.open()

                    if modal.is_open():
                        with modal.container():
                            updated_content = st.text_area(
                                "Edit the email content below:", value=generated_content, height=300)
                            if st.button(f"Save Changes", key=f"save_modal_{contact_id}"):
                                supabase_client.update_generated_content(
                                    contact_id, updated_content)
                                modal.close()

                    # Send Email Button
                    if st.button(f"Send Email to {email}", key=f"send_{contact_id}"):
                        access_token = gmail_client.get_access_token()
                        if access_token:
                            service = gmail_client.build_service(access_token)
                            signature = """
                                <div>
                                    Luuk Alleman<br>
                                    <i>AI Developer | Founder at Everyman AI</i><br>
                                    🌐 <a href="https://www.everyman.ai">www.everyman.ai</a><br>
                                    📄 <a href="https://www.everyman.ai/luuk">You are probably wondering who I am, here's everything you need to know about me.</a><br>
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
                            email_body = f"<p>{generated_content}{signature}</p>"
                            response = gmail_client.send_email(
                            service, "hi@everyman.ai", email, subject, email_body)
                            st.success(
                                f"Email successfully sent to {email}")
                            supabase_client.update_sent_status(contact_id)
                            st.experimental_rerun()  # Refresh the page after sending an email

                    # Delete Email Button
                    if st.button(f"Delete Email for {name}", key=f"delete_{contact_id}"):
                        try:
                            supabase_client.client.table("leads").update({
                                "generated_content": None,
                                "language": None,
                                "subject": None
                            }).eq("id", contact_id).execute()
                            st.success(f"Email data deleted for {name}.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(
                                f"Error deleting email data for {name}: {e}")


def contact_fetching_tab():
    st.title("Contact Fetching Dashboard")

    # Initialize Apollo Contact Manager
    manager = ApolloContactManager()

    # Define user inputs for the payload
    st.subheader("Adjust Filtering Criteria")
    titles = st.multiselect(
        "Select Person Titles",
        options=[
            "Manager", "Project Manager", "Founder", "Owner", "CEO", "Director", "Product Owner",
            "Marketing Manager", "Sales Manager", "Operations Manager", "Research Analyst",
            "Business Development Manager", "Account Manager", "Sales Development Representative",
            "Software Engineer", "Data Scientist", "Product Manager", "Chief Technology Officer",
            "Chief Operating Officer", "Chief Financial Officer", "General Manager", "Consultant",
            "Program Manager", "Team Lead", "Innovation Manager", "Creative Director",
            "Digital Marketing Manager", "Content Strategist", "Customer Success Manager",
            "Technical Lead", "HR Manager", "UX Designer", "Legal Counsel", "IT Manager",
            "Finance Manager", "Strategy Consultant", "Procurement Manager", "Supply Chain Manager",
            "Operations Analyst", "Marketing Specialist"
        ],
        default=["Manager", "Founder", "CEO", "Director", "Project Manager"]
    )

    locations = st.text_input(
        "Enter Locations (comma-separated)",
        value="Netherlands"
    ).split(",")

    email_status = st.selectbox(
        "Email Verification Status",
        options=["verified", "unverified", "likely to engage", "unavailable"],
        index=0
    )

    employee_ranges = st.multiselect(
        "Select Employee Ranges",
        options=["1,10", "11,20", "21,50", "51,100", "101,250", "251,9999"],
        default=["1,10", "11,20"]
    )
    start_page = st.number_input(
        "Specify the Starting Page for Contact Search",
        min_value=1,
        max_value=1000,  # Adjust based on your API limits
        value=50,  # Default starting page
        step=1,
        help="The starting page affects lead quality and contact frequency. Lower pages have more popular leads who might get contacted more often, while higher pages have less contacted leads."
    )
    max_contacts = st.number_input(
        "Max Number of Contacts to Fetch",
        min_value=1, max_value=500, value=10, step=1
    )

    # Preview the payload
    st.subheader("Payload Preview")
    payload_preview = {
        "person_titles": titles,
        "person_locations": [loc.strip() for loc in locations if loc.strip()],
        "contact_email_status": email_status,
        "organization_num_employees_ranges": employee_ranges,
        "per_page": min(25, max_contacts),
        "page": start_page  # Always start from the first page in this example
    }
    st.json(payload_preview)

    # Fetch and display contacts
    if st.button("Fetch Contacts"):
        contacts = manager.run(max_contacts=max_contacts,
                               start_page=start_page, payload=payload_preview)
        if contacts:
            st.success(f"Fetched {len(contacts)} contacts.")
            st.dataframe(contacts)
        else:
            st.warning("No contacts found with the specified criteria.")


# Add the new tab to Streamlit
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio(
    "Choose a tab", ["Dashboard", "Run LeadMachine", "Contact Fetching", "Log Responses"])

if selected_tab == "Dashboard":
    dashboard_tab()
elif selected_tab == "Run LeadMachine":
    email_automation_and_sending_tab()
elif selected_tab == "Contact Fetching":
    contact_fetching_tab()
elif selected_tab == "Log Responses":
    log_responses_tab()
