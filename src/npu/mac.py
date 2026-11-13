"""MAC 연산(반복문 직접 구현). (보너스) N×N Cross/X 패턴 생성기."""


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
