## NFDtoNFC v1.0.0-b3

Windows에서 Apple 기기(macOS/iOS/iPadOS)에서 생성된 NFD 한글 파일명을 NFC로 자동 복구하는 유틸리티입니다.

### 주요 변경사항
- NFD -> NFC 파일명 자동 변환 안정화
- 트레이 아이콘 표시/초기화 로직 개선
- 버전/빌드 번호 표기 및 실행파일 속성 버전 정보 반영
- 빌드 파이프라인 정리 및 배포 구조 개선

### 배포 파일
- `NFDtoNFC-v1.0.0-b3.exe`

### 보안/서명 안내
- 본 릴리즈는 현재 **코드 서명(디지털 서명) 미적용** 상태입니다.
- Windows SmartScreen에서 "알 수 없는 게시자" 경고가 표시될 수 있습니다.

### SmartScreen 경고 시 실행 방법
1. `추가 정보` 클릭
2. `실행` 클릭

### SHA256
`1e9f7c53a11f59f4048dd8aafd971387b5d6835b04c69d56317fc9d93133f068`

PowerShell 검증 명령:
```powershell
Get-FileHash -LiteralPath "c:\VSCode\NFDtoNFC\dist\NFDtoNFC-v1.0.0-b3.exe" -Algorithm SHA256
```

CMD 검증 명령:
```cmd
certutil -hashfile "c:\VSCode\NFDtoNFC\dist\NFDtoNFC-v1.0.0-b3.exe" SHA256
```
