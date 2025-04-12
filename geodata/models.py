import os

from django.contrib.gis.db import models

from core.models import User


class RawFile(models.Model):
    FILE_TYPE_CHOICES = (
        ("SHP", "Shapefile"),
        ("GPKG", "GeoPackage"),
        ("KML", "KML"),
        ("GEOJSON", "GeoJSON"),
        ("CSV", "CSV"),
        ("XLSX", "Excel"),
    )

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="raw_files/")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="raw_files")
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def extension(self):
        return os.path.splitext(self.file.name)[1]


class ProcessedData(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="processed_data")
    raw_file = models.ForeignKey(RawFile, on_delete=models.SET_NULL, null=True, related_name="processed_data")

    # Spatial data field
    geometry = models.GeometryField(srid=4326, null=True, blank=True)

    # Additional properties stored as JSON
    properties = models.JSONField(default=dict, blank=True)

    # Related farmer(s)
    farmers = models.ManyToManyField(User, related_name="related_data", limit_choices_to={"user_type": "FARMER"})

    def __str__(self):
        return self.name
