import json

from django import forms
from django.contrib.gis.geos import GEOSGeometry
from rolepermissions.checkers import has_role

from core.models import User
from geovault.roles import Farmer, FarmerAdmin

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
    farmers = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = ProcessedData
        fields = ["name", "description", "geometry_data", "properties", "farmers"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "properties": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = User.objects.all()
        farmers = [user for user in users if has_role(user, Farmer) or has_role(user, FarmerAdmin)]
        farmer_queryset = User.objects.filter(pk__in=[user.pk for user in farmers])

        # Set the queryset
        self.fields["farmers"].queryset = farmer_queryset

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
