"""성능 분석: 크기별 MAC 연산 10회 반복 평균(ms) 측정, N×N / 평균 ms / N² 표 출력."""
import time

from npu.judge import CROSS
from npu.mac import mac, make_pattern


def measure_avg_ms(pattern, filt, repeats=10):
    """MAC 연산을 repeats회 반복해 평균 소요 시간(ms)을 반환한다. I/O는 측정 구간 밖."""
    start = time.perf_counter()
    for _ in range(repeats):
        mac(pattern, filt)
    elapsed = time.perf_counter() - start
    return elapsed * 1000 / repeats


def measure_sizes(sizes=(3, 5, 13, 25), repeats=10):
    """크기별로 B1 생성기 패턴/필터를 만들어 평균 시간(ms)을 측정한다.

    반환: (크기, 평균 ms, 연산 횟수 N²) 튜플 리스트.
    """
    results = []
    for n in sizes:
        pattern = make_pattern(n, CROSS)
        filt = make_pattern(n, CROSS)
        avg_ms = measure_avg_ms(pattern, filt, repeats)
        results.append((n, avg_ms, n * n))
    return results


def format_table(rows):
    """(크기, 평균 ms, N²) 리스트를 '크기(N×N) / 평균 시간(ms) / 연산 횟수(N²)' 표 문자열로 만든다."""
    header = f"{'크기 (N×N)':<12}{'평균 시간 (ms)':<16}{'연산 횟수 (N²)':<14}"
    lines = [header]
    for n, avg_ms, ops in rows:
        lines.append(f"{f'{n}×{n}':<12}{avg_ms:<16.4f}{ops:<14}")
    return "\n".join(lines)
