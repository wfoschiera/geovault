import json

from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Q
from rolepermissions.checkers import has_role

from core.models import User
from geovault.roles import Farmer, FarmerAdmin, Technician

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


class RawFileProcessingForm(forms.Form):  # Changed from ModelForm to Form
    operation_choices = [
        ("simplify", "Simplify Geometry"),
        ("buffer", "Buffer Features"),
        ("reproject", "Reproject Data"),
        ("extract", "Extract Properties"),
    ]

    raw_file = forms.ModelChoiceField(
        queryset=RawFile.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Select Raw File to Process",
    )

    operation = forms.ChoiceField(
        choices=operation_choices, widget=forms.RadioSelect(), label="Select Processing Operation"
    )

    operation_param = forms.FloatField(
        required=False,
        label="Operation Parameter",
        help_text="Parameter value for the selected operation (e.g., buffer distance, simplification tolerance)",
    )

    name = forms.CharField(max_length=255, label="Output Name")
    description = forms.CharField(  # Changed from TextField to CharField
        required=False, widget=forms.Textarea(attrs={"rows": 4})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            if has_role(user, Technician):
                # Get farmers related to this technician
                related_farmers = User.objects.filter(technicians__technician=user)
                # Get all raw files from related farmers and files uploaded by the technician
                self.fields["raw_file"].queryset = RawFile.objects.filter(
                    Q(uploaded_by__in=related_farmers) | Q(uploaded_by=user)
                )
            else:
                # If a farmer, only show their files
                self.fields["raw_file"].queryset = RawFile.objects.filter(uploaded_by=user)
