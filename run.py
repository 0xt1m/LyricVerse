import os
import subprocess

# Paths
UPDATER_SCRIPT = "./updater.py"
APP_MAIN_SCRIPT = "./LyricVerse/main.py"

# Run updater
print("Starting updater...")
updater_process = subprocess.run(["python", UPDATER_SCRIPT])
if updater_process.returncode != 0:
    print("Updater encountered an error. Running the existing app.")

# Run the app
print("Starting main application...")
subprocess.run(["python", APP_MAIN_SCRIPT])