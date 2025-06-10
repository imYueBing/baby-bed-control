# 婴儿智能监控系统 (Baby Smart Monitoring System)

基于树莓派的婴儿智能监控系统，包含床体升降控制、心率检测和视频监控功能，实现对婴儿状态的全面监控，并支持与前端移动应用的实时交互。

    python3 app.py --debug-camera

## 功能特点

- **床体升降控制**：通过Arduino控制床体高度，树莓派转发控制指令
- **心率监测**：通过Arduino连接心率传感器，实时监测婴儿心率
- **视频监控**：通过树莓派连接摄像头，提供实时视频流
- **前端交互**：提供API接口和WebSocket连接，与React Native前端应用交互

## 系统架构

- `app.py`：主应用程序入口
- `config/`：配置文件目录
- `modules/`：功能模块目录
  - `arduino/`：Arduino通信模块
    - `base_controller.py`：基础串行通信控制器
    - `bed_controller.py`：床体控制器
    - `heart_rate_controller.py`：心率监测控制器
    - `controller.py`：Arduino主控制器（外观模式）
  - `camera/`：摄像头模块（视频监控）
- `api/`：API服务模块
  - `server.py`：API服务器主类
  - `endpoints/`：REST API端点
    - `bed.py`：床体控制API
    - `heart_rate.py`：心率监测API
    - `video.py`：视频监控API
    - `system.py`：系统信息API
  - `websocket/`：WebSocket事件处理
    - `bed.py`：床体控制WebSocket事件
    - `heart_rate.py`：心率监测WebSocket事件
    - `video.py`：视频监控WebSocket事件
- `utils/`：工具函数模块
- `arduino_sketch/`：Arduino代码
  - `baby_monitor_arduino.ino`：上传到Arduino的代码

## 安装指南

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置环境：
   创建`.env`文件，参考`.env.example`

3. 启动应用：
   ```
   python app.py
   ```

## 多种启动模式

本项目提供了命令行选项，允许以不同模式启动应用。

### 1. 启动完整系统 (默认)

启动所有模块（Arduino、摄像头、API服务器），功能完整。

```bash
python3 app.py
```

### 2. 仅测试摄像头模块

此模式仅启动摄像头，并在本地调试窗口中显示画面，不初始化其他系统组件。这对于快速测试摄像头硬件和基本捕获功能非常有用。

```bash
python3 app.py --only-camera
```

### 3. 无Arduino模式启动 (启动摄像头和API服务器)

启动除Arduino控制器以外的系统组件（摄像头、API服务器）。当Arduino未连接或不需要测试其功能时适用。

```bash
python3 app.py --no-arduino
```

### 4. 启动完整系统并开启本地摄像头调试窗口

启动完整系统，并额外打开一个本地调试窗口显示摄像头实时画面。有助于在本地直接监控通过API流式传输的相同画面。

```bash
python3 app.py --debug-camera
```

您也可以自定义调试窗口的名称：
```bash
python3 app.py --debug-camera --debug-window-name "我的摄像头画面"
```

### 5. 控制AI人脸识别功能

AI人脸识别功能默认是否启用取决于 `config/config.json` 文件中 `enable_ai_face_detection` 的设置。

您可以使用命令行参数覆盖此配置：

- **启动并启用AI人脸识别：**
  ```bash
  python3 app.py --enable-face-detection
  ```
  （这将随完整系统一起启用AI。可以与其他标志如 `--debug-camera` 或 `--no-arduino` 结合使用。）

- **启动并禁用AI人脸识别：**
  ```bash
  python3 app.py --disable-face-detection
  ```

**组合示例：** 以无Arduino模式启动，打开本地摄像头调试窗口，并强制启用AI人脸识别：
```bash
python3 app.py --no-arduino --debug-camera --enable-face-detection
   ```

## 硬件连接

- Arduino：通过USB连接到树莓派，控制床体电机和心率传感器
- 摄像头：Raspberry Pi Camera Module 3 Standard，直接连接到树莓派USB端口或使用CSI摄像头接口

## API文档

系统提供了完整的REST API和WebSocket API，详情请参阅：

- [API参考文档 (中文)](docs/api_reference_zh.md)
- [API参考文档 (韩文)](docs/api_reference_ko.md)

## 开发指南

详细的安装和开发指南：

- [安装指南 (中文)](docs/setup_guide_zh.md)
- [安装指南 (韩文)](docs/setup_guide_ko.md)

## 许可证

MIT 

## 故障排除

如果您遇到系统问题，以下是一些有助于诊断问题的工具：

### 心率功能故障排除

如果您的心率检测功能出现问题，而床控制功能正常工作，请使用以下专用工具进行诊断：

```bash
# 测试Arduino心率通信
python test_arduino_heart_rate.py --port /dev/ttyACM0 --baud 9600 --debug

# 测试HTTP心率API端点 (简化版)
python test_http_heart_rate.py --host localhost --port 5000 --iterations 5

# 测试完整的心率API (包括WebSocket)
python test_heart_rate_api.py --host localhost --port 5000 --iterations 5
```

这些工具会帮助您识别问题所在：

1. 如果`test_arduino_heart_rate.py`成功但`test_http_heart_rate.py`失败，问题可能在于API层。
2. 如果两者都失败，问题可能在于Arduino代码或硬件连接。

常见心率问题的解决方案：

- **Arduino不响应GET_HEART_RATE命令**：确保Arduino代码中正确实现了`sendHeartRate()`函数。
- **心率值始终为空**：检查心率传感器连接和Arduino的模拟引脚配置。
- **前端无法获取心率**：检查网络连接，确保正确处理了API响应格式。

查看我们更新后的代码，它增加了额外的错误处理和日志记录，以帮助诊断和修复心率检测问题。

### 测试Arduino通信

使用 `arduino_test_direct.py` 脚本测试与Arduino的直接通信：

```bash
python arduino_test_direct.py --port /dev/ttyACM0 --baud 9600
```

这将向Arduino发送一系列测试命令并显示响应。

### 测试API端点

要测试API服务器是否正常工作，请使用 `test_frontend_api.py` 脚本：

```bash
python test_frontend_api.py --host localhost --port 5000 --test-websocket
```

此脚本将测试所有HTTP API端点和WebSocket连接。

### 测试前端集成

提供了一个简单的基于HTML的测试界面来测试前端集成：

1. 启动API服务器：
   ```bash
   python app.py
   ```

2. 在Web浏览器中打开 `test_frontend.html` 文件
3. 输入API主机和端口（默认：localhost:5000）
4. 点击"连接"测试API和WebSocket连接
5. 使用床控按钮测试API命令

如果前端测试正常工作但您的实际前端应用程序出现问题，则问题可能与以下相关：

- CORS配置
- API端点格式不匹配
- WebSocket连接参数
- 前端和树莓派之间的网络连接

检查浏览器开发者控制台中的详细错误消息，这些消息可以帮助确定具体问题。