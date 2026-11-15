from ultralytics import YOLO
import time

CONFIG = [
    {
        "model": YOLO("model/shibako.pt"),
        "label": "シバコ",
        "video": "video/shibako.mp4",
        "sound": "sound/shibako.mp3"
    },
]


def object_detect(frame,queue_v,queue_s):
    for config in CONFIG:
        results = config["model"](frame)
        for i in results[0].boxes.conf.tolist():
            if i > 0.9:
                print(f"{config['label']}を検出")
                queue_v.put({"type": "play_video", "video_file": config["video"]})  # 別プロセスに再生命令
                queue_s.put({"type": "play_sound", "sound_file": config["sound"]})
                return time.time()
        return 0