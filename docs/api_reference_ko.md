# 아기 스마트 모니터링 시스템 - API 참조 문서

이 문서는 아기 스마트 모니터링 시스템의 API 인터페이스 참조를 제공하며, HTTP REST API와 WebSocket API를 포함합니다.

## 기본 정보

- **기본 URL**: `http://<라즈베리파이 IP주소>:5000`
- **콘텐츠 유형**: 모든 API 요청 및 응답은 JSON 형식 사용
- **인증**: 현재 버전에는 인증 메커니즘이 포함되어 있지 않음

## REST API

### 시스템 상태

#### 시스템 상태 가져오기

```
GET /api/status
```

침대 높이, 심박수, 카메라 상태 등을 포함한 시스템의 전체 상태를 가져옵니다.

**응답 예시**:

```json
{
  "status": "ok",
  "timestamp": "2023-07-01T12:34:56.789Z",
  "bed_height": 45,
  "heart_rate": 120,
  "camera_active": true,
  "recording": false
}
```

#### 시스템 정보 가져오기

```
GET /api/system/info
```

플랫폼, 리소스 사용 상황 등을 포함한 시스템 상세 정보를 가져옵니다.

**응답 예시**:

```json
{
  "status": "ok",
  "system": {
    "platform": "Linux-5.10.103-v7l-armv7l-with-debian-11.3",
    "python_version": "3.9.2",
    "hostname": "raspberrypi"
  },
  "resources": {
    "cpu_percent": 15.2,
    "memory_percent": 42.8,
    "disk_percent": 38.6
  },
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

### 침대 제어

#### 침대 올리기

```
POST /api/bed/up
```

침대 올리기를 시작합니다.

**응답 예시**:

```json
{
  "status": "ok",
  "action": "up",
  "message": "침대 올리기 시작됨"
}
```

#### 침대 내리기

```
POST /api/bed/down
```

침대 내리기를 시작합니다.

**응답 예시**:

```json
{
  "status": "ok",
  "action": "down",
  "message": "침대 내리기 시작됨"
}
```

#### 침대 이동 멈추기

```
POST /api/bed/stop
```

침대 이동을 멈춥니다.

**응답 예시**:

```json
{
  "status": "ok",
  "action": "stop",
  "message": "침대 이동 중지됨"
}
```

#### 침대 높이 가져오기

```
GET /api/bed/height
```

현재 침대 높이를 가져옵니다.

**응답 예시**:

```json
{
  "status": "ok",
  "bed_height": 45,
  "message": "침대 높이 가져오기 성공"
}
```

### 심박수 모니터링

#### 심박수 가져오기

```
GET /api/heart-rate
```

현재 심박수 데이터를 가져옵니다.

**응답 예시**:

```json
{
  "status": "ok",
  "heart_rate": 120,
  "timestamp": "2023-07-01T12:34:56.789Z",
  "message": "심박수 가져오기 성공"
}
```

### 비디오 모니터링

#### 비디오 스냅샷 가져오기

```
GET /api/video/snapshot
```

현재 비디오 프레임의 JPEG 이미지를 가져옵니다.

**응답**: JPEG 이미지 데이터 (Content-Type: image/jpeg)

#### 비디오 스트림 가져오기

```
GET /api/video/stream
```

MJPEG 비디오 스트림을 가져옵니다.

**응답**: MJPEG 스트림 (Content-Type: multipart/x-mixed-replace; boundary=frame)

#### 비디오 녹화 제어

```
POST /api/video/recording
```

비디오 녹화 시작 또는 중지.

**요청 매개변수**:

```json
{
  "action": "start",  // 또는 "stop"
  "output_dir": "videos"  // 선택 사항, 출력 디렉토리
}
```

**응답 예시 (녹화 시작)**:

```json
{
  "status": "ok",
  "action": "start",
  "message": "비디오 녹화 시작"
}
```

**응답 예시 (녹화 중지)**:

```json
{
  "status": "ok",
  "action": "stop",
  "message": "비디오 녹화 중지"
}
```

## WebSocket API

WebSocket 인터페이스를 통해 실시간 데이터 푸시 및 양방향 통신을 구현할 수 있습니다. WebSocket 연결 URL은 다음과 같습니다:

```
ws://<라즈베리파이 IP주소>:5000/socket.io
```

### 연결 및 상태 이벤트

#### 연결 이벤트

클라이언트가 성공적으로 연결되면 서버가 환영 메시지를 보냅니다.

**서버 이벤트**: `welcome`

**데이터 형식**:
```json
{
  "message": "아기 모니터링 시스템에 연결됨"
}
```

### 침대 제어 이벤트

#### 침대 제어 명령 보내기

**클라이언트 이벤트**: `bed_control`

**전송 데이터**:
```json
{
  "action": "up"  // 또는 "down", "stop"
}
```

#### 침대 제어 응답

**서버 이벤트**: `bed_control_response`

**데이터 형식**:
```json
{
  "status": "ok",  // 또는 "error"
  "action": "up",  // 또는 "down", "stop"
  "message": "침대 up 작업 성공"  // 작업 및 결과에 따라 변경
}
```

#### 침대 상태 업데이트

**서버 이벤트**: `bed_status_update`

**데이터 형식**:
```json
{
  "bed_height": 45,
  "status": "ok"
}
```

### 심박수 모니터링 이벤트

#### 심박수 데이터 요청

**클라이언트 이벤트**: `request_heart_rate`

**전송 데이터**: 데이터 전송 필요 없음

#### 심박수 데이터 업데이트

**서버 이벤트**: `heart_rate_update`

**데이터 형식**:
```json
{
  "heart_rate": 120,
  "timestamp": "2023-07-01T12:34:56.789Z",
  "status": "ok"
}
```

### 비디오 모니터링 이벤트

#### 비디오 프레임 요청

**클라이언트 이벤트**: `request_video_frame`

**전송 데이터**: 데이터 전송 필요 없음

#### 비디오 프레임 수신

**서버 이벤트**: `video_frame`

**데이터 형식**:
```json
{
  "frame": "base64로 인코딩된 JPEG 데이터",
  "status": "ok"
}
```

#### 비디오 녹화 제어

**클라이언트 이벤트**: `start_recording`

**전송 데이터**:
```json
{
  "output_dir": "videos"  // 선택 사항
}
```

**클라이언트 이벤트**: `stop_recording`

**전송 데이터**: 데이터 전송 필요 없음

#### 녹화 상태 업데이트

**서버 이벤트**: `recording_status`

**데이터 형식**:
```json
{
  "status": "ok",
  "action": "start",  // 또는 "stop"
  "recording": true,  // 또는 false
  "message": "비디오 녹화 시작"  // 또는 "비디오 녹화 중지"
}
```

### 오류 처리

오류가 발생하면 서버가 오류 이벤트를 보냅니다.

**서버 이벤트**: `error`

**데이터 형식**:
```json
{
  "message": "오류 메시지"
}
``` 