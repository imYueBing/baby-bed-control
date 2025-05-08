# 婴儿智能监控系统 - 安装指南

本文档提供婴儿智能监控系统的安装和配置指南。

## 硬件要求

### 树莓派
- Raspberry Pi 4 Model B（推荐）或Raspberry Pi 3 Model B+
- 至少16GB SD卡
- 5V/3A电源适配器
- 推荐使用散热器和风扇

### Arduino
- Arduino Uno/Nano/Mega 任一型号
- USB连接线（连接树莓派和Arduino）

### 摄像头
- 树莓派官方摄像头模块或USB摄像头
- 摄像头支架（可选）

### 床体控制
- 步进电机（带驱动器，如A4988）
- 2个限位开关
- 跳线

### 心率监测
- 心率传感器模块（如MAX30102）
- 跳线

## 软件安装

### 树莓派设置

1. 安装最新的Raspberry Pi OS：
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 启用摄像头（如果使用树莓派摄像头模块）：
   ```bash
   sudo raspi-config
   ```
   进入"Interface Options" > "Camera" > 选择"Yes"

### Arduino设置

1. 安装Arduino IDE
2. 安装ArduinoJson库：
   - 打开Arduino IDE
   - 选择"Tools" > "Manage Libraries..."
   - 搜索"ArduinoJson"并安装最新版本
3. 上传Arduino代码：
   - 打开`arduino_sketch/baby_monitor_arduino.ino`
   - 连接Arduino到电脑
   - 选择正确的Arduino板型和端口
   - 点击"Upload"按钮上传代码

## 硬件连接

### Arduino接线

1. 步进电机驱动器连接：
   - STEP连接到Arduino引脚3
   - DIR连接到Arduino引脚4
   - EN连接到Arduino引脚5
   - GND连接到Arduino GND
   - VCC连接到外部电源

2. 限位开关连接：
   - 上限位开关连接到Arduino引脚8
   - 下限位开关连接到Arduino引脚9
   - 两个开关的另一端都连接到GND

3. 心率传感器连接：
   - 传感器输出连接到Arduino A0引脚
   - VCC连接到Arduino 3.3V或5V（根据传感器要求）
   - GND连接到Arduino GND

### 摄像头连接

- 树莓派摄像头：通过CSI端口连接到树莓派
- USB摄像头：插入树莓派的USB端口

## 系统配置

### 配置文件

1. 创建配置文件：
   ```bash
   cp config/config.json.example config/config.json
   ```

2. 编辑配置文件以匹配你的系统设置：
   ```bash
   nano config/config.json
   ```

3. 设置环境变量（可选）：
   ```bash
   cp config/env_sample.txt .env
   nano .env
   ```

### 自动启动

要使系统在树莓派启动时自动运行：

1. 创建服务文件：
   ```bash
   sudo nano /etc/systemd/system/baby-monitor.service
   ```

2. 添加以下内容：
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

3. 启用服务：
   ```bash
   sudo systemctl enable baby-monitor.service
   sudo systemctl start baby-monitor.service
   ```

## 故障排除

### 串口连接问题

如果树莓派无法与Arduino通信：

1. 检查USB连接
2. 确认Arduino设备路径：
   ```bash
   ls -l /dev/tty*
   ```
3. 更新配置文件中的Arduino端口

### 摄像头问题

如果摄像头无法工作：

1. 检查摄像头连接
2. 确认摄像头已启用：
   ```bash
   vcgencmd get_camera
   ```
3. 尝试使用不同的摄像头应用测试：
   ```bash
   raspistill -o test.jpg
   ```

### 验证系统运行

1. 检查服务状态：
   ```bash
   sudo systemctl status baby-monitor.service
   ```

2. 查看日志：
   ```bash
   tail -f logs/baby_monitor_*.log
   ```

3. 测试API：
   ```bash
   curl http://localhost:5000/api/status
   ``` 