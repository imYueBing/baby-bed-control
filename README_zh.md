# 婴儿智能监控系统 (Baby Smart Monitoring System)

基于树莓派的婴儿智能监控系统，包含床体升降控制、心率检测和视频监控功能，实现对婴儿状态的全面监控，并支持与前端移动应用的实时交互。

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

## 硬件连接

- Arduino：通过USB连接到树莓派，控制床体电机和心率传感器
- 摄像头：直接连接到树莓派USB端口或使用CSI摄像头接口

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