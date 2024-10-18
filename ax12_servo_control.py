import serial
import time

# シリアルポートの設定（U2D2用）
SERIAL_PORT = '/dev/ttyUSB0'  # U2D2のポート
BAUDRATE = 115200  # 確認されたボーレート

# AX-12のID
SERVO_ID = 5  # デフォルトのIDは1ですが、必要に応じて変更してください

# パケットヘッダー
HEADER = bytes([0xFF, 0xFF])

# 命令セット
INST_PING = 0x01
INST_READ = 0x02
INST_WRITE = 0x03

def calculate_checksum(packet):
    return (~sum(packet) & 0xFF)

def send_packet(servo_id, instruction, params=None):
    if params is None:
        params = []
    length = len(params) + 2
    packet = [servo_id, length, instruction] + params
    checksum = calculate_checksum(packet)
    packet = HEADER + bytes(packet) + bytes([checksum])
    
    serial_port.write(packet)
    print(f"送信したパケット: {packet.hex()}")
    
    # 応答を待つ
    time.sleep(0.05)
    response = serial_port.read(serial_port.in_waiting or 1)
    print(f"受信した応答: {response.hex()}")

def set_position(servo_id, position):
    print(f"位置 {position} に設定を試みます")
    params = [0x1E, position & 0xFF, (position >> 8) & 0xFF]
    send_packet(servo_id, INST_WRITE, params)

def ping_servo(servo_id):
    send_packet(servo_id, INST_PING)

try:
    # シリアルポートを開く
    serial_port = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=0.1)
    print(f"ポート {SERIAL_PORT} を開きました（ボーレート: {BAUDRATE}）")

    # サーボにPINGを送信
    print("サーボにPINGを送信...")
    ping_servo(SERVO_ID)

    # サーボを動かす
    print("サーボを動かします...")
    for pos in range(0, 1024, 100):  # 0度から300度まで
        set_position(SERVO_ID, pos)
        time.sleep(1)

    for pos in range(1023, -1, -100):  # 300度から0度まで
        set_position(SERVO_ID, pos)
        time.sleep(1)

except serial.SerialException as e:
    print(f"シリアルポートエラー: {e}")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
finally:
    if 'serial_port' in locals() and serial_port.is_open:
        serial_port.close()
        print("シリアルポートを閉じました")