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
  "action": "up",
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
  "action": "down",
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
  "action": "stop",
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

通过WebSocket接口，可以实现实时数据推送和双向通信。连接WebSocket的URL为：

```
ws://<树莓派IP地址>:5000/socket.io
```

### 连接与状态事件

#### 连接事件

客户端成功连接后，服务器会发送欢迎消息。

**服务器事件**: `welcome`

**数据格式**:
```json
{
  "message": "已连接到婴儿监控系统"
}
```

### 床体控制事件

#### 发送床体控制命令

**客户端事件**: `bed_control`

**发送数据**:
```json
{
  "action": "up"  // 或 "down", "stop"
}
```

#### 床体控制响应

**服务器事件**: `bed_control_response`

**数据格式**:
```json
{
  "status": "ok",  // 或 "error"
  "action": "up",  // 或 "down", "stop"
  "message": "床体up操作成功"  // 根据操作和结果变化
}
```

#### 床体状态更新

**服务器事件**: `bed_status_update`

**数据格式**:
```json
{
  "bed_height": 45,
  "status": "ok"
}
```

### 心率监测事件

#### 请求心率数据

**客户端事件**: `request_heart_rate`

**发送数据**: 无需发送数据

#### 心率数据更新

**服务器事件**: `heart_rate_update`

**数据格式**:
```json
{
  "heart_rate": 120,
  "timestamp": "2023-07-01T12:34:56.789Z",
  "status": "ok"
}
```

### 视频监控事件

#### 请求视频帧

**客户端事件**: `request_video_frame`

**发送数据**: 无需发送数据

#### 接收视频帧

**服务器事件**: `video_frame`

**数据格式**:
```json
{
  "frame": "base64编码的JPEG数据",
  "status": "ok"
}
```

#### 控制视频录制

**客户端事件**: `start_recording`

**发送数据**:
```json
{
  "output_dir": "videos"  // 可选
}
```

**客户端事件**: `stop_recording`

**发送数据**: 无需发送数据

#### 录制状态更新

**服务器事件**: `recording_status`

**数据格式**:
```json
{
  "status": "ok",
  "action": "start",  // 或 "stop"
  "recording": true,  // 或 false
  "message": "开始录制视频"  // 或 "停止录制视频"
}
```

### 错误处理

当出现错误时，服务器会发送错误事件

**服务器事件**: `error`

**数据格式**:
```json
{
  "message": "错误信息"
}
``` 