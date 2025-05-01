from django.urls import path
from .views import (
    PanacompsDashboardView,
    ViewDetailPanaComps,
    ViewHistoyDetailPanaComps,
    CheckHistoryView,
    DownloadPDFRawDataCSV,
    UpdatePanacompsDashboardView,
    ResetPanacompsDashboardView,
    DownloadPenaCompsCSV,
    FilterPDFDataView,
    filter_units_and_folios,
    filter_folios_number,
    filter_region_view,
    DownloadSearchResultCSVView,
    DownloadDetailResultExcelView,
)


urlpatterns = [
    path("", PanacompsDashboardView.as_view(), name="home"),
    path('filter-units-folios/', filter_units_and_folios, name='filter_units_folios'), 
    
    path('filter-region-view/', filter_region_view, name='filter-region-view'), 
    path('filter-folios-number/', filter_folios_number, name='filter_folios-number'), 
    path("view-detail-ajax/", ViewDetailPanaComps.as_view(), name="view_detail_ajax"),
    path("view-histoy-detail-ajax/", ViewHistoyDetailPanaComps.as_view(), name="view-histoy-detail-ajax"),
    path('check-history/', CheckHistoryView.as_view(), name='check-history-ajax'),
    path("download-csv/", DownloadPDFRawDataCSV.as_view(), name="download_csv"),
    path(
        "update-panaComs-dashboard/",
        UpdatePanacompsDashboardView.as_view(),
        name="update_panaComs_dashboard",
    ),
    path(
        "Reset-all-data/",
        ResetPanacompsDashboardView.as_view(),
        name="Reset-all-data",
    ),
    path(
        "download-comps-csv/", DownloadPenaCompsCSV.as_view(), name="download_comps_csv"
    ),
    path("filter-pdf-data/", FilterPDFDataView.as_view(), name="filter_pdf_data"),

    path('search-result-csv/', DownloadSearchResultCSVView.as_view(), name='search-result-csv'),
    path('download-detial-result-excel/',  DownloadDetailResultExcelView.as_view(), name='download-detial-result-excel'),

    
]
