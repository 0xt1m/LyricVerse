from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("app_info", views.app_info, name="app_info"),
    path("new_version", views.new_version, name="new_version"),
    path("new_version/download", views.download, name="download")
]