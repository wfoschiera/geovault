import json

from django import forms
from django.contrib.gis.geos import GEOSGeometry

from core.models import User

from .models import ProcessedData, RawFile


class RawFileUploadForm(forms.ModelForm):
    class Meta:
        model = RawFile
        fields = ["name", "file", "file_type", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ProcessedDataForm(forms.ModelForm):
    geometry_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    farmers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(user_type="FARMER"), widget=forms.CheckboxSelectMultiple(), required=False
    )

    class Meta:
        model = ProcessedData
        fields = ["name", "description", "geometry_data", "properties", "farmers"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "properties": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter farmers based on technician relationships
        if kwargs.get("instance"):
            technician = kwargs["instance"].processed_by
            self.fields["farmers"].queryset = User.objects.filter(
                technicians__technician=technician, user_type="FARMER"
            )

    def clean_geometry_data(self):
        data = self.cleaned_data["geometry_data"]
        if data:
            return GEOSGeometry(data)

        return None

    def clean_properties(self):
        data = self.cleaned_data["properties"]
        if isinstance(data, str):
            try:
                return json.loads(data)
            except forms.ValidationError:
                raise forms.ValidationError("Invalid JSON data for properties")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.geometry = self.cleaned_data["geometry_data"]
        if commit:
            instance.save()
            self.save_m2m()
        return instance
