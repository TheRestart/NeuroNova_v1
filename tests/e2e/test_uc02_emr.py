"""
UC02 - EMR (전자의무기록) End-to-End 테스트

목적: 환자 등록, 진료 기록 생성, 처방 생성 전체 시나리오 테스트
작성일: 2026-01-02
"""

import requests
import json
import time
from datetime import datetime, timedelta


class UC02EMRE2ETest:
    """UC02 EMR End-to-End 테스트 클래스"""

    def __init__(self, base_url="http://localhost/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

        # 테스트 데이터
        self.patient_data = {
            "family_name": "테스트",
            "given_name": f"환자{int(time.time())}",
            "birth_date": "1985-03-20",
            "gender": "M",
            "phone": "010-1111-2222",
            "email": f"test_patient_{int(time.time())}@example.com",
            "address": "서울특별시 강남구 테헤란로 123",
            "blood_type": "A+",
            "allergies": ["페니실린"]
        }

        self.encounter_data = {
            "type": "외래",
            "department": "신경외과",
            "chief_complaint": "두통과 어지러움",
            "diagnosis": "편두통 의심",
            "treatment_plan": "약물 치료 및 경과 관찰"
        }

        # 저장된 ID
        self.doctor_token = None
        self.nurse_token = None
        self.patient_id = None
        self.encounter_id = None
        self.order_id = None

    def log_result(self, test_name, status, message, response=None):
        """테스트 결과 로깅"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "status": status,
            "message": message
        }
        if response:
            result["status_code"] = response.status_code
            result["response_time"] = response.elapsed.total_seconds()

        self.test_results.append(result)

        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
        print(f"{status_symbol} {test_name}: {message}")
        if response:
            print(f"  - Status: {response.status_code}, Time: {response.elapsed.total_seconds():.3f}s")

    def doctor_login(self, username="doctor", password="doctor123"):
        """Doctor 로그인 (사전 준비)"""
        url = f"{self.base_url}/acct/login/"
        payload = {"username": username, "password": password}

        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.doctor_token = data.get("access")
                self.log_result(
                    "Doctor Login (Setup)",
                    "PASS",
                    f"Doctor 로그인 성공: {username}",
                    response
                )
                return True
            else:
                self.log_result(
                    "Doctor Login (Setup)",
                    "FAIL",
                    f"로그인 실패: {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("Doctor Login (Setup)", "FAIL", f"예외 발생: {str(e)}")
            return False

    def nurse_login(self, username="nurse", password="nurse123"):
        """Nurse 로그인 (사전 준비)"""
        url = f"{self.base_url}/acct/login/"
        payload = {"username": username, "password": password}

        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.nurse_token = data.get("access")
                self.log_result(
                    "Nurse Login (Setup)",
                    "PASS",
                    f"Nurse 로그인 성공: {username}",
                    response
                )
                return True
            else:
                self.log_result(
                    "Nurse Login (Setup)",
                    "FAIL",
                    f"로그인 실패: {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("Nurse Login (Setup)", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_create_patient(self):
        """시나리오 1: 환자 등록 (병렬 저장: OpenEMR + Django DB)"""
        if not self.doctor_token:
            self.log_result("UC02-1: 환자 등록", "SKIP", "Doctor 토큰이 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        try:
            response = self.session.post(url, json=self.patient_data, headers=headers)

            if response.status_code == 201:
                data = response.json()
                self.patient_id = data.get("patient_id") or data.get("patientId") or data.get("id")

                # Persistence Status 확인 (병렬 저장)
                persistence_status = data.get("persistence_status", {})
                django_success = persistence_status.get("django", {}).get("success", False)
                openemr_success = persistence_status.get("openemr", {}).get("success", False)

                if django_success and openemr_success:
                    self.log_result(
                        "UC02-1: 환자 등록",
                        "PASS",
                        f"환자 등록 성공 (Django + OpenEMR): {self.patient_id}",
                        response
                    )
                elif django_success:
                    self.log_result(
                        "UC02-1: 환자 등록",
                        "PASS",
                        f"환자 등록 성공 (Django만, OpenEMR 실패): {self.patient_id}",
                        response
                    )
                else:
                    self.log_result(
                        "UC02-1: 환자 등록",
                        "FAIL",
                        f"환자 등록 실패 (Django 저장 실패): {response.text}",
                        response
                    )
                    return False

                return True
            else:
                self.log_result(
                    "UC02-1: 환자 등록",
                    "FAIL",
                    f"환자 등록 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-1: 환자 등록", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_get_patient_list(self):
        """시나리오 2: 환자 목록 조회 (Pagination, Filtering)"""
        if not self.doctor_token:
            self.log_result("UC02-2: 환자 목록 조회", "SKIP", "Doctor 토큰이 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        params = {"page": 1, "page_size": 10}

        try:
            response = self.session.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                assert "results" in data or isinstance(data, list)

                patient_count = data.get("count") if isinstance(data, dict) else len(data)

                self.log_result(
                    "UC02-2: 환자 목록 조회",
                    "PASS",
                    f"환자 목록 조회 성공: {patient_count}명",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-2: 환자 목록 조회",
                    "FAIL",
                    f"목록 조회 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-2: 환자 목록 조회", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_get_patient_detail(self):
        """시나리오 3: 환자 상세 조회"""
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC02-3: 환자 상세 조회", "SKIP", "Patient ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/{self.patient_id}/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        try:
            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                assert data.get("family_name") == self.patient_data["family_name"]

                self.log_result(
                    "UC02-3: 환자 상세 조회",
                    "PASS",
                    f"환자 상세 조회 성공: {data.get('family_name')} {data.get('given_name')}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-3: 환자 상세 조회",
                    "FAIL",
                    f"상세 조회 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-3: 환자 상세 조회", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_search_patient(self):
        """시나리오 4: 환자 검색 (이름, 생년월일)"""
        if not self.doctor_token:
            self.log_result("UC02-4: 환자 검색", "SKIP", "Doctor 토큰이 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/search/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        params = {"q": self.patient_data["family_name"]}

        try:
            response = self.session.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                self.log_result(
                    "UC02-4: 환자 검색",
                    "PASS",
                    f"환자 검색 성공: {len(results)}건",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-4: 환자 검색",
                    "FAIL",
                    f"검색 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-4: 환자 검색", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_create_encounter(self):
        """시나리오 5: 진료 기록 생성 (Encounter)"""
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC02-5: 진료 기록 생성", "SKIP", "Patient ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/encounters/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        # Encounter 데이터에 patient_id 추가
        payload = {**self.encounter_data, "patient_id": self.patient_id}

        try:
            response = self.session.post(url, json=payload, headers=headers)

            if response.status_code == 201:
                data = response.json()
                self.encounter_id = data.get("encounter_id") or data.get("encounterId") or data.get("id")

                self.log_result(
                    "UC02-5: 진료 기록 생성",
                    "PASS",
                    f"진료 기록 생성 성공: {self.encounter_id}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-5: 진료 기록 생성",
                    "FAIL",
                    f"진료 기록 생성 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-5: 진료 기록 생성", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_get_encounter_list(self):
        """시나리오 6: 환자 진료 기록 조회 (타임라인)"""
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC02-6: 진료 기록 조회", "SKIP", "Patient ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/{self.patient_id}/encounters/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        try:
            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", []) if isinstance(data, dict) else data
                count = len(results)

                self.log_result(
                    "UC02-6: 진료 기록 조회",
                    "PASS",
                    f"진료 기록 조회 성공: {count}건",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-6: 진료 기록 조회",
                    "FAIL",
                    f"진료 기록 조회 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-6: 진료 기록 조회", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_update_patient(self):
        """시나리오 7: 환자 정보 수정"""
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC02-7: 환자 정보 수정", "SKIP", "Patient ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/patients/{self.patient_id}/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        payload = {"phone": "010-9999-8888", "address": "서울특별시 서초구 서초대로 74길 33"}

        try:
            response = self.session.patch(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                assert data.get("phone") == payload["phone"]

                self.log_result(
                    "UC02-7: 환자 정보 수정",
                    "PASS",
                    f"환자 정보 수정 성공: {self.patient_id}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC02-7: 환자 정보 수정",
                    "FAIL",
                    f"정보 수정 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result("UC02-7: 환자 정보 수정", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_patient_permission(self):
        """시나리오 8: Patient 역할 권한 검증 (본인만 조회)"""
        # Patient 계정으로 로그인 (기존 계정 사용)
        url = f"{self.base_url}/acct/login/"
        payload = {"username": "patient", "password": "patient123"}

        try:
            response = self.session.post(url, json=payload)
            if response.status_code != 200:
                self.log_result("UC02-8: Patient 권한 검증", "SKIP", "Patient 로그인 실패")
                return False

            patient_token = response.json().get("access")

            # 다른 환자 정보 조회 시도 (권한 오류 기대)
            if self.patient_id:
                url = f"{self.base_url}/emr/patients/{self.patient_id}/"
                headers = {"Authorization": f"Bearer {patient_token}"}
                response = self.session.get(url, headers=headers)

                # 403 Forbidden 기대 (본인이 아닌 경우)
                if response.status_code in [403, 404]:
                    self.log_result(
                        "UC02-8: Patient 권한 검증",
                        "PASS",
                        f"권한 검증 정상 (타인 정보 접근 차단): {response.status_code}",
                        response
                    )
                    return True
                else:
                    self.log_result(
                        "UC02-8: Patient 권한 검증",
                        "FAIL",
                        f"권한 검증 실패 (타인 정보 접근 허용): {response.status_code}",
                        response
                    )
                    return False
        except Exception as e:
            self.log_result("UC02-8: Patient 권한 검증", "FAIL", f"예외 발생: {str(e)}")
            return False

    def run_all_tests(self):
        """전체 테스트 실행"""
        print("\n" + "="*80)
        print("UC02 - EMR (전자의무기록) End-to-End 테스트 시작")
        print("="*80 + "\n")

        # 사전 준비
        print("[INFO] 사전 준비: Doctor/Nurse 로그인...")
        self.doctor_login()
        self.nurse_login()
        print()

        # 테스트 시나리오 실행
        tests = [
            ("환자 등록", self.test_create_patient),
            ("환자 목록 조회", self.test_get_patient_list),
            ("환자 상세 조회", self.test_get_patient_detail),
            ("환자 검색", self.test_search_patient),
            ("진료 기록 생성", self.test_create_encounter),
            ("진료 기록 조회", self.test_get_encounter_list),
            ("환자 정보 수정", self.test_update_patient),
            ("Patient 권한 검증", self.test_patient_permission),
        ]

        for test_name, test_func in tests:
            print(f"\n[RUN] {test_name}...")
            test_func()

        # 결과 요약
        self.print_summary()

    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "="*80)
        print("테스트 결과 요약")
        print("="*80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")

        print(f"\n총 테스트: {total}")
        print(f"  - PASS: {passed}")
        print(f"  - FAIL: {failed}")
        print(f"  - SKIP: {skipped}")

        if failed > 0:
            print("\n[FAIL] 실패한 테스트:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test_name']}: {result['message']}")

        # JSON 리포트 저장
        report_file = f"uc02_test_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] 상세 리포트 저장: {report_file}")
        print("="*80 + "\n")


if __name__ == "__main__":
    tester = UC02EMRE2ETest(base_url="http://localhost/api")
    tester.run_all_tests()
