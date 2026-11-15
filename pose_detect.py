# import =======================================
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import gesture
# ==============================================

# 連続で送られてくるフレーム画像から動作の検知を行うするPose_detectorクラス
class Pose_detector:
    def __init__(self,queue_v,queue_s):
        base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')  # モデルのパスを指定
        options = vision.PoseLandmarkerOptions(  # ポーズランドマーカーのオプションを設定
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.gesture_manager = gesture.GestureManager(queue_v,queue_s)      # 動作の検知を管理するクラス
        self.detecting_rate = 3  # 検知回数 n 回に一回の間隔で動作検出を行う。(毎秒15回を分周して毎秒５回)
        self.count = 0  # 1フレームごとにカウントアップする。0からdetecting rateまで


    def draw_landmarks_on_image(self,rgb_image, detection_result):
      pose_landmarks_list = detection_result.pose_landmarks
      annotated_image = np.copy(rgb_image)

      pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
      pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

      for pose_landmarks in pose_landmarks_list:
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=pose_landmarks,
            connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
            landmark_drawing_spec=pose_landmark_style,
            connection_drawing_spec=pose_connection_style)

      return annotated_image

    # フレーム画像から身体の検知、動作の検知を行うメソッド
    def single_frame_detect(self,frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # BGRからRGBに変換
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb) # MediaPipeのImageオブジェクトに変換
        detection_result = self.detector.detect(mp_image) # 検出

        annotated = self.draw_landmarks_on_image(frame_rgb, detection_result) # ランドマークを描画
        vis_image = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR) # RGBからBGRに変換してOpenCVで表示できるようにする
        cv2.imshow("Pose Landmarker", vis_image) # 画像を表示

        if len(detection_result.pose_landmarks)>=1 and self.count >= self.detecting_rate:     # 体が検出されれば、detecting rateの間隔で動作検出
            self.gesture_manager.update(detection_result.pose_landmarks[0]) # 現在フレームで判定用クラスを更新,判定
            detected_gesture = self.gesture_manager.get_detect()     # 判定状況を確認
            if not detected_gesture is None:                    # なんらかの動作が検出されていれば
                print(f"{detected_gesture}を検知")               # 特定動作が検出されたと出力
            self.count = 0
        self.count+=1