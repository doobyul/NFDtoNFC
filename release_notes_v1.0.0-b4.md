## NFDtoNFC v1.0.0-b4

Windows에서 Apple 기기(macOS/iOS/iPadOS)에서 생성된 NFD 한글 파일명을 NFC로 자동 복구하는 유틸리티입니다.

### 주요 변경사항
- onefile 용량 최적화 (불필요 assets 제외)
- 트레이 fallback 아이콘 로직 경량화
- 필수 의존성 유지 + 배포 안정성 유지

### 배포 파일
- `NFDtoNFC-v1.0.0-b4.exe`

### 보안/서명 안내
- 본 릴리즈는 현재 **코드 서명(디지털 서명) 미적용** 상태입니다.
- Windows SmartScreen에서 "알 수 없는 게시자" 경고가 표시될 수 있습니다.

### SmartScreen 경고 시 실행 방법
1. `추가 정보` 클릭
2. `실행` 클릭

### SHA256
`44026d46c9de2333dd9ff84b328b9ff67fb2a3a32324bb05cf576e47b9972b87`

CMD 검증 명령:
```cmd
certutil -hashfile "c:\VSCode\NFDtoNFC\dist\NFDtoNFC-v1.0.0-b4.exe" SHA256
```
