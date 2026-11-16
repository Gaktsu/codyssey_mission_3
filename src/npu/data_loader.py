"""모드 2: data.json 로드, 키(size_N_idx) 파싱, 필터 선택, 스키마/크기 검증(케이스 단위 FAIL)."""
import json

from npu.judge import normalize_label

FILTER_SIZES = (5, 13, 25)


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
