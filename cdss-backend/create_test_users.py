"""
CDSS 테스트 사용자 생성 스크립트
Week 1 작업: 7개 역할별 테스트 사용자 생성

사용법:
python manage.py shell < create_test_users.py
"""

from acct.models import User, Role

print("=" * 50)
print("CDSS 테스트 사용자 생성 중...")
print("=" * 50)

# 기존 사용자 삭제 (선택사항)
# User.objects.all().delete()

# 1. Admin
admin, created = User.objects.get_or_create(
    username='admin1',
    defaults={
        'email': 'admin@hospital.com',
        'role': Role.ADMIN,
        'employee_id': 'A001',
        'department': 'IT',
        'first_name': '관리자',
        'last_name': '김',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✓ [Admin] {admin.username} 생성 완료")
else:
    print(f"  [Admin] {admin.username} 이미 존재")

# 2. Doctor
doctor, created = User.objects.get_or_create(
    username='doctor1',
    defaults={
        'email': 'doctor@hospital.com',
        'role': Role.DOCTOR,
        'employee_id': 'D001',
        'department': 'Neurosurgery',
        'first_name': '의사',
        'last_name': '이',
    }
)
if created:
    doctor.set_password('doctor123')
    doctor.save()
    print(f"✓ [Doctor] {doctor.username} 생성 완료")
else:
    print(f"  [Doctor] {doctor.username} 이미 존재")

# 3. RIB (방사선과)
rib, created = User.objects.get_or_create(
    username='rib1',
    defaults={
        'email': 'rib@hospital.com',
        'role': Role.RIB,
        'employee_id': 'R001',
        'department': 'Radiology',
        'first_name': '방사선사',
        'last_name': '박',
    }
)
if created:
    rib.set_password('rib123')
    rib.save()
    print(f"✓ [RIB] {rib.username} 생성 완료")
else:
    print(f"  [RIB] {rib.username} 이미 존재")

# 4. Lab (검사실)
lab, created = User.objects.get_or_create(
    username='lab1',
    defaults={
        'email': 'lab@hospital.com',
        'role': Role.LAB,
        'employee_id': 'L001',
        'department': 'Laboratory',
        'first_name': '검사사',
        'last_name': '최',
    }
)
if created:
    lab.set_password('lab123')
    lab.save()
    print(f"✓ [Lab] {lab.username} 생성 완료")
else:
    print(f"  [Lab] {lab.username} 이미 존재")

# 5. Nurse
nurse, created = User.objects.get_or_create(
    username='nurse1',
    defaults={
        'email': 'nurse@hospital.com',
        'role': Role.NURSE,
        'employee_id': 'N001',
        'department': 'Emergency',
        'first_name': '간호사',
        'last_name': '정',
    }
)
if created:
    nurse.set_password('nurse123')
    nurse.save()
    print(f"✓ [Nurse] {nurse.username} 생성 완료")
else:
    print(f"  [Nurse] {nurse.username} 이미 존재")

# 6. Patient
patient, created = User.objects.get_or_create(
    username='patient1',
    defaults={
        'email': 'patient@example.com',
        'role': Role.PATIENT,
        'phone': '010-1234-5678',
        'first_name': '환자',
        'last_name': '홍',
    }
)
if created:
    patient.set_password('patient123')
    patient.save()
    print(f"✓ [Patient] {patient.username} 생성 완료")
else:
    print(f"  [Patient] {patient.username} 이미 존재")

# 7. External
external, created = User.objects.get_or_create(
    username='external1',
    defaults={
        'email': 'external@partner.com',
        'role': Role.EXTERNAL,
        'department': 'External Partner',
        'first_name': '외부',
        'last_name': '강',
    }
)
if created:
    external.set_password('external123')
    external.save()
    print(f"✓ [External] {external.username} 생성 완료")
else:
    print(f"  [External] {external.username} 이미 존재")

print("=" * 50)
print("테스트 사용자 생성 완료!")
print("=" * 50)
print("\n사용자 정보:")
print("-" * 50)

users = User.objects.all().order_by('role')
for user in users:
    print(f"{user.get_role_display():10} | {user.username:12} | {user.email}")

print("-" * 50)
print(f"전체 사용자 수: {User.objects.count()}")
print("\n모든 비밀번호: <role>123 (예: admin123, doctor123)")
