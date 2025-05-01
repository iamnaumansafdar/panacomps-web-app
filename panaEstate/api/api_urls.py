from django.urls import path
from .api_views import MetricsByFolioView, MetricsByBuildingView, PDFsByFolioView, BuildingDetailView

urlpatterns = [
    path('metrics/folio/<int:folio_id>/', MetricsByFolioView.as_view(), name='metrics-by-folio'),
    path('metrics/building/<int:building_id>/', MetricsByBuildingView.as_view(), name='metrics-by-building'),
    path('pdfs/folio/<int:folio_id>/', PDFsByFolioView.as_view(), name='pdfs-by-folio'),
    path('building/<int:building_id>/', BuildingDetailView.as_view(), name='building-detail'),
]
