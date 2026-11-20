from npu.data_loader import evaluate_all, load_data
from npu.judge import CROSS, X, decide
from npu.mac import mac, make_pattern
from npu.perf import format_table, measure_avg_ms, measure_data_sizes, measure_sizes

ROW_ERROR = "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."

def main():
    try:
        while True:
            choice = input("모드를 선택하세요 (1: 사용자 입력, 2: data.json 분석, 3: 패턴 생성기): ").strip()
            # 3x3 입력으로 사용자가 패턴을 직접 정한 뒤 MAC연산을 수행
            if choice == "1":
                return run_mode1()
            # data.json에 있는 5x5, 13x13, 25x25 패턴을 가져와서 MAC연산을 수행
            if choice == "2":
                return run_mode2()
            # 패턴 생성기로 사이즈별 패턴을 만들어 MAC연산 성능을 측정
            if choice == "3":
                return run_mode3()
            print("잘못된 선택입니다. 1, 2 또는 3을 입력하세요.")
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 종료되어 프로그램을 종료합니다.")
        return None

# ============== 모드 1 ==============

# 사용자 입력 모드를 실행
def run_mode1():
    print()
    filter_a = read_matrix("필터 A")
    print("필터 A 저장 완료\n")
    filter_b = read_matrix("필터 B")
    print("필터 B 저장 완료\n")

    pattern = read_matrix("패턴")
    print()

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    verdict = decide(score_a, score_b, "A", "B", tie="판정 불가")
    avg_ms = measure_avg_ms(pattern, filter_a)

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_ms:.4f} ms")
    print(f"판정: {verdict}")

    return {"score_a": score_a, "score_b": score_b, "verdict": verdict, "avg_ms": avg_ms}

# 사용자 입력 모드(모드 1)일 경우 패턴을 받아 측정하는 함수
def read_matrix(label):
    print(f"{label} 입력 (한 줄에 3개 숫자, 공백 구분):")
    return [read_row(f"{label} {i + 1}행: ") for i in range(3)]

# 패턴을 입력 및 검증하는 함수
def read_row(prompt):
    while True: 
        row = parse_row(input(prompt))
        if row is not None:
            return row
        print(ROW_ERROR)

# 사용자 입력이 유효한지 확인하는 함수
def parse_row(line):
    parts = line.split()
    if len(parts) != 3:
        return None
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None

# ============== 모드 2 ==============

# data.json에 있는 필터와 패턴을 통해 측정하는 함수
def run_mode2(data_path="data/data.json"):
    print()
    filters, patterns = load_data(data_path)
    if filters is None:
        return None

    results = evaluate_all(patterns, filters)

    print()
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"{r['key']}: Cross={r['score_cross']}, X={r['score_x']}, "
            f"판정={r['verdict']}, expected={r['expected']}, {status}"
        )

    print()
    print(format_table(measure_data_sizes(results, patterns, filters)))

    total = len(results)
    passed = sum(r["passed"] for r in results)
    failed = total - passed
    print()
    print(f"총 {total} / 통과 {passed} / 실패 {failed}")

    failures = [r for r in results if not r["passed"]]
    if failures:
        print()
        print("실패 케이스:")
        for r in failures:
            print(f"  {r['key']}: {r['reason']}")

# ============== 모드 3 ==============

# 패턴 생성기로 사이즈별 필터, 패턴을 만들어 보여주고 MAC연산 평균 시간을 표로 출력하는 함수
def run_mode3(sizes=(3, 5, 13, 25)):
    print()
    for n in sizes:
        filter_cross = make_pattern(n, CROSS)
        filter_x = make_pattern(n, X)
        pattern = make_pattern(n, CROSS)

        print(f"===== {n}×{n} =====")
        print("필터 Cross:")
        print_matrix(filter_cross)
        print()
        print("필터 X:")
        print_matrix(filter_x)
        print()
        print("패턴:")
        print_matrix(pattern)
        print()

        score_cross = mac(pattern, filter_cross)
        score_x = mac(pattern, filter_x)
        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")
        print(f"판정: {decide(score_cross, score_x, CROSS, X)}")
        print()

    print(format_table(measure_sizes(sizes)))

# 행렬을 한 줄씩 공백으로 구분해 출력하는 함수
def print_matrix(matrix):
    for row in matrix:
        print(" ".join(f"{v:g}" for v in row))


if __name__ == "__main__":
    main()
