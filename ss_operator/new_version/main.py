import os
import threading
import requests
import urllib.request

def internet_on():
	try:
		urllib.request.urlopen('https://8.8.8.8', timeout=1)
		return True
	except urllib.request.URLError as err: 
		return False

def run_updater():
	os.system("python3 updater.py")

c_version = open("version.txt", "r").read()
if internet_on():
	n_version = requests.get("http://localhost:8000/new_version").json()['latest_version']
	print(f"New version: {n_version}")
	if c_version != n_version:
		t = threading.Thread(target=run_updater)
		t.start()
		quit()
else:
	print("[-] There is no connection to the internet!")
	
print(f"Current version: {c_version}")
print("\n###############################\n")

print("Hello world!!!")
while True:
	expression = input("Enter an expression: ")
	if expression == "stop":
		break
	print(eval(expression))