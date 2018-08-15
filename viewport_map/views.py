import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from google_auth.decorators import auth_required

from .forms import LocationForm
from .fusiontables import LocationTable
from .models import Location


class Main(View):

    @method_decorator(auth_required)
    def get(self, request):
        return render(request, 'viewport_map/main.html')


class Locations(View):

    @method_decorator(auth_required)
    def get(self, request):
        locations = Location.objects.all()
        data = []
        for location in locations:
            data.append({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address})
        return JsonResponse({'locations': data})

    @transaction.atomic
    @method_decorator(auth_required)
    def post(self, request):
        """Saves a location into local database and fusiontable service."""
        location_table = LocationTable.build_service(request)
        try:
            post_data = json.loads(request.body)
        except (ValueError, TypeError):
            post_data = None

        form = LocationForm(post_data)
        if form.is_valid():
            location = form.save()
            location_table.save(location)
            data = {
                'location': {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                }
            }
            status = 200
        else:
            data = form.errors
            status = 400

        return JsonResponse(data, status=status)


class ClearLocations(View):

    @transaction.atomic
    @method_decorator(auth_required)
    def delete(self, request):
        """Clear data from local table and fusiontable service."""
        location_table = LocationTable.build_service(request)
        Location.objects.all().delete()
        location_table.clear()
        return JsonResponse({}, status=202)
