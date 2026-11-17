from npu.judge import CROSS, X

# MAC 연산을 수행하는 함수
def mac(pattern, filt):
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total

# 패턴 생성하는 함수 (보너스 과제 1)
def make_pattern(n, label):
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
