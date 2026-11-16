"""진입점: 모드 선택, 모드 1 입력(검증·재입력), 결과/요약 출력."""
from npu.data_loader import evaluate_all, load_data
from npu.judge import decide
from npu.mac import mac
from npu.perf import format_table, measure_avg_ms, measure_sizes

ROW_ERROR = "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(line):
    """공백으로 구분된 숫자 3개 줄을 float 리스트로 변환한다. 실패 시 None."""
    parts = line.split()
    if len(parts) != 3:
        return None
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None


def read_row(prompt):
    """유효한 숫자 3개가 입력될 때까지 해당 줄만 다시 입력받는다."""
    while True:
        row = parse_row(input(prompt))
        if row is not None:
            return row
        print(ROW_ERROR)


def read_matrix(label):
    """3×3 행렬을 한 줄(행)씩 입력받는다. 행 하나가 틀리면 그 행만 재입력."""
    print(f"{label} 입력 (한 줄에 3개 숫자, 공백 구분):")
    return [read_row(f"{label} {i + 1}행: ") for i in range(3)]


def run_mode1():
    """모드 1: 필터 A/B 입력 → 저장 확인 → 패턴 입력 → MAC 연산 → 판정 → 성능(3×3).

    연산 시간은 패턴×필터A를 10회 반복한 평균(ms)을 대표값으로 쓴다
    (A·B 모두 같은 3×3 크기라 MAC 1회 비용은 동일하다).
    """
    filter_a = read_matrix("필터 A")
    print("필터 A 저장 완료")
    filter_b = read_matrix("필터 B")
    print("필터 B 저장 완료")
    pattern = read_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    verdict = decide(score_a, score_b, "A", "B", tie="판정 불가")
    avg_ms = measure_avg_ms(pattern, filter_a)

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_ms:.4f} ms")
    print(f"판정: {verdict}")

    return {"score_a": score_a, "score_b": score_b, "verdict": verdict, "avg_ms": avg_ms}


def run_mode2(data_path="data/data.json"):
    """모드 2: 필터 로드 → 패턴 평가 → 성능 분석 → 결과 요약.

    data.json을 못 읽으면(load_data가 None 반환) 메시지를 남기고 None을 반환한다.
    """
    filters, patterns = load_data(data_path)
    if filters is None:
        return None

    results = evaluate_all(patterns, filters)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"{r['key']}: Cross={r['score_cross']}, X={r['score_x']}, "
            f"판정={r['verdict']}, expected={r['expected']}, {status}"
        )

    print(format_table(measure_sizes()))

    total = len(results)
    passed = sum(r["passed"] for r in results)
    failed = total - passed
    print(f"총 {total} / 통과 {passed} / 실패 {failed}")

    failures = [r for r in results if not r["passed"]]
    if failures:
        print("실패 케이스:")
        for r in failures:
            print(f"  {r['key']}: {r['reason']}")

    return {"results": results, "total": total, "passed": passed, "failed": failed}


def main():
    """진입점: 모드를 선택해 실행한다.

    1/2가 아닌 입력은 안내 후 재입력. Ctrl+D(EOF)·Ctrl+C는 안내 후 조용히 종료한다.
    """
    try:
        while True:
            choice = input("모드를 선택하세요 (1: 사용자 입력, 2: data.json 분석): ").strip()
            if choice == "1":
                return run_mode1()
            if choice == "2":
                return run_mode2()
            print("잘못된 선택입니다. 1 또는 2를 입력하세요.")
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 종료되어 프로그램을 종료합니다.")
        return None


if __name__ == "__main__":
    main()
