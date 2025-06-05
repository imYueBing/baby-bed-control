import serial
import time

def init_serial(port="/dev/ttyUSB0", baudrate=9600, timeout=2):
    return serial.Serial(port, baudrate, timeout=timeout)

def send_command(ser, command):
    ser.write((command + '\n').encode('utf-8'))
    print(f"[SEND] {command}")

def read_response(ser, timeout=2):
    start = time.time()
    responses = []
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                responses.append(line)
    return responses

# 示例用法
if __name__ == "__main__":
    ser = init_serial("/dev/ttyUSB0")  # 替换成你的串口设备名

    try:
        send_command(ser, "UP")
        time.sleep(0.5)
        response = read_response(ser)
        print("[RESPONSE]", response)

        send_command(ser, "GET_HEART_RATE")
        time.sleep(0.5)
        response = read_response(ser)
        print("[RESPONSE]", response)

    except KeyboardInterrupt:
        print("程序中止")
    finally:
        ser.close()
