# 心率API问题修复指南

## 问题描述

心率API请求(`/api/heart-rate`)失败，而床控制功能正常工作。Arduino代码使用`[HEART]`和`[BPM]`格式输出心率，而Python后端可能无法识别这些格式。

## 解决方案

我们已经修改了Python后端代码，使其能够识别多种心率数据格式，包括您的Arduino代码使用的`[HEART]`和`[BPM]`格式。

## 测试步骤

1. **测试Arduino心率通信**

   ```bash
   python test_arduino_heart_rate.py --port /dev/ttyACM0 --baud 9600 --debug
   ```

   这将直接测试Arduino是否能够正确响应心率请求。确认Arduino能够返回心率数据，并且格式是`[HEART] 数值`或`[BPM] 数值`。

2. **测试HTTP心率API**

   ```bash
   python test_http_heart_rate.py --host localhost --port 5000 --iterations 5
   ```

   这将测试HTTP API是否能够正确获取和返回心率数据。

## 常见问题和解决方案

### 1. Arduino不返回心率数据

确认以下几点：
- 心率传感器连接正确
- Arduino代码中的`getHeartRate()`函数正确返回当前心率
- 串口通信波特率设置正确（9600）

### 2. Python后端无法识别Arduino返回的心率格式

我们已经修改了`heart_rate_controller.py`文件，使其能够识别以下格式：
- `HEART_RATE_DATA:数值`
- `[BPM] 数值`
- `[HEART] 数值`
- `HEART=数值`（在状态响应中）

如果您使用了其他格式，请修改`heart_rate_controller.py`文件中的`_handle_specific_response`方法，添加对应的格式处理代码。

### 3. 心率值为零或为空

如果Arduino返回的心率值为零或为空，可能是因为：
- 心率传感器未检测到有效信号
- 传感器连接松动或不正确
- 传感器位置不合适

请检查传感器连接和位置，确保它能够正确检测心率。

### 4. API请求超时

如果API请求超时，可能是因为：
- Arduino响应时间过长
- 串口通信出现问题

尝试增加API请求的超时时间，或者优化Arduino代码以更快地响应请求。

## 修改的文件

1. `modules/arduino/heart_rate_controller.py`
   - 添加了对`[HEART]`和`[BPM]`格式的支持
   - 增加了对`HEART=`格式的支持（用于状态响应）
   - 添加了更多调试日志

2. `test_arduino_heart_rate.py`
   - 添加了对多种心率格式的支持
   - 增加了详细的测试输出

3. `test_http_heart_rate.py`
   - 创建了专门测试HTTP心率API的脚本

## 结论

通过这些修改，Python后端应该能够正确识别Arduino返回的心率数据，使心率API正常工作。如果您仍然遇到问题，请查看日志输出，可能会提供更多关于问题原因的信息。 