# 動画再生関数
# 動画ファイルのパスを引数に取り、動画を再生する関数
# 使用例：play_video.play_video("sample_video.mp4")

import cv2 as cv

def video_player(queue):    # 常駐し、動画再生/停止をメインプロセスからの命令で行う
    playing = False
    while True:
        if not queue.empty():  # 命令があれば確認する
            cmd = queue.get()  # メインプロセスからの命令を確認
            if cmd["type"] == "play_video" and cmd["video_file"] != "" and not playing:  # 動画再生命令
                cap = cv.VideoCapture(cmd["video_file"])    #指定されたパスの動画
                playing = True  # 再生中

            elif playing and cmd["type"] == "stop": # 再生中に停止命令で動画終了
                cap.release()
                cv.destroyWindow("Frame")
                playing = False

            elif cmd["type"] == "exit":     # プロセス終了命令でbreak
                break

        if playing:  # 再生命令から停止命令の間繰り返す
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:    # 動画の終わりまできたら終了
                    cap.release()
                    cv.destroyWindow("Frame")
                    playing = False
                else:
                    cv.imshow("Frame", frame)   # 動画再生(フレームで)
                    if cv.waitKey(int(500 / cap.get(cv.CAP_PROP_FPS))) & 0xFF == ord('q'):
                        cap.release()
                        cv.destroyWindow("Frame")
                        playing = False



# def play_video(video_path):
#     cap = cv.VideoCapture(video_path)
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             break
#         cv.imshow("Frame", frame)
#         if cv.waitKey(int(500/cap.get(cv.CAP_PROP_FPS))) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv.destroyWindow("Frame")