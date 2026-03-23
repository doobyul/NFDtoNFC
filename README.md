# Hangul Filename Fixer (NFD → NFC)

Windows에서 Apple 기기(macOS / iOS / iPadOS)에서 생성된 **NFD 한글 파일명**을 자동으로 **NFC 파일명**으로 바꿔주는 상주 유틸리티입니다.

예)

- `한글.txt` → `한글.txt`

---

## 주요 기능

- 사용자 폴더(`%USERPROFILE%`) 기반 파일 감시
- 생성/이동/수정 이벤트 감지 후 파일명 정규화
- 디바운스 처리 (`debounce_ms`)
- 파일 크기/mtime 안정화 확인 후 rename
- 충돌 시 skip + 로그 기록
- rename 루프 방지(자체 rename 이벤트 무시)
- 시스템 트레이 메뉴
  - 감시 일시중지/재개
  - 지금 전체 검사
  - 최근 로그 보기
  - 시작프로그램 등록/해제
  - 종료

---

## 프로젝트 구조

```text
NFDtoNFC/
  src/
    main.py
    watcher.py
    normalizer.py
    renamer.py
    config.py
    tray.py
    utils.py
  config/
    config.default.json
  assets/
    icon.ico
  logs/
  README.md
  LICENSE
  requirements.txt
  build_exe.bat
```

---

## 설치

```bash
pip install -r requirements.txt
```

---

## 실행

### 기본 실행 (트레이)

```bash
python src/main.py
```

### 시작 시 전체 검사 1회 수행

```bash
python src/main.py --scan-now
```

### 콘솔 모드(트레이 없이)

```bash
python src/main.py --no-tray
```

---

## 설정 파일

기본 경로: `config/config.default.json`

```json
{
  "watch_roots": ["%USERPROFILE%"],
  "recursive": true,
  "process_directories": false,
  "debounce_ms": 1000,
  "retry_count": 5,
  "retry_delay_ms": 700,
  "conflict_mode": "skip",
  "excluded_paths": [
    "AppData\\Local\\Temp",
    "AppData\\Local\\Packages",
    ".git",
    "node_modules"
  ]
}
```

---

## 로그 파일

- 로그는 `logs/` 폴더에 저장됩니다.
- 실행 **세션마다 별도 파일**로 생성됩니다.
- 파일명 형식:

```text
NFDtoNFC-log-yymmdd-hhmmss.log
```

예)

```text
NFDtoNFC-log-260312-191533.log
```

트레이 메뉴의 **"최근 로그 보기"** 는 현재 실행 세션 로그를 우선 열고,
없으면 가장 최신 로그 파일을 엽니다.

---

## EXE 빌드

Windows CMD에서:

```bat
build_exe.bat
```

산출물은 `dist/` 폴더에 생성됩니다.

### 버전/빌드 번호 정책

- 현재 초기 버전(Initial Release): `v1.0.0`
- 앱 버전: 루트의 `VERSION` 파일 (예: `1.0.0`)
- 빌드 번호: 루트의 `BUILD_NUMBER` 파일

`build_exe.bat` 실행 시:
1) `BUILD_NUMBER`가 자동으로 1 증가
2) exe 파일명이 아래 형식으로 생성

```text
NFDtoNFC-v<version>-b<build>.exe
```

예)

```text
dist/NFDtoNFC-v1.0.0-b12.exe
```

---

## 보안/동작 원칙

- 관리자 권한 불필요
- 드라이버 설치 없음
- 네트워크 통신 없음
- 파일 **내용** 변경 없음
- 파일 **이름(rename)** 만 수행

---

## 라이선스

MIT License
