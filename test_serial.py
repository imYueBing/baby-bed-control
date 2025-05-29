import serial
import time

# !! 重要 !! 将此处的 PORT 和 BAUDRATE 修改为您实际用于 minicom 并成功连接的值
PORT = "/dev/ttyUSB0"  # 或者您的 Arduino 实际端口，例如 /dev/ttyACM0
BAUDRATE = 9600
TIMEOUT = 1

print(f"尝试连接到端口: {PORT}，波特率: {BAUDRATE}")

try:
    # 尝试不同的 dsrdtr 设置
    print("尝试连接 (默认 dsrdtr)...")
    ser = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
    print(f"连接成功 (默认 dsrdtr)! 端口: {ser.name}")
    ser.close()
    print("连接已关闭。")

except serial.SerialException as e:
    print(f"连接失败 (默认 dsrdtr): {e}")
except Exception as ex:
    print(f"发生意外错误 (默认 dsrdtr): {ex}")

print("-" * 30)

try:
    print("尝试连接 (dsrdtr=False)...")
    ser = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT, dsrdtr=False)
    print(f"连接成功 (dsrdtr=False)! 端口: {ser.name}")
    # 可选：等待 Arduino 重启 (如果它会因为打开连接而重启)
    # print("等待2秒让 Arduino 重启...")
    # time.sleep(2)
    # ser.flushInput()
    # print("尝试发送 'test'...")
    # ser.write(b"test\n")
    # response = ser.readline().decode().strip()
    # print(f"收到响应: {response}")
    ser.close()
    print("连接已关闭。")

except serial.SerialException as e:
    print(f"连接失败 (dsrdtr=False): {e}")
except Exception as ex:
    print(f"发生意外错误 (dsrdtr=False): {ex}")

print("-" * 30)

try:
    print("尝试连接 (dsrdtr=True)...") # 有些板子可能明确需要 DTR
    ser = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT, dsrdtr=True)
    print(f"连接成功 (dsrdtr=True)! 端口: {ser.name}")
    ser.close()
    print("连接已关闭。")

except serial.SerialException as e:
    print(f"连接失败 (dsrdtr=True): {e}")
except Exception as ex:
    print(f"发生意外错误 (dsrdtr=True): {ex}")
