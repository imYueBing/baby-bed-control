# 아기 스마트 모니터링 시스템 - 설치 가이드

이 문서는 아기 스마트 모니터링 시스템의 설치 및 구성 가이드를 제공합니다.

## 하드웨어 요구사항

### 라즈베리파이
- Raspberry Pi 4 Model B(권장) 또는 Raspberry Pi 3 Model B+
- 최소 16GB SD 카드
- 5V/3A 전원 어댑터
- 방열판 및 팬 사용 권장

### 아두이노
- Arduino Uno/Nano/Mega 중 하나
- USB 케이블(라즈베리파이와 아두이노 연결용)

### 카메라
- 라즈베리파이 공식 카메라 모듈 또는 USB 카메라
- 카메라 마운트(선택 사항)

### 침대 제어
- 스텝 모터(드라이버 포함, A4988 등)
- 리밋 스위치 2개
- 점퍼 와이어

### 심박수 모니터링
- 심박수 센서 모듈(MAX30102 등)
- 점퍼 와이어

## 소프트웨어 설치

### 라즈베리파이 설정

1. 최신 Raspberry Pi OS 설치:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Python 종속성 설치:
   ```bash
   pip install -r requirements.txt
   ```

3. 카메라 활성화(라즈베리파이 카메라 모듈 사용 시):
   ```bash
   sudo raspi-config
   ```
   "Interface Options" > "Camera" > "Yes" 선택

### 아두이노 설정

1. Arduino IDE 설치
2. ArduinoJson 라이브러리 설치:
   - Arduino IDE 열기
   - "Tools" > "Manage Libraries..." 선택
   - "ArduinoJson"을 검색하고 최신 버전 설치
3. 아두이노 코드 업로드:
   - `arduino_sketch/baby_monitor_arduino.ino` 열기
   - 아두이노를 컴퓨터에 연결
   - 올바른 아두이노 보드와 포트 선택
   - "Upload" 버튼을 클릭하여 코드 업로드

## 하드웨어 연결

### 아두이노 배선

1. 스텝 모터 드라이버 연결:
   - STEP을 아두이노 핀 3에 연결
   - DIR을 아두이노 핀 4에 연결
   - EN을 아두이노 핀 5에 연결
   - GND를 아두이노 GND에 연결
   - VCC를 외부 전원에 연결

2. 리밋 스위치 연결:
   - 상한 리밋 스위치를 아두이노 핀 8에 연결
   - 하한 리밋 스위치를 아두이노 핀 9에 연결
   - 두 스위치의 다른 쪽 끝을 GND에 연결

3. 심박수 센서 연결:
   - 센서 출력을 아두이노 A0 핀에 연결
   - VCC를 아두이노 3.3V 또는 5V에 연결(센서 요구사항에 따라)
   - GND를 아두이노 GND에 연결

### 카메라 연결

- 라즈베리파이 카메라: CSI 포트를 통해 라즈베리파이에 연결
- USB 카메라: 라즈베리파이의 USB 포트에 삽입

## 시스템 구성

### 구성 파일

1. 구성 파일 생성:
   ```bash
   cp config/config.json.example config/config.json
   ```

2. 시스템 설정에 맞게 구성 파일 편집:
   ```bash
   nano config/config.json
   ```

3. 환경 변수 설정(선택 사항):
   ```bash
   cp .env.example .env
   nano .env
   ```

### 시스템 구조

시스템은 모듈식 설계를 채택하여 다음과 같은 주요 구성 요소를 포함합니다:

1. **아두이노 제어 모듈** (`modules/arduino/`)
   - 기본 컨트롤러 (`base_controller.py`): 아두이노와의 기본 직렬 통신 처리
   - 침대 컨트롤러 (`bed_controller.py`): 침대 높이 제어 전용
   - 심박수 컨트롤러 (`heart_rate_controller.py`): 심박수 모니터링 전용
   - 메인 컨트롤러 (`controller.py`): 퍼사드 패턴을 사용하여 모든 기능 통합

2. **API 서비스 모듈** (`api/`)
   - API 서버 (`server.py`): HTTP 및 WebSocket 서비스 제공
   - REST API 엔드포인트 (`endpoints/`): 모든 REST API 인터페이스 포함
   - WebSocket 처리 (`websocket/`): 모든 WebSocket 이벤트 처리 포함

3. **카메라 모듈** (`modules/camera/`)
   - 비디오 스트림 및 스냅샷 기능 제공

4. **유틸리티 함수** (`utils/`)
   - 일반 도구 및 보조 함수 제공

### 자동 시작

라즈베리파이 시작 시 시스템이 자동으로 실행되도록 설정:

1. 서비스 파일 생성:
   ```bash
   sudo nano /etc/systemd/system/baby-monitor.service
   ```

2. 다음 내용 추가:
   ```
   [Unit]
   Description=Baby Monitoring System
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/baby-bed-control/app.py
   WorkingDirectory=/path/to/baby-bed-control
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. 서비스 활성화:
   ```bash
   sudo systemctl enable baby-monitor.service
   sudo systemctl start baby-monitor.service
   ```

## 문제 해결

### 직렬 포트 연결 문제

라즈베리파이가 아두이노와 통신할 수 없는 경우:

1. USB 연결 확인
2. 아두이노 장치 경로 확인:
   ```bash
   ls -l /dev/tty*
   ```
3. 구성 파일에서 아두이노 포트 업데이트
4. 아두이노 드라이버가 설치되어 있는지 확인:
   ```bash
   sudo apt install arduino-core
   ```

### 카메라 문제

카메라가 작동하지 않는 경우:

1. 카메라 연결 확인
2. 카메라가 활성화되어 있는지 확인:
   ```bash
   vcgencmd get_camera
   ```
3. 다른 카메라 애플리케이션으로 테스트:
   ```bash
   raspistill -o test.jpg
   ```

### API 서비스 문제

API 서비스가 시작되지 않는 경우:

1. 포트가 사용 중인지 확인:
   ```bash
   sudo netstat -tuln | grep 5000
   ```
2. 방화벽 설정 확인:
   ```bash
   sudo ufw status
   ```
3. 수동으로 시작하고 오류 확인:
   ```bash
   python app.py
   ```

### 시스템 실행 확인

1. 서비스 상태 확인:
   ```bash
   sudo systemctl status baby-monitor.service
   ```

2. 로그 확인:
   ```bash
   tail -f baby_monitor.log
   ```

3. API 테스트:
   ```bash
   curl http://localhost:5000/api/status
   ```

4. 브라우저에서 비디오 스트림 액세스:
   ```
   http://<라즈베리파이 IP주소>:5000/api/video/stream
   ``` 