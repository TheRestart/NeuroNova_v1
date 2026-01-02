"""
OpenEMR OAuth2 인증 테스트 스크립트

사용법:
    python test_openemr_auth.py

요구사항:
    - OpenEMR 컨테이너 실행 중
    - .env 파일에 OPENEMR_CLIENT_ID, OPENEMR_CLIENT_SECRET 설정
"""

import sys
import os
from pathlib import Path

# Django 프로젝트 경로 추가
BASE_DIR = Path(__file__).resolve().parent.parent
DJANGO_DIR = BASE_DIR / 'NeuroNova_02_back_end' / '02_django_server'
sys.path.insert(0, str(DJANGO_DIR))

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdss_backend.settings')

import django
django.setup()

from emr.services.openemr_client import OpenEMRClient
from django.conf import settings
import json


def print_section(title):
    """섹션 구분선 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_environment_variables():
    """환경 변수 확인"""
    print_section("1. 환경 변수 확인")

    config = {
        "OPENEMR_BASE_URL": settings.OPENEMR_BASE_URL,
        "OPENEMR_FHIR_URL": settings.OPENEMR_FHIR_URL,
        "OPENEMR_CLIENT_ID": settings.OPENEMR_CLIENT_ID,
        "OPENEMR_CLIENT_SECRET": settings.OPENEMR_CLIENT_SECRET[:10] + "..." if settings.OPENEMR_CLIENT_SECRET else "(Empty)",
        "SKIP_OPENEMR_INTEGRATION": settings.SKIP_OPENEMR_INTEGRATION,
    }

    for key, value in config.items():
        status = "[PASS]" if value and value != "(Empty)" else "[FAIL]"
        print(f"{status} {key}: {value}")

    # 필수 검증
    if not settings.OPENEMR_CLIENT_ID or not settings.OPENEMR_CLIENT_SECRET:
        print("\n[ERROR] OpenEMR OAuth2 credentials not configured!")
        print("Please set OPENEMR_CLIENT_ID and OPENEMR_CLIENT_SECRET in .env file.")
        print("See: 01_doc/50_OpenEMR_OAuth2_설정_가이드.md")
        return False

    return True


def test_client_initialization():
    """OpenEMRClient 초기화 테스트"""
    print_section("2. OpenEMRClient 초기화")

    try:
        client = OpenEMRClient()
        print(f"[PASS] Client initialized")
        print(f"  - Base URL: {client.base_url}")
        print(f"  - Client ID: {client.client_id}")
        print(f"  - Client Secret: {client.client_secret[:10]}..." if client.client_secret else "(Empty)")
        return client
    except Exception as e:
        print(f"[FAIL] Client initialization failed: {e}")
        return None


def test_token_acquisition(client):
    """Access Token 발급 테스트"""
    print_section("3. OAuth2 Access Token 발급")

    try:
        token = client.get_access_token()

        if token:
            print(f"[PASS] Access Token acquired successfully")
            print(f"  - Token (first 30 chars): {token[:30]}...")
            print(f"  - Token length: {len(token)} characters")
            return token
        else:
            print(f"[FAIL] Token acquisition returned None")
            return None

    except Exception as e:
        print(f"[FAIL] Token acquisition failed: {e}")
        return None


def test_fhir_api_call(client):
    """FHIR API 호출 테스트 (Patient 목록 조회)"""
    print_section("4. FHIR API 호출 (Patient 목록)")

    try:
        # Patient 목록 조회 (최대 5개)
        patients = client.get_patients(limit=5)

        if patients is not None:
            print(f"[PASS] Retrieved {len(patients)} patients")

            if patients:
                print("\n  First Patient:")
                first_patient = patients[0]
                print(f"    - ID: {first_patient.get('id', 'N/A')}")

                # 이름 파싱
                name = first_patient.get('name', [{}])[0]
                family = name.get('family', 'N/A')
                given = ' '.join(name.get('given', []))
                print(f"    - Name: {given} {family}")

                print(f"    - Gender: {first_patient.get('gender', 'N/A')}")
                print(f"    - Birth Date: {first_patient.get('birthDate', 'N/A')}")
            else:
                print("  (No patients in OpenEMR database)")

            return True
        else:
            print(f"[FAIL] API call returned None")
            return False

    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        return False


def test_patient_creation(client):
    """환자 생성 테스트"""
    print_section("5. FHIR API 환자 생성 (Optional)")

    print("[INFO] Skipping patient creation test (read-only test)")
    print("  To test patient creation, use: tests/e2e/test_uc02_emr.py")
    return True


def main():
    """메인 테스트 실행"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "OpenEMR OAuth2 인증 테스트")
    print("=" * 80)

    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
    }

    # Test 1: 환경 변수
    results["total"] += 1
    if test_environment_variables():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n[CRITICAL] Environment variables not configured. Aborting.")
        print_summary(results)
        sys.exit(1)

    # Test 2: 클라이언트 초기화
    results["total"] += 1
    client = test_client_initialization()
    if client:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_summary(results)
        sys.exit(1)

    # Test 3: 토큰 발급
    results["total"] += 1
    token = test_token_acquisition(client)
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n[CRITICAL] Token acquisition failed. Check OpenEMR Admin Panel settings.")
        print_summary(results)
        sys.exit(1)

    # Test 4: FHIR API 호출
    results["total"] += 1
    if test_fhir_api_call(client):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 5: 환자 생성 (Skip)
    results["total"] += 1
    if test_patient_creation(client):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # 결과 요약
    print_summary(results)

    # Exit code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


def print_summary(results):
    """테스트 결과 요약 출력"""
    print_section("테스트 결과 요약")

    print(f"Total Tests:  {results['total']}")
    print(f"  [PASS] Passed:  {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"  [FAIL] Failed:  {results['failed']} ({results['failed']/results['total']*100:.1f}%)")

    if results["failed"] == 0:
        print("\n[SUCCESS] All tests passed! OpenEMR OAuth2 is configured correctly.")
        print("\nNext steps:")
        print("  1. Run E2E tests: python tests/e2e/test_uc02_emr.py")
        print("  2. Check Django API: http://localhost:8000/api/emr/patients/")
    else:
        print("\n[WARNING] Some tests failed. Please check the error messages above.")
        print("\nTroubleshooting:")
        print("  1. Check OpenEMR Admin Panel (http://localhost:8081)")
        print("  2. Verify API Client settings (Grant Types, Scopes)")
        print("  3. See: 01_doc/50_OpenEMR_OAuth2_설정_가이드.md")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
