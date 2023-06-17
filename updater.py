import os
import requests

os.remove("main.py")
os.system("wget http://localhost:9000/main.py")

n_version = requests.get("http://localhost:8000/new_version").json()['latest_version']
with open("version.txt", "w") as v_file:
	v_file.write(n_version)

os.system("python3 main.py")