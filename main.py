# カメラから入力されたフレームの画像を用いて、特定のポーズ判定をする

# import =======================================
import cv2
import time
from multiprocessing import Process, Queue
import pose_detect
from object_detect import object_detect
from play_video import video_player
from play_sound import sound_player


# ==============================================

def select_camera(): # カメラを選択する関数だが、ここではデフォルトのカメラを使用するように設定
    #cam_id = input("使用するカメラIDを入力してください（通常は0）: ")
    return 0 #int(cam_id)


def main():
    camera_id = select_camera()
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"カメラ {camera_id} を開けませんでした。")
        return

    print("ESCキーで終了します。")

    queue_v = Queue() # プロセス間通信のキュー
    queue_s = Queue() # プロセス間通信のキュー
    video_process = Process(
        target = video_player,  # play_video.py の
        args=(queue_v,)
    )
    sound_process = Process(
        target=sound_player,  # play_video.py の
        args=(queue_s,)
    )
    video_process.start()
    sound_process.start()

    frame_rate = 15             # 一秒間のmediapipe検知回数
    T = 1/frame_rate            # 周期(インターバル)
    t0 = 0
    pose_detector = pose_detect.Pose_detector(queue_v,queue_s)    # 検知用クラス
    detect_time = 0

    while True: # カメラからフレームを取得して処理するループ
        if  time.time()-t0 < T: # 周期ぶんの時間が経過するまで待つ
            continue
        t0 = time.time()

        ret, frame = cap.read()  # フレームを読み込む
        if not ret:  # フレームが取得できなかった場合
            return

        pose_detector.single_frame_detect(frame)
        if time.time() - detect_time >5.0:
            detect_time = object_detect(frame,queue_v,queue_s)

        key = cv2.waitKey(1)    # キー入力を待つ
        if key == 27:           # ESCキーが押されたら終了
            break

    cap.release() # カメラを解放
    cv2.destroyAllWindows() # ウィンドウを閉じる

    queue_v.put({"type":"exit"})     # 終了命令
    queue_s.put({"type":"exit"})     # 終了命令

if __name__ == '__main__':
    main()

