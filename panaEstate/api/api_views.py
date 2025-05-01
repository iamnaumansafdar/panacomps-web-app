from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from panaEstate.models import Metrics, PDFRawData, Folios, Building
from panaEstate.api.api_serializers import MetricsSerializer, PDFRawDataSerializer, FullBuildingSerializer
from rest_framework.permissions import IsAuthenticated


#API to retrieve metrics data by folio ID
class MetricsByFolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, folio_id):
        metrics = Metrics.objects.filter(folio__folio=folio_id)
        if not metrics:
            return Response({"error": "Metrics not found for the given folio ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MetricsSerializer(metrics, many=True)
        return Response(serializer.data)



# API to retrieve metrics data by building ID
class MetricsByBuildingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, building_id):
        metrics = Metrics.objects.filter(building_id=building_id)
        if not metrics.exists():
            return Response({"error": "Metrics not found for the given building ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MetricsSerializer(metrics, many=True)
        return Response(serializer.data)


#API to retrieve PDF data by folio ID
class PDFsByFolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, folio_id):
        pdfs = PDFRawData.objects.filter(folio__folio=folio_id)
        if not pdfs.exists():
            return Response({"error": "PDFs not found for the given folio ID"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PDFRawDataSerializer(pdfs, many=True)
        return Response(serializer.data)



#API to retrieve building data by building ID
class BuildingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, building_id):
        try:
            building = Building.objects.get(id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FullBuildingSerializer(building)
        return Response(serializer.data)