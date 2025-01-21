import os
import subprocess

# Paths
UPDATER_SCRIPT = "./updater.exe"
APP_MAIN_SCRIPT = "./LyricVerse.exe"

# Run updater
print("Starting updater...")
updater_process = subprocess.run([UPDATER_SCRIPT])
if updater_process.returncode != 0:
    print("Updater encountered an error. Running the existing app.")

# Run the app
print("Starting main application...")
os.chdir("./LyricVerse")
subprocess.run([APP_MAIN_SCRIPT])