import serial
import struct
import time
import sys

# シリアルポートの設定
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 115200
SERVO_ID = 5

# AX-12制御クラス
class AX12:
    def __init__(self, serial_port, baudrate=115200, servo_id=1):
        self.serial_port = serial.Serial(serial_port, baudrate, timeout=0.1)
        self.servo_id = servo_id
        self.current_position = 512  # 中央位置（0-1023の範囲の中央）

    def calculate_checksum(self, packet):
        return (~sum(packet) & 0xFF)

    def set_position(self, position):
        # 位置を0-1023の範囲に制限
        position = max(0, min(1023, int(position)))
        
        # 現在の位置と同じ場合は送信しない
        if position == self.current_position:
            return

        # パケットの作成
        params = [0x1E, position & 0xFF, (position >> 8) & 0xFF]
        length = len(params) + 2
        packet = [self.servo_id, length, 0x03] + params
        checksum = self.calculate_checksum(packet)
        packet = bytes([0xFF, 0xFF] + packet + [checksum])
        
        # パケットの送信
        self.serial_port.write(packet)
        print(f"位置を設定: {position}")  # デバッグ用
        self.current_position = position
        time.sleep(0.01)

    def close(self):
        self.serial_port.close()

# ゲームパッド制御クラス
class GamepadController:
    def __init__(self, device_path="/dev/input/js0"):
        self.device_path = device_path
        self.device = None
        
    def open(self):
        self.device = open(self.device_path, 'rb')
        
    def read_event(self):
        try:
            event = self.device.read(8)
            if event:
                return struct.unpack('IhBB', event)
            return None
        except:
            return None
            
    def close(self):
        if self.device:
            self.device.close()

def main():
    try:
        # AX-12の初期化
        print("AX-12を初期化中...")
        ax12 = AX12(SERIAL_PORT, BAUDRATE, SERVO_ID)
        
        # ゲームパッドの初期化
        print("ゲームパッドを初期化中...")
        gamepad = GamepadController()
        gamepad.open()
        
        # 初期位置を中央に設定
        current_position = 512
        ax12.set_position(current_position)
        
        print("\n制御開始:")
        print("- 十字キー左右: モーターを左右に動かす")
        print("- Ctrl+C: プログラム終了")
        
        movement_speed = 10  # 1回の移動量
        
        while True:
            event = gamepad.read_event()
            if event:
                time_ms, value, event_type, number = event
                
                # 十字キーの左右（軸番号6）を検出
                if event_type & 0x02 and number == 6:
                    if value < 0:  # 左
                        current_position = max(0, current_position - movement_speed)
                        ax12.set_position(current_position)
                    elif value > 0:  # 右
                        current_position = min(1023, current_position + movement_speed)
                        ax12.set_position(current_position)
                    
            time.sleep(0.01)  # CPU負荷軽減のための短い待機

    except KeyboardInterrupt:
        print("\nプログラムを終了します")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if 'gamepad' in locals():
            gamepad.close()
        if 'ax12' in locals():
            ax12.close()

if __name__ == "__main__":
    main()