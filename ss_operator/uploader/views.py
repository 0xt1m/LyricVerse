from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from .forms import UploadFileForm

# Addition Functions
def is_float(string):
	try:
		float(string)
		return True
	except ValueError:
		return False

def handle_the_form(file, version):
	with open(str("new_version/" + str(file)), "wb+") as destination:
		for chunk in file.chunks():
			destination.write(chunk)

	with open("new_version/version.txt", "w") as v_file:
		v_file.write(version)

# Create your views here.
def upload(request):
	# return HttpResponse("Hello, world. You're at the uploader.")
	return render(request, "uploader/upload.html")

def upload_file(request):
	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid() and is_float(request.POST["version"]):
			handle_the_form(request.FILES["file"], request.POST["version"])
			return HttpResponseRedirect("/upload")
	else:
		form = UploadFileForm()
	return render(request, "uploader/upload.html", {"form": form})