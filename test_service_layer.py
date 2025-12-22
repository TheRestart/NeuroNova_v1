
import os
import django
import sys

# Django 설정 로드
sys.path.append(r"d:\1222\NeuroNova_v1\NeuroNova_02_back_end\01_django_server")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cdss_backend.settings")
django.setup()

from emr.services import PatientService, OrderService
from emr.models import PatientCache, Order

def test_patient_creation():
    print("\n[Test] Patient Creation")
    data = {
        "family_name": "Test",
        "given_name": "User",
        "birth_date": "1990-01-01",
        "gender": "male",
        "phone": "010-1234-5678",
        "email": "test@example.com",
        "address": "Seoul",
        "blood_type": "A+"
    }
    
    try:
        patient = PatientService.create_patient(data)
        print(f"Success! Created patient: {patient.patient_id} ({patient.full_name})")
        return patient
    except Exception as e:
        print(f"Failed: {e}")
        return None

def test_order_creation(patient):
    if not patient:
        print("Skipping order test (no patient)")
        return

    print("\n[Test] Order Creation")
    order_data = {
        "patient": patient,
        "ordered_by": "Doctor Strange",
        "order_type": "medication",
        "urgency": "routine",
        "status": "ordered",
        "notes": "Take with water"
    }
    
    items_data = [
        {
            "drug_code": "ASP001",
            "drug_name": "Aspirin",
            "dosage": "100mg",
            "frequency": "QD",
            "duration": "3 days",
            "route": "PO",
            "instructions": "After meal"
        },
        {
            "drug_code": "TYL002",
            "drug_name": "Tylenol",
            "dosage": "500mg",
            "frequency": "PRN",
            "duration": "1 days",
            "route": "PO",
            "instructions": "For pain"
        }
    ]
    
    try:
        order = OrderService.create_order(order_data, items_data)
        print(f"Success! Created order: {order.order_id}")
        for item in order.items.all():
            print(f"  - Item: {item.item_id} ({item.drug_name})")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    print("Staritng Service Layer Test...")
    new_patient = test_patient_creation()
    test_order_creation(new_patient)
