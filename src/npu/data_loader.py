"""모드 2: data.json 로드, 키(size_N_idx) 파싱, 필터 선택, 스키마/크기 검증(케이스 단위 FAIL)."""
import json
import re

from npu.judge import CROSS, UNDECIDED, X, decide, is_pass, normalize_label
from npu.mac import mac

FILTER_SIZES = (5, 13, 25)
KEY_PATTERN = re.compile(r"^size_(\d+)_\d+$")


def load_data(path="data/data.json"):
    """data.json을 읽어 크기별 필터와 패턴 목록을 반환한다.

    반환: (filters, patterns). filters는 {5: {"Cross": [...], "X": [...]}, 13: {...}, 25: {...}}.
    파일이 없거나 JSON 문법 오류면 안내 메시지를 출력하고 (None, None)을 반환한다(크래시 없음).
    """
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


def _is_nxn(matrix, n):
    return isinstance(matrix, list) and len(matrix) == n and all(
        isinstance(row, list) and len(row) == n for row in matrix
    )


def evaluate_pattern(key, item, filters):
    """패턴 1건을 검증·채점한다: 키에서 N 추출 → 필터 선택 → 크기 검증 → MAC → 판정.

    검증에 실패하면 score_cross/score_x/verdict/expected는 None, passed=False,
    reason에 실패 사유가 담긴 dict를 반환한다(예외를 던지지 않음 — 호출자가 다음
    케이스를 계속 처리할 수 있다).
    """
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
    """모든 패턴 케이스를 평가한다. 한 케이스가 FAIL이어도 중단 없이 다음 케이스를 계속 처리한다."""
    return [evaluate_pattern(key, item, filters) for key, item in patterns.items()]
