import requests
from requests.auth import HTTPBasicAuth
import json
import csv
import time
import os
import getpass
from cryptography.fernet import Fernet
# Jira Cloud URL - update this value to your cloud url
jira_url = "https://opswat.atlassian.net/"

# API endpoint for adding users to a group
api_endpoint = f"{jira_url}/rest/api/3/group/user"

# Authentication credentials - update the email and api_token for your user and token combination
# Function to generate a key and instantiate a Fernet instance
def generate_key():
    return Fernet.generate_key()


# Function to encrypt the token
def encrypt_token(token, key):
    fernet = Fernet(key)
    encrypted_token = fernet.encrypt(token.encode())
    return encrypted_token


# Function to decrypt the token
def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    decrypted_token = fernet.decrypt(encrypted_token).decode()
    return decrypted_token


# Authentication credentials - update the email for your user
email = getpass.getpass("Please input your email: ")

# Store the API token and key in text files
token_file_path = "/Users/luke.le/Downloads/api_token.txt"  # Update this path
key_file_path = "/Users/luke.le/Downloads/key.key"  # Update this path

# Check if the key file exists
if os.path.exists(key_file_path):
    # Read the key from the file
    with open(key_file_path, mode="rb") as key_file:
        key = key_file.read()
    print(f"Encryption key has been read from {key_file_path}.")

    # Check if the token file exists
    if os.path.exists(token_file_path):
        # Read the encrypted token from the file
        with open(token_file_path, mode="rb") as token_file:
            encrypted_token = token_file.read()
        # Decrypt the token
        api_token = decrypt_token(encrypted_token, key)
        print(f"API token has been decrypted from {token_file_path}.")
    else:
        print("Token file does not exist. Please enter a new API token.")
        api_token = getpass.getpass("Please enter your API token: ")
        encrypted_token = encrypt_token(api_token, key)
        with open(token_file_path, mode="wb") as token_file:
            token_file.write(encrypted_token)
        print(f"API token has been encrypted and stored in {token_file_path}.")
else:
    # Generate a new key and prompt the user for the API token
    key = generate_key()
    with open(key_file_path, mode="wb") as key_file:
        key_file.write(key)
    print(f"New encryption key has been generated and stored in {key_file_path}.")

    api_token = getpass.getpass("Please enter your API token: ")
    encrypted_token = encrypt_token(api_token, key)
    with open(token_file_path, mode="wb") as token_file:
        token_file.write(encrypted_token)
    print(f"API token has been encrypted and stored in {token_file_path}.")
# Read the CSV file with user and group IDs
csv_file_path = getpass.getpass("Please enter your CSV path: ")

auth = HTTPBasicAuth(email, api_token)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Process the CSV file
with open(csv_file_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        user_id = row["userid"]  # Change to match your CSV column names
        group_id = row["groupid"]  # Change to match your CSV column names

        # Construct the JSON payload
        payload = json.dumps({"accountId": user_id})

        # Set the query parameters for the group ID
        query = {"groupId": group_id}
        time.sleep(3)
        # Make the API request to add the user to the group
        response = requests.post(
            api_endpoint,
            data=payload,
            headers=headers,
            params=query,
            auth=auth,
        )

        if response.status_code == 201:
            print(f"Added user with ID '{user_id}' to group with ID '{group_id}'.")
        elif response.status_code == 400:
            print(f" user with ID '{user_id}' already existed to group with ID '{group_id}'.")
        else:
            print(
                f"Failed to add user with ID '{user_id}' to group. Status Code: {response.status_code}"
            )