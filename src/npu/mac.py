"""MAC 연산(반복문 직접 구현). (보너스) N×N Cross/X 패턴 생성기."""
from npu.judge import CROSS, X


def mac(pattern, filt):
    """같은 위치의 값끼리 곱해 모두 더한 점수(float)를 반환한다.

    pattern, filt는 같은 크기의 n×n 2차원 리스트여야 한다.
    크기 검증은 호출하는 쪽(data_loader)에서 먼저 수행한다.
    """
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def make_pattern(n, label):
    """N×N Cross 또는 X 패턴을 생성한다. (1.0 = 채움, 0.0 = 빈칸)

    Cross: 가운데 행과 가운데 열이 1
    X:     두 대각선(i == j, i + j == n - 1)이 1
    가운데가 하나로 정해지도록 n은 양의 홀수만 허용한다.
    """
    if n < 1 or n % 2 == 0:
        raise ValueError(f"n은 양의 홀수여야 합니다: {n}")
    if label not in (CROSS, X):
        raise ValueError(f"label은 {CROSS} 또는 {X}여야 합니다: {label}")

    c = n // 2
    pattern = []
    for i in range(n):
        row = []
        for j in range(n):
            if label == CROSS:
                filled = i == c or j == c
            else:
                filled = i == j or i + j == n - 1
            row.append(1.0 if filled else 0.0)
        pattern.append(row)
    return pattern
