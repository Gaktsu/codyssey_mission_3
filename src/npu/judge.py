"""라벨 정규화(+/cross → Cross, x → X)와 epsilon(1e-9) 기반 판정, PASS/FAIL."""

CROSS = "Cross"
X = "X"
UNDECIDED = "UNDECIDED"

# 두 점수 차이가 이 값보다 작으면 부동소수점 오차로 보고 동점 처리
EPSILON = 1e-9

# 원본 라벨(소문자, 공백 제거) → 표준 라벨
# expected: '+', 'x' / filter 키: 'cross', 'x'
LABEL_MAP = {"+": CROSS, "cross": CROSS, "x": X}


def normalize_label(raw):
    """원본 라벨을 표준 라벨(Cross / X)로 바꾼다. 알 수 없는 라벨이면 None."""
    if not isinstance(raw, str):
        return None
    return LABEL_MAP.get(raw.strip().lower())


def decide(score_a, score_b, label_a, label_b, tie=UNDECIDED):
    """점수가 큰 쪽의 라벨을 반환한다. |a - b| < EPSILON 이면 tie를 반환한다.

    모드 1: decide(a, b, "A", "B", tie="판정 불가")
    모드 2: decide(cross, x, CROSS, X)  → Cross / X / UNDECIDED
    """
    if abs(score_a - score_b) < EPSILON:
        return tie
    return label_a if score_a > score_b else label_b


def is_pass(verdict, expected):
    """판정이 expected와 같으면 True. UNDECIDED는 항상 FAIL."""
    return verdict != UNDECIDED and verdict == expected
