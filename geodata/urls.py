from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_file, name="upload_file"),
    path("process/<int:file_id>/", views.process_file, name="process_file"),
    path("download/<int:data_id>/", views.download_processed_data, name="download_data"),
    path("view/<int:data_id>/", views.view_data, name="view_data"),
]
