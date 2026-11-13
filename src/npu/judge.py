"""라벨 정규화(+/cross → Cross, x → X)와 epsilon(1e-9) 기반 판정, PASS/FAIL."""

CROSS = "Cross"
X = "X"

# 원본 라벨(소문자, 공백 제거) → 표준 라벨
# expected: '+', 'x' / filter 키: 'cross', 'x'
LABEL_MAP = {"+": CROSS, "cross": CROSS, "x": X}


def normalize_label(raw):
    """원본 라벨을 표준 라벨(Cross / X)로 바꾼다. 알 수 없는 라벨이면 None."""
    if not isinstance(raw, str):
        return None
    return LABEL_MAP.get(raw.strip().lower())
