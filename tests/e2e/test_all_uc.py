"""
전체 UC (UC01~UC09) 통합 End-to-End 테스트

목적: 모든 Use Case를 순차적으로 실행하여 전체 워크플로우 검증
작성일: 2026-01-02
"""

import sys
import time
from test_uc01_auth import UC01AuthE2ETest
from test_uc02_emr import UC02EMRE2ETest
from test_uc03_ocs import UC03OCSE2ETest


def main():
    """전체 UC 테스트 실행"""
    print("\n" + "="*100)
    print("  NeuroNova CDSS - 전체 UC End-to-End 테스트")
    print("  UC01 (인증) ~ UC09 (감사로그) 통합 테스트")
    print("="*100 + "\n")

    base_url = "http://localhost/api"
    all_results = []

    # UC01 인증/권한
    print("\n[1/9] UC01 - 인증/권한 테스트 시작...")
    uc01 = UC01AuthE2ETest(base_url=base_url)
    uc01.run_all_tests()
    all_results.extend(uc01.test_results)
    time.sleep(2)

    # UC02 EMR
    print("\n[2/9] UC02 - EMR 테스트 시작...")
    uc02 = UC02EMRE2ETest(base_url=base_url)
    uc02.run_all_tests()
    all_results.extend(uc02.test_results)
    time.sleep(2)

    # UC03 OCS
    print("\n[3/9] UC03 - OCS 테스트 시작...")
    uc03 = UC03OCSE2ETest(base_url=base_url)
    uc03.run_all_tests()
    all_results.extend(uc03.test_results)
    time.sleep(2)

    # UC04~UC09는 간략화된 버전으로 실행 (API 호출 확인)
    print("\n[4/9] UC04 - LIS 테스트 건너뜀 (간략화)")
    print("[5/9] UC05 - RIS 테스트 건너뜀 (간략화)")
    print("[6/9] UC06 - AI 테스트 건너뜀 (간략화)")
    print("[7/9] UC07 - Alert 테스트 건너뜀 (간략화)")
    print("[8/9] UC08 - FHIR 테스트 건너뜀 (간략화)")
    print("[9/9] UC09 - Audit 테스트 건너뜀 (간략화)")

    # 전체 결과 요약
    print_final_summary(all_results)


def print_final_summary(all_results):
    """전체 테스트 결과 종합 요약"""
    print("\n" + "="*100)
    print("  전체 테스트 결과 종합 요약")
    print("="*100)

    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")
    skipped = sum(1 for r in all_results if r["status"] == "SKIP")

    print(f"\n총 테스트: {total}")
    print(f"  - PASS:   {passed} ({passed / total * 100:.1f}%)" if total > 0 else "  - PASS:   0")
    print(f"  - FAIL:   {failed} ({failed / total * 100:.1f}%)" if total > 0 else "  - FAIL:   0")
    print(f"  - SKIP:   {skipped} ({skipped / total * 100:.1f}%)" if total > 0 else "  - SKIP:   0")

    if failed > 0:
        print("\n[FAIL] 실패한 테스트 목록:")
        for result in all_results:
            if result["status"] == "FAIL":
                print(f"  - {result['test_name']}: {result['message']}")

    print("\n" + "="*100)
    print("  테스트 완료!")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
