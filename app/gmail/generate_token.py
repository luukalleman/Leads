import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:58565/"
TOKEN_URL = "https://oauth2.googleapis.com/token"

app = Flask(__name__)
def save_to_env_file(key, value):
    """
    Save a key-value pair to the .env file.
    """
    try:
        # Check if the .env file already contains the key
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, "r") as file:
                lines = file.readlines()
            # If the key exists, update its value
            with open(env_path, "w") as file:
                key_found = False
                for line in lines:
                    if line.startswith(f"{key}="):
                        file.write(f"{key}={value}\n")
                        key_found = True
                    else:
                        file.write(line)
                # If the key was not found, add it to the file
                if not key_found:
                    file.write(f"{key}={value}\n")
        else:
            # If the .env file does not exist, create it
            with open(env_path, "w") as file:
                file.write(f"{key}={value}\n")
    except Exception as e:
        print(f"Error saving {key} to .env: {e}")
        
@app.route("/")
def index():
    code = request.args.get("code")
    if not code:
        return "No authorization code provided."
    # Exchange code for tokens
    payload = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(TOKEN_URL, data=payload)

    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")

        if refresh_token:
            save_to_env_file("GMAIL_REFRESH_TOKEN", refresh_token)
            return f"Refresh token saved to .env: {refresh_token}"


        return f"Access Token: {access_token}"

    return f"Failed to retrieve tokens: {response.json()}"

if __name__ == "__main__":
    print(f"Please visit this URL to authorize this application:")
    print(
        f"https://accounts.google.com/o/oauth2/auth?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=https://www.googleapis.com/auth/gmail.send+https://www.googleapis.com/auth/gmail.readonly"  # Modified this line
        f"&access_type=offline"
    )
    app.run(port=58565)