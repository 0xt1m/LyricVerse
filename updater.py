import os
import requests

# Configuration
SERVER_URL = "http://18.223.188.46:8484/LyricVerse.exe"
VERSION_URL = "http://18.223.188.46:8484/version.txt"
DOWNLOAD_PATH = "./LyricVerse.exe"
OLD_APP_PATH = "./LyricVerse/LyricVerse.exe"
LOCAL_VERSION_FILE = "./LyricVerse/version.txt"

server_version = "0.0"

# Step 1: Check internet connection
def check_internet_connection():
    try:
        requests.get(VERSION_URL, timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Step 2: Check version
def needs_update():
    global server_version

    try:
        response = requests.get(VERSION_URL, timeout=2)
        if response.status_code == 200:
            server_version = float(response.text.strip())
            if os.path.exists(LOCAL_VERSION_FILE):
                with open(LOCAL_VERSION_FILE, "r") as file:
                    local_version = float(file.read().strip())
                return server_version > local_version
            else:
                return True
        else:
            print("Failed to fetch version info. Status code:", response.status_code)
            return False
    except requests.RequestException as e:
        print("Error checking version:", e)
        return False

# Step 3: Download the new version
def download_new_version():
    print("Downloading new version...")
    response = requests.get(SERVER_URL, stream=True)
    if response.status_code == 200:
        with open(DOWNLOAD_PATH, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print("Download completed.")
    else:
        print("Failed to download the app. Status code:", response.status_code)
        exit(1)

# Step 4: Delete the old version
def delete_old_version():
    if os.path.exists(OLD_APP_PATH):
        print("Deleting old version...")
        os.remove(OLD_APP_PATH)
        print("Old version deleted.")

# Step 5: Extract the new version
def extract_new_version():
    print("Extracting new version...")
    os.rename(DOWNLOAD_PATH, OLD_APP_PATH)

    with open(LOCAL_VERSION_FILE, "w") as file:
        file.write(str(server_version))

    os.remove(DOWNLOAD_PATH)
    print("Extraction completed.")

# Main process
def main():
    if not check_internet_connection():
        print("No internet connection. Running the old version...")
        return

    try:
        if needs_update():
            download_new_version()
            delete_old_version()
            extract_new_version()
    except:
        pass

if __name__ == "__main__":
    main()