from django.urls import path
from .views import ViewLiensDetailPanaComps, ViewForclosurersDetailPanaComps

urlpatterns = [
    path("view-lien-ajax/", ViewLiensDetailPanaComps.as_view(), name="view-lien-ajax"),
    path("view-forclosures-ajax/", ViewForclosurersDetailPanaComps.as_view(), name="view-forclosures-ajax"),
    # path('gravamenes/<uuid:building_guid>/', GravamenesView.as_view(), name='view_gravamenes'),
    # path('remate/<uuid:building_guid>/', RemateView.as_view(), name='view_remate'),
]
