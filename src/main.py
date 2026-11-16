"""진입점: 모드 선택, 모드 1 입력(검증·재입력), 결과/요약 출력."""

ROW_ERROR = "입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(line):
    """공백으로 구분된 숫자 3개 줄을 float 리스트로 변환한다. 실패 시 None."""
    parts = line.split()
    if len(parts) != 3:
        return None
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None


def read_row(prompt):
    """유효한 숫자 3개가 입력될 때까지 해당 줄만 다시 입력받는다."""
    while True:
        row = parse_row(input(prompt))
        if row is not None:
            return row
        print(ROW_ERROR)


def read_matrix(label):
    """3×3 행렬을 한 줄(행)씩 입력받는다. 행 하나가 틀리면 그 행만 재입력."""
    print(f"{label} 입력 (한 줄에 3개 숫자, 공백 구분):")
    return [read_row(f"{label} {i + 1}행: ") for i in range(3)]
