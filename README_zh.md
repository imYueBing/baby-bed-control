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