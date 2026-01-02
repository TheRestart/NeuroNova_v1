"""
UC01 - 인증/권한 End-to-End 테스트

목적: 회원가입, 로그인, 토큰 갱신, 권한 검증 전체 시나리오 테스트
작성일: 2026-01-02
"""

import requests
import json
import time
from datetime import datetime


class UC01AuthE2ETest:
    """UC01 인증/권한 End-to-End 테스트 클래스"""

    def __init__(self, base_url="http://localhost/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

        # 테스트 데이터
        self.patient_data = {
            "username": f"patient_e2e_{int(time.time())}",
            "password": "TestP@ss123",
            "email": f"patient_e2e_{int(time.time())}@example.com",
            "role": "patient",
            "firstName": "테스트",
            "lastName": "환자",
            "phone": "010-1234-5678"
        }

        self.doctor_data = {
            "username": f"doctor_e2e_{int(time.time())}",
            "password": "TestP@ss123",
            "email": f"doctor_e2e_{int(time.time())}@hospital.com",
            "role": "doctor",
            "employeeId": f"D-E2E-{int(time.time())}",
            "department": "신경외과",
            "firstName": "테스트",
            "lastName": "의사",
            "phone": "010-9999-0000"
        }

        # 인증 토큰
        self.admin_token = None
        self.patient_token = None
        self.doctor_token = None
        self.refresh_token = None

    def log_result(self, test_name, status, message, response=None):
        """테스트 결과 로깅"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "status": status,  # PASS, FAIL, SKIP
            "message": message
        }
        if response:
            result["status_code"] = response.status_code
            result["response_time"] = response.elapsed.total_seconds()

        self.test_results.append(result)

        # 콘솔 출력
        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
        print(f"{status_symbol} {test_name}: {message}")
        if response:
            print(f"  - Status: {response.status_code}, Time: {response.elapsed.total_seconds():.3f}s")

    def admin_login(self, username="admin", password="admin123"):
        """Admin 로그인 (사전 준비)"""
        url = f"{self.base_url}/acct/login/"
        payload = {
            "username": username,
            "password": password
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access")
                self.log_result(
                    "Admin Login (Setup)",
                    "PASS",
                    f"Admin 로그인 성공: {username}",
                    response
                )
                return True
            else:
                self.log_result(
                    "Admin Login (Setup)",
                    "FAIL",
                    f"Admin 로그인 실패: {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "Admin Login (Setup)",
                "FAIL",
                f"Admin 로그인 예외 발생: {str(e)}"
            )
            return False

    def test_patient_register(self):
        """시나리오 1-1: Patient 자가 회원가입"""
        url = f"{self.base_url}/acct/register/"

        try:
            response = self.session.post(url, json=self.patient_data)

            if response.status_code == 201:
                data = response.json()
                assert data.get("username") == self.patient_data["username"]
                assert data.get("role") == "patient"

                self.log_result(
                    "UC01-1: Patient 회원가입",
                    "PASS",
                    f"환자 회원가입 성공: {self.patient_data['username']}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-1: Patient 회원가입",
                    "FAIL",
                    f"회원가입 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-1: Patient 회원가입",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_doctor_register_by_admin(self):
        """시나리오 1-2: Admin이 Doctor 계정 생성"""
        if not self.admin_token:
            self.log_result(
                "UC01-2: Doctor 계정 생성 (Admin)",
                "SKIP",
                "Admin 토큰이 없어 건너뜀"
            )
            return False

        url = f"{self.base_url}/acct/register/"
        headers = {"Authorization": f"Bearer {self.admin_token}"}

        try:
            response = self.session.post(url, json=self.doctor_data, headers=headers)

            if response.status_code == 201:
                data = response.json()
                assert data.get("username") == self.doctor_data["username"]
                assert data.get("role") == "doctor"

                self.log_result(
                    "UC01-2: Doctor 계정 생성 (Admin)",
                    "PASS",
                    f"의사 계정 생성 성공: {self.doctor_data['username']}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-2: Doctor 계정 생성 (Admin)",
                    "FAIL",
                    f"계정 생성 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-2: Doctor 계정 생성 (Admin)",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_patient_login(self):
        """시나리오 2-1: Patient 로그인"""
        url = f"{self.base_url}/acct/login/"
        payload = {
            "username": self.patient_data["username"],
            "password": self.patient_data["password"]
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "access" in data
                assert "refresh" in data
                assert data.get("user", {}).get("role") == "patient"

                self.patient_token = data["access"]
                self.refresh_token = data["refresh"]

                self.log_result(
                    "UC01-3: Patient 로그인",
                    "PASS",
                    f"환자 로그인 성공, JWT 토큰 발급됨",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-3: Patient 로그인",
                    "FAIL",
                    f"로그인 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-3: Patient 로그인",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_doctor_login(self):
        """시나리오 2-2: Doctor 로그인"""
        url = f"{self.base_url}/acct/login/"
        payload = {
            "username": self.doctor_data["username"],
            "password": self.doctor_data["password"]
        }

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "access" in data
                assert "refresh" in data
                assert data.get("user", {}).get("role") == "doctor"

                self.doctor_token = data["access"]

                self.log_result(
                    "UC01-4: Doctor 로그인",
                    "PASS",
                    f"의사 로그인 성공, JWT 토큰 발급됨",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-4: Doctor 로그인",
                    "FAIL",
                    f"로그인 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-4: Doctor 로그인",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_token_refresh(self):
        """시나리오 3: Refresh Token으로 Access Token 갱신"""
        if not self.refresh_token:
            self.log_result(
                "UC01-5: 토큰 갱신",
                "SKIP",
                "Refresh 토큰이 없어 건너뜀"
            )
            return False

        url = f"{self.base_url}/acct/token/refresh/"
        payload = {"refresh": self.refresh_token}

        try:
            response = self.session.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                assert "access" in data

                # 새 토큰 저장
                new_access_token = data["access"]

                self.log_result(
                    "UC01-5: 토큰 갱신",
                    "PASS",
                    f"Access Token 갱신 성공",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-5: 토큰 갱신",
                    "FAIL",
                    f"토큰 갱신 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-5: 토큰 갱신",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_get_current_user(self):
        """시나리오 4: 현재 로그인 사용자 정보 조회"""
        if not self.patient_token:
            self.log_result(
                "UC01-6: 사용자 정보 조회",
                "SKIP",
                "Patient 토큰이 없어 건너뜀"
            )
            return False

        url = f"{self.base_url}/acct/me/"
        headers = {"Authorization": f"Bearer {self.patient_token}"}

        try:
            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                assert data.get("username") == self.patient_data["username"]
                assert data.get("role") == "patient"

                self.log_result(
                    "UC01-6: 사용자 정보 조회",
                    "PASS",
                    f"사용자 정보 조회 성공: {data.get('username')}",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-6: 사용자 정보 조회",
                    "FAIL",
                    f"정보 조회 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-6: 사용자 정보 조회",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_permission_denied(self):
        """시나리오 5: 권한 없는 API 접근 시도 (Patient → Admin 전용 API)"""
        if not self.patient_token:
            self.log_result(
                "UC01-7: 권한 검증 (403)",
                "SKIP",
                "Patient 토큰이 없어 건너뜀"
            )
            return False

        # Admin 전용 API에 Patient 토큰으로 접근 시도
        url = f"{self.base_url}/acct/users/"
        headers = {"Authorization": f"Bearer {self.patient_token}"}

        try:
            response = self.session.get(url, headers=headers)

            # 403 Forbidden 또는 401 Unauthorized를 기대
            if response.status_code in [403, 401]:
                self.log_result(
                    "UC01-7: 권한 검증 (403)",
                    "PASS",
                    f"권한 검증 정상 작동 (Status: {response.status_code})",
                    response
                )
                return True
            elif response.status_code == 200:
                self.log_result(
                    "UC01-7: 권한 검증 (403)",
                    "FAIL",
                    f"권한 검증 실패: Patient가 Admin API에 접근 가능함",
                    response
                )
                return False
            else:
                self.log_result(
                    "UC01-7: 권한 검증 (403)",
                    "FAIL",
                    f"예상치 못한 응답 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-7: 권한 검증 (403)",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def test_logout(self):
        """시나리오 6: 로그아웃 (선택적)"""
        if not self.patient_token:
            self.log_result(
                "UC01-8: 로그아웃",
                "SKIP",
                "Patient 토큰이 없어 건너뜀"
            )
            return False

        url = f"{self.base_url}/acct/logout/"
        headers = {"Authorization": f"Bearer {self.patient_token}"}

        try:
            response = self.session.post(url, headers=headers)

            if response.status_code in [200, 204, 205]:
                self.log_result(
                    "UC01-8: 로그아웃",
                    "PASS",
                    f"로그아웃 성공",
                    response
                )
                return True
            else:
                self.log_result(
                    "UC01-8: 로그아웃",
                    "FAIL",
                    f"로그아웃 실패 (Status: {response.status_code}): {response.text}",
                    response
                )
                return False
        except Exception as e:
            self.log_result(
                "UC01-8: 로그아웃",
                "FAIL",
                f"예외 발생: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """전체 테스트 실행"""
        print("\n" + "="*80)
        print("UC01 - 인증/권한 End-to-End 테스트 시작")
        print("="*80 + "\n")

        # 사전 준비: Admin 로그인
        print("[INFO] 사전 준비: Admin 로그인...")
        self.admin_login()
        print()

        # 테스트 시나리오 실행
        tests = [
            ("회원가입", self.test_patient_register),
            ("의사 계정 생성", self.test_doctor_register_by_admin),
            ("환자 로그인", self.test_patient_login),
            ("의사 로그인", self.test_doctor_login),
            ("토큰 갱신", self.test_token_refresh),
            ("사용자 정보 조회", self.test_get_current_user),
            ("권한 검증", self.test_permission_denied),
            ("로그아웃", self.test_logout),
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
        report_file = f"uc01_test_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] 상세 리포트 저장: {report_file}")
        print("="*80 + "\n")


if __name__ == "__main__":
    # 테스트 실행
    tester = UC01AuthE2ETest(base_url="http://localhost/api")
    tester.run_all_tests()
