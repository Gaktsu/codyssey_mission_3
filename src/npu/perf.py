import time

from npu.judge import CROSS
from npu.mac import mac, make_pattern

# MAC 연산을 10회 반복해서 평균 소요 시간을 측정함
def measure_avg_ms(pattern, filt, repeats=10):
    start = time.perf_counter()
    for _ in range(repeats):
        mac(pattern, filt)
    elapsed = time.perf_counter() - start
    return elapsed * 1000 / repeats

# 패턴 생성기를 통해 사이즈별 패턴을 만들고 이것으로 각각의 평균 소요 시간을 측정
def measure_sizes(sizes=(3, 5, 13, 25), repeats=10):
    results = []
    for n in sizes:
        pattern = make_pattern(n, CROSS)
        filt = make_pattern(n, CROSS)
        avg_ms = measure_avg_ms(pattern, filt, repeats)
        results.append((n, avg_ms, n * n))
    return results

# data.json의 패턴/필터로 사이즈별 평균 소요 시간을 측정 (검증을 통과해 점수가 계산된 케이스만 사용)
def measure_data_sizes(results, patterns, filters, repeats=10):
    rows = []
    for n in sorted(filters):
        cases = [
            patterns[r["key"]]["input"]
            for r in results
            if r["score_cross"] is not None and r["key"].split("_")[1] == str(n)
        ]
        if not cases:
            continue
        filt = filters[n][CROSS]
        avg_ms = sum(measure_avg_ms(p, filt, repeats) for p in cases) / len(cases)
        rows.append((n, avg_ms, n * n))
    return rows

# 각 사이즈별 MAC연산 수행 결과들을 테이블 형식으로 반환
def format_table(rows):
    header = f"{'크기 (N×N)':<12}{'평균 시간 (ms)':<16}{'연산 횟수 (N²)':<14}"
    lines = [header]
    for n, avg_ms, ops in rows:
        lines.append(f"{f'{n}×{n}':<14}{avg_ms:<20f}{ops:<14}")
    return "\n".join(lines)
