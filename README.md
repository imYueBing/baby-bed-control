# 아기 스마트 모니터링 시스템 (Baby Smart Monitoring System)

라즈베리파이 기반 아기 스마트 모니터링 시스템으로, 침대 높이 조절, 심박수 감지 및 비디오 모니터링 기능을 포함하여 아기 상태를 종합적으로 모니터링하고 프론트엔드 모바일 애플리케이션과 실시간 상호작용을 지원합니다.

## 주요 기능

- **침대 높이 제어**: 아두이노를 통해 침대 높이를 제어하고, 라즈베리파이가 제어 명령을 전달
- **심박수 모니터링**: 아두이노를 통해 심박수 센서에 연결하여 아기의 심박수를 실시간으로 모니터링
- **비디오 모니터링**: 라즈베리파이에 연결된 카메라를 통해 실시간 비디오 스트림 제공
- **프론트엔드 상호작용**: API 인터페이스와 WebSocket 연결을 제공하여 React Native 프론트엔드 애플리케이션과 상호작용

## 시스템 구조

- `app.py`: 메인 애플리케이션 진입점
- `config/`: 구성 파일 디렉토리
- `modules/`: 기능 모듈 디렉토리
  - `arduino/`: 아두이노 통신 모듈
    - `base_controller.py`: 기본 직렬 통신 컨트롤러
    - `bed_controller.py`: 침대 컨트롤러
    - `heart_rate_controller.py`: 심박수 모니터링 컨트롤러
    - `controller.py`: 아두이노 마스터 컨트롤러 (퍼사드 패턴)
  - `camera/`: 카메라 모듈 (비디오 모니터링)
- `api/`: API 서비스 모듈
  - `server.py`: API 서버 메인 클래스
  - `endpoints/`: REST API 엔드포인트
    - `bed.py`: 침대 제어 API
    - `heart_rate.py`: 심박수 모니터링 API
    - `video.py`: 비디오 모니터링 API
    - `system.py`: 시스템 정보 API
  - `websocket/`: WebSocket 이벤트 처리
    - `bed.py`: 침대 제어 WebSocket 이벤트
    - `heart_rate.py`: 심박수 모니터링 WebSocket 이벤트
    - `video.py`: 비디오 모니터링 WebSocket 이벤트
- `utils/`: 유틸리티 함수 모듈
- `arduino_sketch/`: 아두이노 코드
  - `baby_monitor_arduino.ino`: 아두이노에 업로드할 코드

## 설치 가이드

1. 종속성 설치:
   ```
   pip install -r requirements.txt
   ```

2. 환경 구성:
   `.env.example`을 참조하여 `.env` 파일 생성

3. 애플리케이션 시작:
   ```
   python app.py
   ```

## 하드웨어 연결

- 아두이노: USB를 통해 라즈베리파이에 연결, 침대 모터와 심박수 센서 제어
- 카메라: Raspberry Pi Camera Module 3 Standard, 라즈베리파이 USB 포트에 직접 연결하거나 CSI 카메라 인터페이스 사용

## API 문서

시스템은 완전한 REST API와 WebSocket API를 제공합니다. 자세한 내용은 다음을 참조하세요:

- [API 참조 문서 (중국어)](docs/api_reference_zh.md)
- [API 참조 문서 (한국어)](docs/api_reference_ko.md)

## 개발 가이드

자세한 설치 및 개발 가이드:

- [설치 가이드 (중국어)](docs/setup_guide_zh.md)
- [설치 가이드 (한국어)](docs/setup_guide_ko.md)

## 라이선스

MIT 