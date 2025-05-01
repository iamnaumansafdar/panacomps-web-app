from rest_framework import serializers
from panaEstate.models import Metrics, Folios, Building, PDFRawData




class FoliosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folios
        fields = ['folio']


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['name']


class MetricsSerializer(serializers.ModelSerializer):
    folio = FoliosSerializer()
    building = BuildingSerializer()
    class Meta:
        model = Metrics
        fields = '__all__'

        
class PDFRawDataSerializer(serializers.ModelSerializer):
    folio = FoliosSerializer()
    class Meta:
        model = PDFRawData
        fields = '__all__'



class FullBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'