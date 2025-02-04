import json
import os # use to check for existence of key 
from cryptography.fernet import Fernet

# Used to save, retrieve and delete the passwords using encryption and file management 
# I used the cryptography.fernet module to encrypt the passwords before saving them 
# Also reads n writes to passwords.json 

PASSWORD_FILE = "passwords.json"
# encryption key 
KEY_FILE = "key.key"

# Generate or load encryption key if it DNE 
# loads from key.key 
def load_or_create_key():
    if not os.path.exists(KEY_FILE):
        # if DNE, it generates a new key 
        key = Fernet.generate_key()
        # need to use wb since encrypted
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else: # if it already exists, just read from key.key 
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

# Load encryption key
key = load_or_create_key()
cipher = Fernet(key)

# encrypts and saves password to json file 
def save_password(service, username, password):
    try:
        with open(PASSWORD_FILE, "r") as file:
            passwords = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        passwords = {}

    encrypted_password = cipher.encrypt(password.encode()).decode()  # Encrypt the password

    # add the password 
    passwords[service] = {"username": username, "password": encrypted_password}

    # save updated passwords bck to file 
    with open(PASSWORD_FILE, "w") as file:
        json.dump(passwords, file, indent=4)

    print("Password saved successfully.")

# to retrieve and decrypt the password 
def get_password(service):
    try:
        with open(PASSWORD_FILE, "r") as file:
            passwords = json.load(file) # load the passwords stored 

        if service in passwords: # if it exists just decrypt 
            username = passwords[service]["username"]
            encrypted_password = passwords[service]["password"]

            # Decrypt the password
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()

            print(f"Service: {service}")
            print(f"Username: {username}")
            print(f"Password: {decrypted_password}")

            return {"username": username, "password": decrypted_password}

        else:
            print("Service not found.")
            return None
        
    except (FileNotFoundError, json.JSONDecodeError):
        print("No saved passwords found.")
        return None
    
   # except Exception as e:
     #   print(f"Error retrieving password: {e}")
       # return None

# to delete exisiting password 
def delete_password(service):
    try:
        with open(PASSWORD_FILE, "r") as file:
            passwords = json.load(file)

        if service in passwords: # if found in list
            del passwords[service] # deleteee 

            with open(PASSWORD_FILE, "w") as file:
                # save updated password back to file 
                # .dump(object, file,..)
                json.dump(passwords, file, indent=4)
            print("Password deleted successfully.")
        else:
            print("Service not found.")
    # to catch errors since we using try 
    except (FileNotFoundError, json.JSONDecodeError):
        print("No saved passwords found.")

# to list all the stored passwords aka the services 
def get_all_services():
    try:
        with open("passwords.json", "r") as file:
            data = json.load(file)
            return list(data.keys())  # Get service names
    except (FileNotFoundError, json.JSONDecodeError):
        return []

