"""
EMR URLs
"""
from django.urls import path
from . import views

app_name = 'emr'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # OpenEMR Proxy endpoints (인증은 Django에서 처리)
    path('patients/search/', views.search_patients, name='search_patients'),
    path('patients/<str:patient_id>/', views.get_patient_detail, name='patient_detail'),
    path('patients/<str:patient_id>/encounters/', views.get_patient_encounters, name='patient_encounters'),
    path('patients/<str:patient_id>/vitals/', views.get_patient_vitals, name='patient_vitals'),

    # Cached data endpoints
    path('cached/patients/', views.list_cached_patients, name='cached_patients'),
    path('cached/encounters/', views.list_cached_encounters, name='cached_encounters'),
]
