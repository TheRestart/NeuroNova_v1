"""
UC03 - OCS (처방전달) End-to-End 테스트

목적: 처방 생성, 상태 변경, 워크플로우 전체 시나리오 테스트
작성일: 2026-01-02
"""

import requests
import json
import time
from datetime import datetime


class UC03OCSE2ETest:
    """UC03 OCS End-to-End 테스트 클래스"""

    def __init__(self, base_url="http://localhost/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

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

    def setup(self):
        """사전 준비: 로그인, 환자/진료 기록 생성"""
        # Doctor 로그인
        url = f"{self.base_url}/acct/login/"
        response = self.session.post(url, json={"username": "doctor", "password": "doctor123"})
        if response.status_code == 200:
            self.doctor_token = response.json().get("access")
            print("[SETUP] Doctor 로그인 성공")
        else:
            print("[SETUP] Doctor 로그인 실패")
            return False

        # Nurse 로그인
        response = self.session.post(url, json={"username": "nurse", "password": "nurse123"})
        if response.status_code == 200:
            self.nurse_token = response.json().get("access")
            print("[SETUP] Nurse 로그인 성공")
        else:
            print("[SETUP] Nurse 로그인 실패")

        # 환자 목록에서 첫 번째 환자 선택
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        response = self.session.get(f"{self.base_url}/emr/patients/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", []) if isinstance(data, dict) else data
            if results:
                self.patient_id = results[0].get("patient_id") or results[0].get("id")
                print(f"[SETUP] 환자 선택: {self.patient_id}")
            else:
                print("[SETUP] 환자가 없습니다 (샘플 데이터 필요)")
                return False

        return True

    def test_create_order(self):
        """시나리오 1: 처방 생성 (Doctor)"""
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC03-1: 처방 생성", "SKIP", "사전 데이터가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/orders/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        payload = {
            "patient_id": self.patient_id,
            "order_type": "medication",
            "order_items": [
                {
                    "medication_master_id": 1,  # 샘플 데이터 (아스피린 등)
                    "dosage": "1정",
                    "frequency": "1일 1회",
                    "duration": 7,
                    "route": "경구"
                }
            ],
            "urgency": "routine",
            "notes": "혈압 모니터링 필요"
        }

        try:
            response = self.session.post(url, json=payload, headers=headers)
            if response.status_code == 201:
                data = response.json()
                self.order_id = data.get("order_id") or data.get("id")
                self.log_result("UC03-1: 처방 생성", "PASS", f"처방 생성 성공: {self.order_id}", response)
                return True
            else:
                self.log_result("UC03-1: 처방 생성", "FAIL", f"처방 생성 실패: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("UC03-1: 처방 생성", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_get_order_list(self):
        """시나리오 2: 처방 목록 조회"""
        if not self.doctor_token:
            self.log_result("UC03-2: 처방 목록 조회", "SKIP", "Doctor 토큰이 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/orders/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", []) if isinstance(data, dict) else data
                self.log_result("UC03-2: 처방 목록 조회", "PASS", f"처방 목록 조회 성공: {len(results)}건", response)
                return True
            else:
                self.log_result("UC03-2: 처방 목록 조회", "FAIL", f"목록 조회 실패: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("UC03-2: 처방 목록 조회", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_get_order_detail(self):
        """시나리오 3: 처방 상세 조회"""
        if not self.doctor_token or not self.order_id:
            self.log_result("UC03-3: 처방 상세 조회", "SKIP", "Order ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/orders/{self.order_id}/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}

        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_result("UC03-3: 처방 상세 조회", "PASS", f"처방 상세 조회 성공: {data.get('status')}", response)
                return True
            else:
                self.log_result("UC03-3: 처방 상세 조회", "FAIL", f"상세 조회 실패: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("UC03-3: 처방 상세 조회", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_execute_order(self):
        """시나리오 4: 처방 집행 (Nurse)"""
        if not self.nurse_token or not self.order_id:
            self.log_result("UC03-4: 처방 집행", "SKIP", "Nurse 토큰 또는 Order ID가 없어 건너뜀")
            return False

        url = f"{self.base_url}/emr/orders/{self.order_id}/execute/"
        headers = {"Authorization": f"Bearer {self.nurse_token}"}

        try:
            response = self.session.post(url, headers=headers)
            if response.status_code in [200, 204]:
                self.log_result("UC03-4: 처방 집행", "PASS", f"처방 집행 성공: {self.order_id}", response)
                return True
            else:
                self.log_result("UC03-4: 처방 집행", "FAIL", f"처방 집행 실패: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("UC03-4: 처방 집행", "FAIL", f"예외 발생: {str(e)}")
            return False

    def test_cancel_order(self):
        """시나리오 5: 처방 취소 (Doctor)"""
        # 새 처방 생성 후 취소 테스트
        if not self.doctor_token or not self.patient_id:
            self.log_result("UC03-5: 처방 취소", "SKIP", "사전 데이터가 없어 건너뜀")
            return False

        # 취소 테스트용 처방 생성
        url = f"{self.base_url}/emr/orders/"
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        payload = {
            "patient_id": self.patient_id,
            "order_type": "medication",
            "order_items": [{"medication_master_id": 1, "dosage": "1정", "frequency": "1일 1회", "duration": 3, "route": "경구"}]
        }

        try:
            response = self.session.post(url, json=payload, headers=headers)
            if response.status_code != 201:
                self.log_result("UC03-5: 처방 취소", "FAIL", "처방 생성 실패 (취소 테스트용)", response)
                return False

            cancel_order_id = response.json().get("order_id") or response.json().get("id")

            # 처방 취소
            url = f"{self.base_url}/emr/orders/{cancel_order_id}/cancel/"
            response = self.session.post(url, headers=headers)

            if response.status_code in [200, 204]:
                self.log_result("UC03-5: 처방 취소", "PASS", f"처방 취소 성공: {cancel_order_id}", response)
                return True
            else:
                self.log_result("UC03-5: 처방 취소", "FAIL", f"처방 취소 실패: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("UC03-5: 처방 취소", "FAIL", f"예외 발생: {str(e)}")
            return False

    def run_all_tests(self):
        """전체 테스트 실행"""
        print("\n" + "="*80)
        print("UC03 - OCS (처방전달) End-to-End 테스트 시작")
        print("="*80 + "\n")

        if not self.setup():
            print("[ERROR] 사전 준비 실패")
            return

        tests = [
            ("처방 생성", self.test_create_order),
            ("처방 목록 조회", self.test_get_order_list),
            ("처방 상세 조회", self.test_get_order_detail),
            ("처방 집행", self.test_execute_order),
            ("처방 취소", self.test_cancel_order),
        ]

        for test_name, test_func in tests:
            print(f"\n[RUN] {test_name}...")
            test_func()

        self.print_summary()

    def print_summary(self):
        """테스트 결과 요약"""
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

        report_file = f"uc03_test_report_{int(time.time())}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] 상세 리포트 저장: {report_file}")
        print("="*80 + "\n")


if __name__ == "__main__":
    tester = UC03OCSE2ETest(base_url="http://localhost/api")
    tester.run_all_tests()
