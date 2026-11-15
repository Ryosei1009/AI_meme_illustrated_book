# 音声再生関数
# 音声ファイルのパスを引数に取り、音声を再生する関数
# 使用例：play_sound.play_sound("sample_sound.mp3")

import pygame
import time

def sound_player(queue):    # 常駐し、動画再生/停止をメインプロセスからの命令で行う
    playing = False
    while True:
        if not queue.empty():  # 命令があれば確認する
            cmd = queue.get()  # メインプロセスからの命令を確認
            if cmd["type"] == "play_sound" and cmd["sound_file"] != "" and not playing:  # 動画再生命令
                pygame.mixer.init()
                pygame.mixer.music.load(cmd["sound_file"])    #指定されたパスの動画
                pygame.mixer.music.play()
                playing = True  # 再生中

            elif playing and cmd["type"] == "stop": # 再生中に停止命令で動画終了
                pygame.mixer.quit()
                playing = False

            elif cmd["type"] == "exit":     # プロセス終了命令でbreak
                break




def play_sound(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)