from urllib.parse import urlparse
from datetime import datetime, timedelta
import pytz
import logging
from dotenv import load_dotenv
from apify_client import ApifyClient
from openai import OpenAI
from pydantic import BaseModel
from app.linkedin.cookies import linkedin_cookies
from app.ai.prompts import get_analysis_prompt, get_language_prompt
import os
# Load environment variables from .env
load_dotenv()
# Clear existing environment variables for debugging
os.environ.pop("APIFY_TOKEN", None)

# Reload .env
load_dotenv(".env")
print("APIFY_TOKEN:", os.getenv("APIFY_TOKEN"))

def extract_username_from_url(linkedin_url):
    """
    Extracts the username from a LinkedIn URL.

    Args:
        linkedin_url (str): LinkedIn profile or post URL.

    Returns:
        str: Extracted username, or None if not found.
    """
    parsed_url = urlparse(linkedin_url)
    path_parts = parsed_url.path.strip("/").split("/")

    # Profile URL example: /in/liam-geschwindt-02b88b168/
    # Post URL example: /posts/liam-geschwindt-02b88b168_slush-slush2024-...
    if path_parts:
        if path_parts[0] == "in":
            return path_parts[1]  # Username from profile URL
        elif path_parts[0] == "posts":
            # Username from post URL before the first underscore
            return path_parts[1].split("_")[0]

    return None


def is_valid_repost(post_url, linkedin_profile_url):
    """
    Checks if a LinkedIn post is a repost based on URL comparison.

    Args:
        post_url (str): The LinkedIn post URL.
        linkedin_profile_url (str): The LinkedIn profile URL.

    Returns:
        bool: False if the post matches the profile URL, True if it’s a repost.
    """
    post_username = extract_username_from_url(post_url)
    profile_username = extract_username_from_url(linkedin_profile_url)

    return post_username != profile_username


def is_recent_post(posted_at_iso, months=6):
    """
    Checks if a post is within the last specified number of months.

    Args:
        posted_at_iso (str): The ISO timestamp of when the post was created.
        months (int): The number of months to consider as recent.

    Returns:
        bool: True if the post is recent, False otherwise.
    """
    # Convert the ISO timestamp to a timezone-aware datetime object
    posted_date = datetime.fromisoformat(posted_at_iso.replace("Z", "+00:00"))

    # Make the current datetime timezone-aware (UTC)
    current_time = datetime.now(pytz.utc)

    # Calculate the date three months ago
    three_months_ago = current_time - timedelta(days=months * 30)

    return posted_date >= three_months_ago



class Response(BaseModel):
    fact: str
    useable: bool
    category: str


class Language(BaseModel):
    language_spoken: str


class LinkedInScraper:
    """
    A class to scrape LinkedIn posts and generate personalized email content.
    """

    def __init__(self, api_key, apify_token):
        self.client = OpenAI(api_key=api_key)
        self.apify_client = ApifyClient(apify_token)
        self.apify_token = apify_token
    def scrape_linkedin_posts(self, linkedin_url):
        """
        Scrapes LinkedIn profile posts using Apify and filters them by date.

        Args:
            linkedin_url (str): The LinkedIn profile URL.

        Returns:
            list: A list of recent posts.
        """
        run_input = {
            "urls": [linkedin_url],
            "minDelay": 2,
            "maxDelay": 8,
            "proxy": {"useApifyProxy": True, "apifyProxyCountry": "US"},
            "cookie": linkedin_cookies,
            "limitPerSource": 5,
        }
        try:
            run = self.apify_client.actor(
                "curious_coder~linkedin-post-search-scraper").call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")
            print(self.apify_token)
            if dataset_id:
                posts = []
                for item in self.apify_client.dataset(dataset_id).iterate_items():
                    post_url = item.get("url", "")
                    post_text = item.get("text", "").strip()
                    posted_at_iso = item.get("postedAtISO")
                    is_repost = is_valid_repost(post_url, linkedin_url)
                    is_recent = is_recent_post(posted_at_iso)
                    # Filter posts by date
                    if post_text and is_recent and not is_repost:
                        print(f"Appending recent post: {post_url}")
                        posts.append(post_text)
                    else:
                        print(f"Skipping old post: {post_url}")

                return posts if posts else False

        except Exception as e:
            print(f"Error during LinkedIn post scraping: {e}")
            return None

    def generate_first_line(self, posts, name):
        """
        Generates a first-line email opener using OpenAI API.

        Args:
            posts (list): A list of LinkedIn posts.

        Returns:
            tuple: The first-line email opener, usability status, and detected language.
        """
        try:
            if not posts or all(post.strip() == "" for post in posts):
                return "I came across your LinkedIn profile and thought it would be great to connect!", False, "EN"

            # Detect language
            language_prompt = get_language_prompt(posts, name)
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an assistant analyzing LinkedIn activity and someones name to detect whether the language spoken by this person is only EN or it could also be NL."},
                    {"role": "user", "content": language_prompt}
                ],
                response_format=Language,
            )
            result = completion.choices[0].message.parsed
            language = result.language_spoken

            # Generate the first-line prompt
            analysis_prompt, sys_message = get_analysis_prompt(posts, language)
 
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sys_message},
                    {"role": "user", "content": analysis_prompt},
                ],
                response_format=Response,

            )
            result = completion.choices[0].message.parsed
            first_line = result.fact
            useable = result.useable
            category = result.category
            print(f"Generated the opening line: {first_line}")
            print(f"This post is useable: {useable}")

            if useable:
                return first_line, language, category
            else:
                return None,language, None

        except Exception as e:
            print(f"Error generating first line: {e}")
            return "It was great to come across your LinkedIn profile!", False, "EN"
