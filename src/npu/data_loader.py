import json
import re

from npu.judge import CROSS, UNDECIDED, X, decide, is_pass, normalize_label
from npu.mac import mac

FILTER_SIZES = (5, 13, 25)
KEY_PATTERN = re.compile(r"^size_(\d+)_\d+$")

# data.json에서 값을 읽어와 (필터만)정규화 후 필터와 패턴을 반환하는 함수
def load_data(path="data/data.json"):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"data.json을 찾을 수 없습니다: {path}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"data.json 형식 오류: {e}")
        return None, None

    filters = {}
    for n in FILTER_SIZES:
        key = f"size_{n}"
        raw = data.get("filters", {}).get(key)
        if raw is None:
            print(f"필터 로드 실패: {key} 키가 없습니다.")
            continue
        filters[n] = {
            normalize_label(label_key): matrix
            for label_key, matrix in raw.items()
            if normalize_label(label_key) is not None
        }
        print(f"{key} 필터 로드 완료")

    return filters, data.get("patterns", {})

# 검증 실패 케이스를 정상 결과와 같은 형식으로 반환 → 중단 없이 다음 케이스 진행
def _fail(key, reason):
    return {
        "key": key,
        "score_cross": None,
        "score_x": None,
        "verdict": None,
        "expected": None,
        "passed": False,
        "reason": reason,
    }

# 패턴 또는 필터가 N x N의 형태가 맞는지 확인하는 함수
def _is_nxn(matrix, n):
    return isinstance(matrix, list) and len(matrix) == n and all(
        isinstance(row, list) and len(row) == n for row in matrix
    )

# 측정 전 패턴을 사용할 수 있는지 확인하고 측정하는 함수
def evaluate_pattern(key, item, filters):
    match = KEY_PATTERN.match(key)
    if not match:
        return _fail(key, f"키 형식 오류: '{key}'는 size_{{N}}_{{idx}} 형식이 아닙니다.")
    n = int(match.group(1))

    if not isinstance(item, dict):
        return _fail(key, "패턴 항목 형식 오류: input/expected를 가진 객체가 아닙니다.")

    size_filters = filters.get(n)
    if not size_filters or CROSS not in size_filters or X not in size_filters:
        return _fail(key, f"size_{n} 필터가 없습니다.")

    expected = normalize_label(item.get("expected"))
    if expected is None:
        return _fail(key, f"라벨 정규화 실패: expected={item.get('expected')!r}")

    pattern = item.get("input")
    filter_cross, filter_x = size_filters[CROSS], size_filters[X]
    if not (_is_nxn(pattern, n) and _is_nxn(filter_cross, n) and _is_nxn(filter_x, n)):
        return _fail(key, f"크기 불일치: 패턴/필터가 {n}×{n}이 아닙니다.")

    score_cross = mac(pattern, filter_cross)
    score_x = mac(pattern, filter_x)
    verdict = decide(score_cross, score_x, CROSS, X)
    passed = is_pass(verdict, expected)

    if verdict == UNDECIDED:
        reason = "두 점수가 동점(UNDECIDED)이라 판정 불가"
    elif not passed:
        reason = f"판정 결과 불일치: 판정={verdict}, expected={expected}"
    else:
        reason = None

    return {
        "key": key,
        "score_cross": score_cross,
        "score_x": score_x,
        "verdict": verdict,
        "expected": expected,
        "passed": passed,
        "reason": reason,
    }


def evaluate_all(patterns, filters):
    return [evaluate_pattern(key, item, filters) for key, item in patterns.items()]
