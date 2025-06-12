# Baby Smart Monitoring System

A Raspberry Pi-based baby smart monitoring system that includes bed height control, heart rate detection, and video monitoring functions to comprehensively monitor the baby's status and support real-time interaction with frontend mobile applications.

## Features

- **Bed Height Control**: Control bed height through Arduino, with Raspberry Pi forwarding control commands
- **Heart Rate Monitoring**: Connect to heart rate sensors through Arduino to monitor baby's heart rate in real-time
- **Video Monitoring**: Provide real-time video streaming through a camera connected to the Raspberry Pi
- **Frontend Interaction**: Provide API interfaces and WebSocket connections for interaction with React Native frontend applications

## System Architecture

- `app.py`: Main application entry point
- `config/`: Configuration files directory
- `modules/`: Functional modules directory
  - `arduino/`: Arduino communication modules
    - `base_controller.py`: Basic serial communication controller
    - `bed_controller.py`: Bed controller
    - `heart_rate_controller.py`: Heart rate monitoring controller
    - `controller.py`: Arduino master controller (Facade pattern)
  - `camera/`: Camera modules (video monitoring)
- `api/`: API service modules
  - `server.py`: API server main class
  - `endpoints/`: REST API endpoints
    - `bed.py`: Bed control API
    - `heart_rate.py`: Heart rate monitoring API
    - `video.py`: Video monitoring API
    - `system.py`: System information API
  - `websocket/`: WebSocket event handling
    - `bed.py`: Bed control WebSocket events
    - `heart_rate.py`: Heart rate monitoring WebSocket events
    - `video.py`: Video monitoring WebSocket events
- `utils/`: Utility function modules
- `arduino_sketch/`: Arduino code
  - `baby_monitor_arduino.ino`: Code to upload to Arduino

## Installation Guide

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment:
   Create a `.env` file referring to `.env.example`

3. Start the application:
   ```
   python app.py
   ```

## Various Running Modes

The project provides command-line options to run in various modes.

### 1. Start the Complete System (Default)

Start the complete system with all modules (Arduino, camera, API server) enabled.

```bash
python3 app.py
```

### 2. Test Camera Module Only

Start only the camera without initializing other system components and display the feed in a local debug window. This mode is useful for quickly testing camera hardware and basic capture functionality.

```bash
python3 app.py --only-camera
```

### 3. Start System Without Arduino (Camera and API Server Only)

Start the system (camera, API server) excluding the Arduino controller. Useful when Arduino is not connected or when you don't need to test those functions.

```bash
python3 app.py --no-arduino
```

### 4. Start Complete System with Local Camera Debug Window

Start the complete system and additionally open a debug window showing the camera feed on the local screen. Helps to directly monitor the same feed that is being streamed through the API.

```bash
python3 app.py --debug-camera
```

You can also customize the window name:
```bash
python3 app.py --debug-camera --debug-window-name "My Camera Feed"
```

### 5. AI Face Detection Control

AI face detection features can be enabled/disabled by default through the `enable_ai_face_detection` setting in the `config/config.json` file.

You can override this setting using command-line arguments:

- **Start with AI face detection enabled:**
  ```bash
  python3 app.py --enable-face-detection
  ```
  (Enables AI along with the complete system. Can be combined with other flags like `--debug-camera` or `--no-arduino`.)

- **Start with AI face detection disabled:**
  ```bash
  python3 app.py --disable-face-detection
  ```

**Example combination:** Start the system without Arduino, open a local camera debug window, and force-enable AI face detection:
```bash
python3 app.py --no-arduino --debug-camera --enable-face-detection
```

## Hardware Connections

- Arduino: Connected to Raspberry Pi via USB, controlling bed motors and heart rate sensors
- Camera: Raspberry Pi Camera Module 3 Standard, connected directly to Raspberry Pi USB port or using CSI camera interface

## API Documentation

The system provides complete REST API and WebSocket API. For details, refer to:

- [API Reference Documentation (Chinese)](docs/api_reference_zh.md)
- [API Reference Documentation (Korean)](docs/api_reference_ko.md)
- [API Reference Documentation (English)](docs/api_reference_en.md)

## Development Guide

Detailed installation and development guides:

- [Setup Guide (Chinese)](docs/setup_guide_zh.md)
- [Setup Guide (Korean)](docs/setup_guide_ko.md)
- [Setup Guide (English)](docs/setup_guide_en.md)

## License

MIT 

## Troubleshooting

If you encounter issues with the system, here are some helpful tools for diagnosing problems:

### Testing the Arduino Communication

Use the `arduino_test_direct.py` script to test direct communication with the Arduino:

```bash
python arduino_test_direct.py --port /dev/ttyACM0 --baud 9600
```

This will send a series of test commands to the Arduino and display the responses.

### Testing the API Endpoints

To test if the API server is working correctly, use the `test_frontend_api.py` script:

```bash
python test_frontend_api.py --host localhost --port 5000 --test-websocket
```

This script will test all the HTTP API endpoints and WebSocket connections.

### Testing the Frontend Integration

A simple HTML-based test interface is provided to test frontend integration:

1. Start the API server:
   ```bash
   python app.py
   ```

