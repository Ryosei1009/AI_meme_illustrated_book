from abc import abstractmethod
from collections import deque

# 各動作を管理するクラス。これを通して検出したい複数の動作を一括で検知する。
class GestureManager:
    def __init__(self,queue_v,queue_s):
        self.gestures = [
            # 下で定義した動作のクラスをここに追加
            Yoruno_Odoriko(),
            Scuba(),
            HappyHappyHappy(),
            # Jump()
        ]
        self.queue_v = queue_v  # プロセス間通信用キュー
        self.queue_s = queue_s  # プロセス間通信用キュー
        self.current_detect = None     # 前回の検知結果を保持する。連続検知防止用 兼 動画強制終了用

    def update(self,landmarks):
        for gesture in self.gestures:
            gesture.update(landmarks)

    def get_detect(self):
        now = None
        for gesture in self.gestures:
            if gesture.detected:    # 何かしら検知されたら
                now = type(gesture).__name__  # 検知結果
                if now != self.current_detect: # 前回と異なる検知結果なら
                    self.queue_v.put({"type": "stop"})  # 別プロセスに動画停止命令(再生されてなければ無視される)
                    self.queue_v.put({"type":"play_video", "video_file":gesture.video_file}) # 別プロセスに再生命令
                    self.queue_s.put({"type": "stop"})  # 別プロセスに動画停止命令(再生されてなければ無視される)
                    self.queue_s.put({"type":"play_sound", "sound_file":gesture.sound_file}) # 別プロセスに再生命令
                break   # 一種類検知されたら終わり

        if now is None and self.current_detect is not None: # 前回は検知されたが、今回何も検知されなかったなら (= 連続動作が途切れたら)
            self.queue_v.put({"type": "stop"})  # 別プロセスに動画停止命令(再生されてなければ無視される)
            self.queue_s.put({"type": "stop"})  # 別プロセスに動画停止命令(再生されてなければ無視される)
        self.current_detect = now   # 今回の検知結果で更新
        return now  # 検知結果を返す


# 各動作の親クラス(abstract)
class Gesture:
    @abstractmethod
    def update(self,landmarks):     # 最新フレームのランドマークから判定に必要な値を履歴に追加し、判定を行うメソッド
        pass

# ====================================================================
# ここで各動作をクラスとして定義する。
# 必要な要素1: 親クラスのメソッドのオーバーライド
# 必要な要素2: 判定に使う過去フレームの値を記録するデック。updateで更新される。
#           " self.history = depue(maxlen=保持する過去フレーム数) "
# 必要な要素3: 検知したときにTrueになるフラグ。
#           " self.detected = False "
# 必要な要素4: 検知したときに再生する動画のパス、再生しないなら""とする
#           " self.video_file = "" "
# ====================================================================
# 簡単な例として "ジャンプ" を定義する。 (判定はかなり雑)
# updateメソッドの中身とhistoryのmaxlen 以外は共通なのでコピペを推奨
class Jump(Gesture):
    def __init__(self):
        self.history = deque(maxlen=15)
        self.detected = False
        self.video_file = ""    # 再生する動画がなければ「""」
        self.sound_file = ""

    def update(self,landmarks):
        self.history.append(landmarks[0].y)   # 鼻のy座標を使うので追加。

        if len(self.history)<15:     # 過去フレームの履歴が十分でなければ判定しない
            return

        movement = max(self.history) - min(self.history)    # 鼻の位置の上下の変動幅, 0.15を超えればジャンプを検出したものとする
        self.detected = (movement > 0.15    # ↓ 履歴の順序(index番号)を比較して、低→高で検出して、高→低の変化では検出しない
                         and self.history.index(max(self.history)) < self.history.index(min(self.history)))

# --------------------------------------------------------------------
class Yoruno_Odoriko(Gesture):
    def __init__(self):
        self.history = deque(maxlen=10)
        self.detected = False
        self.video_file = "video/yoruno_odoriko_v2.mp4"    # 再生する動画
        self.sound_file = "sound/yoruno_odoriko_v2 1.mp3"

    def update(self,landmarks):
        if landmarks[12].y > landmarks[16].y or landmarks[11].y > landmarks[15].y:
            return  # 両手は低い位置
        self.history.append(landmarks[19].x < landmarks[20].x)  # 右手と左手のx座標上の交差を記録

        switched = 0    # 両手が交差したり戻ったりの切り替わり回数をカウント
        before = self.history[0]
        for current in self.history:
            if current != before:
                switched+=1
            before=current

        self.detected = switched >= 2

# --------------------------------------------------------------------
class HappyHappyHappy(Gesture):
    def __init__(self):
        self.history = deque(maxlen=15)
        self.detected = False
        self.video_file = "video/happy.mp4"
        self.sound_file = "sound/happy.mp3"

    def update(self,landmarks):
        self.history.append(landmarks[0].y)  # 鼻のy座標の変化を使う

        if len(self.history) < 15:  # 過去フレームの履歴が十分でなければ判定しない
            return

        movement = max(self.history) - min(self.history)  # 鼻の位置の上下の変動幅, 閾値を超えればジャンプを検出したものとする
        self.detected = (movement > 0.05  # ジャンプの条件に加えて、両手首が両肩より高いとHappyHappyHappy
                         and self.history.index(max(self.history)) < self.history.index(min(self.history))
                         and landmarks[11].y > landmarks[15].y and landmarks[12].y > landmarks[16].y)

# --------------------------------------------------------------------
class Scuba(Gesture):
    def __init__(self):
        self.history = deque(maxlen=10)
        self.detected = False
        self.video_file = "video/scuba.mp4"
        self.sound_file = "sound/scuba.mp3"

    def update(self,landmarks):
        self.history.append("")

        if len(self.history) < 10:  # 過去フレームの履歴が十分でなければ判定しない
            return

        self.detected = (landmarks[12].x < landmarks[15].x < landmarks[11].x
                         and landmarks[0].y < landmarks[19].y < landmarks[12].y and landmarks[14].y > landmarks[16].y)

# ====================================================================
