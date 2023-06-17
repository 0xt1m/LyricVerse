from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import os

def get_latest_version():
	latest_version = open("new_version/version.txt", "r").read()
	return latest_version

def index(request):
	return render(request, "version_checker/index.html")
	# return HttpResponse("Hello, world. You're at the version_checker index.")


def app_info(request):
	data = {
		'latest_version': get_latest_version(),
		'author': "Tymofii Matviiv",
	}
	return JsonResponse(data)

def new_version(request):
	data = {
		'latest_version': get_latest_version(),
	}
	return JsonResponse(data)

def download(request):
	filename = "version.txt"
	file_location = f"{filename}"
	try:    
		with open(file_location, 'r') as f:
		   file_data = f.read()

		response = HttpResponse(file_data)
		response['Content-Disposition'] = f"attachment; filename={filename}"

	except IOError:
		response = HttpResponseNotFound('<h1>File not exist</h1>')

	return response
