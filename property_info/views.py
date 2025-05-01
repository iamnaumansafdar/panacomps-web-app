from django.views.generic import ListView
from .models import Gravamen, Remate
from django.views.generic import View
from django.http import JsonResponse
from .utils import PropertyInfoData




class ViewLiensDetailPanaComps(View):
    def get(self, request):
        folio = request.GET.get("folio")
        selectedBuilding = request.GET.get('selectedBuilding')
        print(selectedBuilding, 'selectedBuilding')
        data = PropertyInfoData.get_view_liens_detial_data(folio, selectedBuilding)
        return JsonResponse(data)



class ViewForclosurersDetailPanaComps(View):
    def get(self, request):
        folio = request.GET.get("folio")
        selectedBuilding = request.GET.get('selectedBuilding')
        print(selectedBuilding, 'selectedBuilding')
        data = PropertyInfoData.get_view_forclosure_detial_data(selectedBuilding)
        return JsonResponse(data)