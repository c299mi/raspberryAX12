import struct
import time
import sys

class GamepadTester:
    def __init__(self, device_path="/dev/input/js0"):
        self.device_path = device_path
        print(f"ゲームパッドテスター: {device_path} を使用")

    def test_gamepad(self):
        try:
            with open(self.device_path, 'rb') as device:
                print("ゲームパッドを検出しました")
                print("ボタンを押すか、スティックを動かしてください...")
                print("終了するには Ctrl+C を押してください")
                
                while True:
                    # 8バイトのイベントを読み取る
                    event = device.read(8)
                    if event:
                        # イベントを解析
                        time_ms, value, event_type, number = struct.unpack('IhBB', event)

                        # イベントタイプの判別（ボタンまたは軸）
                        if event_type & 0x01:    # ボタンイベント
                            print(f"\nボタンイベント:")
                            print(f"  ボタン番号: {number}")
                            print(f"  状態: {'押された' if value == 1 else '離された' if value == 0 else str(value)}")
                            print(f"  time: {time_ms}")
                        
                        elif event_type & 0x02:  # 軸イベント
                            print(f"\n軸イベント:")
                            print(f"  軸番号: {number}")
                            print(f"  値: {value}")  # -32767 から 32767 の範囲
                            print(f"  time: {time_ms}")
                        
                        print("-" * 40)

        except KeyboardInterrupt:
            print("\nテストを終了します")
        except FileNotFoundError:
            print(f"エラー: ゲームパッド {self.device_path} が見つかりません")
            print("以下のコマンドでデバイスを確認してください:")
            print("ls /dev/input/js*")
        except Exception as e:
            print(f"エラー: {str(e)}")

def list_input_devices():
    """利用可能な入力デバイスを表示"""
    import subprocess
    
    print("\n利用可能な入力デバイスを検索中...")
    try:
        # ls -l /dev/input/by-id の実行
        result = subprocess.run(['ls', '-l', '/dev/input/by-id'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("\n検出された入力デバイス:")
            print(result.stdout)
        else:
            print("入力デバイスが見つかりません")
        
        # js* デバイスの検索
        result = subprocess.run(['ls', '-l', '/dev/input/js*'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("\nジョイスティックデバイス:")
            print(result.stdout)
        
    except subprocess.SubprocessError:
        print("デバイス情報の取得中にエラーが発生しました")

if __name__ == "__main__":
    # 利用可能なデバイスを表示
    list_input_devices()
    
    # デフォルトのジョイスティックデバイスでテスト開始
    tester = GamepadTester()
    tester.test_gamepad()