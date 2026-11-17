CROSS = "Cross"
X = "X"
UNDECIDED = "UNDECIDED"

# 두 점수 차이가 이 값보다 작으면 부동소수점 오차로 보고 동점 처리
EPSILON = 1e-9

# 원본 라벨(소문자, 공백 제거) → 표준 라벨
# expected: '+', 'x' / filter 키: 'cross', 'x'
LABEL_MAP = {"+": CROSS, "cross": CROSS, "x": X}

# data.json의 라벨들을 정규화 ("+", "cross"는 "Cross"로 변경 // "x"는 "X"로 변경)
def normalize_label(raw):
    if not isinstance(raw, str):
        return None
    return LABEL_MAP.get(raw.strip().lower())

# 점수 비교하는 함수
# 1e-9보다 작은 오차가 발생할 경우 동점으로 정함
# 더 높은 점수쪽의 label을 반환
def decide(score_a, score_b, label_a, label_b, tie=UNDECIDED):
    if abs(score_a - score_b) < EPSILON:
        return tie
    return label_a if score_a > score_b else label_b

# 판정이 예상과 같다면 True, 아니면 False
def is_pass(verdict, expected):
    return verdict != UNDECIDED and verdict == expected
