import serial
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATES = [1000000, 115200, 57600, 9600]
ID_RANGE = range(0, 253)  # AX-12のID範囲は0-252

def calculate_checksum(packet):
    return (~sum(packet) & 0xFF)

def send_ping(serial_port, servo_id):
    packet = bytes([0xFF, 0xFF, servo_id, 0x02, 0x01])
    checksum = calculate_checksum(packet[2:])
    packet += bytes([checksum])
    
    serial_port.write(packet)
    print(f"  ID {servo_id} にPINGを送信: {packet.hex()}")
    
    time.sleep(0.01)
    response = serial_port.read(serial_port.in_waiting or 1)
    if response:
        print(f"  ID {servo_id} から応答: {response.hex()}")
    return response

def test_communication():
    found_servos = []

    for baudrate in BAUDRATES:
        print(f"\nボーレート {baudrate} でテスト中...")
        try:
            with serial.Serial(SERIAL_PORT, baudrate=baudrate, timeout=0.1) as ser:
                print(f"ポート {SERIAL_PORT} を開きました")
                for servo_id in ID_RANGE:
                    response = send_ping(ser, servo_id)
                    if response:
                        print(f"成功: ボーレート {baudrate}, サーボID {servo_id} で応答を受信しました。")
                        found_servos.append((baudrate, servo_id))
                    time.sleep(0.01)
        except serial.SerialException as e:
            print(f"エラー: {e}")
        
        time.sleep(0.5)  # 次のボーレートテストの前に少し待つ

    return found_servos

if __name__ == "__main__":
    print("AX-12サーボモーター通信テストとIDスキャンを開始します...")
    found_servos = test_communication()
    
    if found_servos:
        print("\n検出されたサーボ:")
        for baudrate, servo_id in found_servos:
            print(f"ボーレート: {baudrate}, サーボID: {servo_id}")
    else:
        print("\nサーボが検出されませんでした。接続と電源を確認してください。")

    print("\nテスト完了")