2. Open the `test_frontend.html` file in a web browser
3. Enter the API host and port (default: localhost:5000)
4. Click "Connect" to test the API and WebSocket connections
5. Use the bed control buttons to test API commands

If the frontend tests work but your actual frontend application is having issues, the problem may be related to:

- CORS configuration
- API endpoint format mismatches
- WebSocket connection parameters
- Network connectivity between your frontend and the Raspberry Pi

Check the browser developer console for detailed error messages that can help identify the specific issue.

---

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

## 다양한 실행 모드

프로젝트는 다양한 모드로 실행할 수 있는 명령줄 옵션을 제공합니다.

### 1. 전체 시스템 시작 (기본값)

모든 모듈(Arduino, 카메라, API 서버)을 활성화하여 전체 시스템을 시작합니다.

```bash
python3 app.py
```

### 2. 카메라 모듈만 테스트

다른 시스템 구성 요소를 초기화하지 않고 카메라만 시작하고 로컬 디버그 창에 화면을 표시합니다. 이 모드는 카메라 하드웨어 및 기본 캡처 기능을 빠르게 테스트하는 데 유용합니다.

```bash
python3 app.py --only-camera
```

### 3. Arduino 없이 시스템 시작 (카메라 및 API 서버)

Arduino 컨트롤러를 제외한 시스템(카메라, API 서버)을 시작합니다. Arduino가 연결되지 않았거나 해당 기능을 테스트할 필요가 없을 때 유용합니다.

```bash
python3 app.py --no-arduino
```

### 4. 로컬 카메라 디버그 창 활성화하여 전체 시스템 시작

전체 시스템을 시작하고 로컬 화면에 카메라 피드를 표시하는 디버그 창을 추가로 엽니다. API를 통해 스트리밍되는 것과 동일한 화면을 로컬에서 직접 모니터링하는 데 도움이 됩니다.

```bash
python3 app.py --debug-camera
```

창 이름을 사용자 지정할 수도 있습니다:
```bash
python3 app.py --debug-camera --debug-window-name "내 카메라 피드"
```

### 5. AI 얼굴 인식 제어

AI 얼굴 인식 기능은 `config/config.json` 파일의 `enable_ai_face_detection` 설정을 통해 기본적으로 활성화/비활성화할 수 있습니다.

명령줄 인수를 사용하여 이 설정을 재정의할 수 있습니다:

- **AI 얼굴 인식 활성화하여 시작:**
  ```bash
  python3 app.py --enable-face-detection
  ```
  (전체 시스템과 함께 AI를 활성화합니다. `--debug-camera` 또는 `--no-arduino`와 같은 다른 플래그와 결합할 수 있습니다.)

- **AI 얼굴 인식 비활성화하여 시작:**
  ```bash
  python3 app.py --disable-face-detection
  ```

**예시 조합:** Arduino 없이 시스템을 시작하고, 로컬 카메라 디버그 창을 열고, AI 얼굴 인식을 강제로 활성화합니다:
```bash
python3 app.py --no-arduino --debug-camera --enable-face-detection
```

## 하드웨어 연결

- 아두이노: USB를 통해 라즈베리파이에 연결, 침대 모터와 심박수 센서 제어
- 카메라: Raspberry Pi Camera Module 3 Standard, 라즈베리파이 USB 포트에 직접 연결하거나 CSI 카메라 인터페이스 사용

## API 문서

시스템은 완전한 REST API와 WebSocket API를 제공합니다. 자세한 내용은 다음을 참조하세요:

- [API 참조 문서 (중국어)](docs/api_reference_zh.md)
- [API 참조 문서 (한국어)](docs/api_reference_ko.md)
- [API 참조 문서 (영어)](docs/api_reference_en.md)

## 개발 가이드

자세한 설치 및 개발 가이드:

- [설치 가이드 (중국어)](docs/setup_guide_zh.md)
- [설치 가이드 (한국어)](docs/setup_guide_ko.md)
- [설치 가이드 (영어)](docs/setup_guide_en.md)

## 라이선스

MIT 

## Troubleshooting

If you encounter issues with the system, here are some helpful tools for diagnosing problems:

### Testing the Arduino Communication

Use the `arduino_test_direct.py` script to test direct communication with the Arduino:

```bash
python arduino_test_direct.py --port /dev/ttyACM0 --baud 9600
```

This will send a series of test commands to the Arduino and display the responses.

### Testing the API Endpoints

To test if the API server is working correctly, use the `test_frontend_api.py` script:

```bash
python test_frontend_api.py --host localhost --port 5000 --test-websocket
```

This script will test all the HTTP API endpoints and WebSocket connections.

### Testing the Frontend Integration

A simple HTML-based test interface is provided to test frontend integration:

1. Start the API server:
   ```bash
   python app.py
   ```

2. Open the `test_frontend.html` file in a web browser
3. Enter the API host and port (default: localhost:5000)
4. Click "Connect" to test the API and WebSocket connections
5. Use the bed control buttons to test API commands

If the frontend tests work but your actual frontend application is having issues, the problem may be related to:

- CORS configuration
- API endpoint format mismatches
- WebSocket connection parameters
- Network connectivity between your frontend and the Raspberry Pi

Check the browser developer console for detailed error messages that can help identify the specific issue. 