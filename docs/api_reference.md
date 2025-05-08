# 婴儿智能监控系统 - API参考文档

本文档提供婴儿智能监控系统的API接口参考，包括HTTP REST API和WebSocket API。

## 基础信息

- **基础URL**: `http://<树莓派IP地址>:5000`
- **内容类型**: 所有API请求和响应均使用JSON格式
- **认证**: 目前版本不包含认证机制

## REST API

### 系统状态

#### 获取系统状态

```
GET /api/status
```

获取系统的整体状态，包括床体高度、心率、摄像头状态等。

**响应示例**:

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

#### 获取系统信息

```
GET /api/system/info
```

获取系统详细信息，包括平台、资源使用情况等。

**响应示例**:

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

### 床体控制

#### 升高床

```
POST /api/bed/up
```

开始升高床体。

**响应示例**:

```json
{
  "status": "ok",
  "message": "已开始升高床"
}
```

#### 降低床

```
POST /api/bed/down
```

开始降低床体。

**响应示例**:

```json
{
  "status": "ok",
  "message": "已开始降低床"
}
```

#### 停止床体移动

```
POST /api/bed/stop
```

停止床体移动。

**响应示例**:

```json
{
  "status": "ok",
  "message": "已停止床体移动"
}
```

#### 获取床体高度

```
GET /api/bed/height
```

获取当前床体高度。

**响应示例**:

```json
{
  "status": "ok",
  "bed_height": 45,
  "message": "获取床体高度成功"
}
```

### 心率监测

#### 获取心率

```
GET /api/heart-rate
```

获取当前心率数据。

**响应示例**:

```json
{
  "status": "ok",
  "heart_rate": 120,
  "timestamp": "2023-07-01T12:34:56.789Z",
  "message": "获取心率成功"
}
```

### 视频监控

#### 获取视频快照

```
GET /api/video/snapshot
```

获取当前视频帧的JPEG图像。

**响应**: JPEG图像数据（Content-Type: image/jpeg）

#### 获取视频流

```
GET /api/video/stream
```

获取MJPEG视频流。

**响应**: MJPEG流（Content-Type: multipart/x-mixed-replace; boundary=frame）

#### 控制视频录制

```
POST /api/video/recording
```

开始或停止视频录制。

**请求参数**:

```json
{
  "action": "start",  // 或 "stop"
  "output_dir": "videos"  // 可选，输出目录
}
```

**响应示例（开始录制）**:

```json
{
  "status": "ok",
  "action": "start",
  "message": "开始录制视频"
}
```

**响应示例（停止录制）**:

```json
{
  "status": "ok",
  "action": "stop",
  "message": "停止录制视频"
}
```

## WebSocket API

WebSocket接口提供实时数据更新和事件通知，连接URL为：`ws://<树莓派IP地址>:5000/socket.io/`。

### 事件

#### 连接事件

客户端连接后将收到欢迎消息：

```json
{
  "message": "已连接到婴儿监控系统"
}
```

#### 床体控制

**发送**:

```json
{
  "action": "up"  // 或 "down", "stop"
}
```

**接收**:

```json
{
  "status": "ok",
  "action": "up",
  "message": "床体up操作成功"
}
```

#### 请求状态更新

**发送**:

```json
// 空对象，无需参数
{}
```

**接收**:

```json
{
  "status": "ok",
  "bed_height": 45,
  "heart_rate": 120,
  "camera_active": true,
  "recording": false,
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

#### 心率更新

当有新的心率数据时，服务器会自动发送：

```json
{
  "heart_rate": 122,
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

#### 请求视频帧

**发送**:

```json
// 空对象，无需参数
{}
```

**接收**:

```json
{
  "status": "ok",
  "frame": "base64编码的JPEG图像数据",
  "timestamp": "2023-07-01T12:34:56.789Z"
}
```

## 错误处理

所有API可能返回以下错误响应：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

常见错误状态码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 示例使用

### 使用cURL发送HTTP请求

```bash
# 获取系统状态
curl http://raspberrypi:5000/api/status

# 升高床
curl -X POST http://raspberrypi:5000/api/bed/up

# 获取视频快照并保存为图像
curl http://raspberrypi:5000/api/video/snapshot > snapshot.jpg
```

### 使用JavaScript连接WebSocket

```javascript
// 使用Socket.IO客户端库
const socket = io('http://raspberrypi:5000');

// 连接事件
socket.on('connect', () => {
  console.log('已连接到服务器');
});

// 接收欢迎消息
socket.on('welcome', (data) => {
  console.log(data.message);
});

// 接收心率更新
socket.on('heart_rate_update', (data) => {
  console.log(`心率: ${data.heart_rate} BPM`);
});

// 发送床体控制命令
function moveBedUp() {
  socket.emit('bed_control', { action: 'up' });
}

// 接收床体控制响应
socket.on('bed_control_response', (data) => {
  console.log(`床体控制: ${data.message}`);
});

// 请求视频帧
function requestVideoFrame() {
  socket.emit('request_video_frame');
}

// 接收视频帧
socket.on('video_frame', (data) => {
  if (data.status === 'ok') {
    // 显示Base64编码的图像
    document.getElementById('video').src = `data:image/jpeg;base64,${data.frame}`;
  }
});
```

## 响应状态码

所有API响应包含以下状态：

- `ok`: 请求成功处理
- `error`: 请求处理失败 