import os
import requests
import zipfile

# Configuration
SERVER_URL = "http://localhost:8000/LyricVerse.zip"
VERSION_URL = "http://localhost:8000/version.txt"
DOWNLOAD_PATH = "./LyricVerse.zip"
EXTRACT_PATH = "./LyricVerse"
OLD_APP_PATH = "./LyricVerse"
LOCAL_VERSION_FILE = "./LyricVerse/version.txt"

# Step 1: Check internet connection
def check_internet_connection():
    try:
        requests.get(VERSION_URL, timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Step 2: Check version
def needs_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            server_version = response.text.strip()
            if os.path.exists(LOCAL_VERSION_FILE):
                with open(LOCAL_VERSION_FILE, "r") as file:
                    local_version = file.read().strip()
                return server_version != local_version
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
        for root, dirs, files in os.walk(OLD_APP_PATH, topdown=False):
            for name in files:
                if name != "updater.exe":  # Skip the updater
                    os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(OLD_APP_PATH)
        print("Old version deleted.")

# Step 5: Extract the new version
def extract_new_version():
    print("Extracting new version...")
    with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
        if os.path.exists(EXTRACT_PATH):
            os.rename(EXTRACT_PATH, OLD_APP_PATH)
        zip_ref.extractall(EXTRACT_PATH)
    os.remove(DOWNLOAD_PATH)
    print("Extraction completed.")

# Step 6: Run the app
def run_app():
    app_main_path = os.path.join(EXTRACT_PATH, "main.py")
    if os.path.exists(app_main_path):
        print("Running the app...")
        os.system(f"python {app_main_path}")
    else:
        print("App main file not found. Cannot run the app.")

# Main process
def main():
    if not check_internet_connection():
        print("No internet connection. Running the old version...")
        run_app()
        return

    if needs_update():
        download_new_version()
        delete_old_version()
        extract_new_version()

    run_app()

if __name__ == "__main__":
    main()