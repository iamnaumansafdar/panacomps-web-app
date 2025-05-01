from django.urls import path
from .views import ContactSupportView, ai_analysis
from django.views.generic import TemplateView

urlpatterns = [
    path('contact-support/', ContactSupportView.as_view(), name='contact_support'),
    path('support-confirmation/', TemplateView.as_view(template_name='support/confirmation.html'), name='support_confirmation'),
    path('ai-analysis/<int:template_id>/', ai_analysis, name='ai_analysis'),
]
