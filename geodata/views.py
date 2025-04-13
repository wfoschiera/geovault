from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rolepermissions.checkers import has_role

from core.models import TechnicianFarmerRelationship, User
from geovault.roles import Farmer, Technician

from .forms import ProcessedDataForm, RawFileUploadForm
from .models import ProcessedData, RawFile


@login_required
def dashboard(request):
    if has_role(request.user, Farmer):
        raw_files = RawFile.objects.filter(uploaded_by=request.user)
        processed_data = ProcessedData.objects.filter(farmers=request.user)
        return render(
            request, "geodata/farmer_dashboard.html", {"raw_files": raw_files, "processed_data": processed_data}
        )

    elif has_role(request.user, Technician):
        # Get all farmers related to this technician
        related_farmers = User.objects.filter(technicians__technician=request.user)

        # Get all raw files from related farmers and files uploaded by the technician
        raw_files = RawFile.objects.filter(Q(uploaded_by__in=related_farmers) | Q(uploaded_by=request.user))

        processed_data = ProcessedData.objects.filter(processed_by=request.user)

        return render(
            request,
            "geodata/technician_dashboard.html",
            {"raw_files": raw_files, "processed_data": processed_data, "related_farmers": related_farmers},
        )

    return redirect("home")


@login_required
def upload_file(request):
    if request.method == "POST":
        form = RawFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            raw_file = form.save(commit=False)
            raw_file.uploaded_by = request.user
            raw_file.save()
            messages.success(request, "File uploaded successfully.")
            return redirect("dashboard")
    else:
        form = RawFileUploadForm()

    return render(request, "geodata/upload_file.html", {"form": form})


@login_required
def process_file(request, file_id):
    if has_role(request.user, Technician):
        raise PermissionDenied

    raw_file = get_object_or_404(RawFile, id=file_id)

    # Check if the technician is related to the farmer who uploaded the file
    if has_role(raw_file.uploaded_by, Farmer):
        if not TechnicianFarmerRelationship.objects.filter(
            technician=request.user, farmer=raw_file.uploaded_by
        ).exists():
            raise PermissionDenied

    if request.method == "POST":
        form = ProcessedDataForm(request.POST)
        if form.is_valid():
            processed_data = form.save(commit=False)
            processed_data.processed_by = request.user
            processed_data.raw_file = raw_file
            processed_data.save()

            # Add related farmers
            form.save_m2m()  # Necessary for many-to-many fields when using commit=False

            messages.success(request, "Data processed successfully.")
            return redirect("dashboard")
    else:
        form = ProcessedDataForm()

    return render(request, "geodata/process_file.html", {"form": form, "raw_file": raw_file})


@login_required
def download_processed_data(request, data_id):
    processed_data = get_object_or_404(ProcessedData, id=data_id)

    # Check permissions
    if has_role(request.user, Farmer):
        if request.user not in processed_data.farmers.all():
            raise PermissionDenied
    elif has_role(request.user, Technician):
        if processed_data.processed_by != request.user:
            raise PermissionDenied

    # Generate GeoJSON from processed data
    geojson = {
        "type": "Feature",
        "geometry": processed_data.geometry.json if processed_data.geometry else None,
        "properties": processed_data.properties,
    }

    response = JsonResponse(geojson)
    response["Content-Disposition"] = f'attachment; filename="{processed_data.name}.geojson"'
    return response


@login_required
def view_data(request, data_id):
    processed_data = get_object_or_404(ProcessedData, id=data_id)

    # Check permissions
    if has_role(request.user, Farmer):
        if request.user not in processed_data.farmers.all():
            raise PermissionDenied

    return render(request, "geodata/view_data.html", {"data": processed_data})
