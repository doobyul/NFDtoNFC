## NFDtoNFC v1.0.1-b5

Windows에서 Apple 기기(macOS/iOS/iPadOS)에서 생성된 NFD 한글 파일명을 NFC로 자동 복구하는 유틸리티입니다.

### 주요 변경사항
- 시작프로그램 자동 실행 시 발생하던 로그 경로 권한 오류 수정
  - 기존: 작업 디렉터리(System32) 영향을 받아 `C:\Windows\System32\logs` 접근 시도 가능
  - 개선: 실행 기준 경로(exe 폴더/프로젝트 루트) 기반으로 로그 경로 고정
- 로그 경로 권한 실패 시 `%LOCALAPPDATA%\NFDtoNFC\logs` fallback 추가
- 기본 설정 파일(`config/config.default.json`) 탐색도 CWD 비의존으로 보강

### 배포 파일
- `NFDtoNFC-v1.0.1-b5.exe`

### 보안/서명 안내
- 본 릴리즈는 현재 **코드 서명(디지털 서명) 미적용** 상태입니다.
- Windows SmartScreen에서 "알 수 없는 게시자" 경고가 표시될 수 있습니다.

### SmartScreen 경고 시 실행 방법
1. `추가 정보` 클릭
2. `실행` 클릭

### SHA256
`f1949e8ae86027a43b7c04a1f4fd00af4163f76bed2b49f64296f7f39e062b00`

CMD 검증 명령:
```cmd
certutil -hashfile "c:\VSCode\NFDtoNFC\dist\NFDtoNFC-v1.0.1-b5.exe" SHA256
```
