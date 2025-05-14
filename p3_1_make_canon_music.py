import numpy as np
from wave_write_16bit_mono import wave_write_16bit_mono

def sine_wave(fs, f, a, duration):
    """指定されたパラメータを持つ正弦波を生成

    Args:
        fs (_type_): サンプリング周波数
        f (_type_): 周波数
        a (_type_): 振幅
        duration (_type_): 長さ

    Returns:
        Numpy Array: _description_
    """

    # numpy の zerosメソッドで音データを格納する配列を確保しておく
    length_of_s = int(fs * duration)
    s = np.zeros(length_of_s)

    # サイン波を作成
    for n in range(length_of_s):
        s[n] = np.sin(2 * np.pi * f * n / fs)

    # フェード処理
    for n in range(int(fs * 0.01)):
        s[n] *= n / (fs * 0.01)
        s[length_of_s - n - 1] *= n / (fs * 0.01)

    # 正弦波の最大振幅に基づいてゲインを計算し、指定された振幅 a になるように調整
    gain = a / np.max(np.abs(s))

    # 計算したゲインを正弦波の各サンプルに適用
    s *= gain

    return s

score = np.array([[1, 2, 659.26, 0.5, 1],
                  [1, 3, 587.33, 0.5, 1],
                  [1, 4, 523.25, 0.5, 1],
                  [1, 5, 493.88, 0.5, 1],
                  [1, 6, 440.00, 0.5, 1],
                  [1, 7, 392.00, 0.5, 1],
                  [1, 8, 440.00, 0.5, 1],
                  [1, 9, 493.88, 0.5, 1],
                  [2, 2, 261.63, 0.5, 1],
                  [2, 3, 196.00, 0.5, 1],
                  [2, 4, 220.00, 0.5, 1],
                  [2, 5, 164.81, 0.5, 1],
                  [2, 6, 174.61, 0.5, 1],
                  [2, 7, 130.81, 0.5, 1],
                  [2, 8, 174.61, 0.5, 1],
                  [2, 9, 196.00, 0.5, 1]])

tempo = 120
number_of_track = 2
end_of_track = (4 + 16) * (60 / tempo) # 4+16拍で、テンポ120なので、(4+16) * (60/120) = 10秒
number_of_note = score.shape[0]

fs = 44100

# マスターとなる音声データの配列の長さを計算（曲の長さ + 2秒分の余裕）
length_of_s_master = int(fs * (end_of_track + 2))
track = np.zeros((length_of_s_master, number_of_track))
s_master = np.zeros(length_of_s_master)

# 楽譜データの各音符について処理
for i in range(number_of_note):
    j = int(score[i, 0] -1) # トラック番号を取得します（0から始まるインデックスに変換）
    onset = score[i, 1] # 音の開始タイミング（拍）を取得
    f = score[i, 2]
    a = score[i, 3]
    duration = score[i, 4]
    s = sine_wave(fs, f, a, duration)
    length_of_s = len(s)
    offset = int(fs * onset) # 音の開始位置をサンプル単位で計算

    # 生成した正弦波を、対応するトラックの適切な位置に加算
    for n in range(length_of_s):
        track[offset + n, j] += s[n]

# 各トラックの音声データを s_master に加算してミックス
for j in range(number_of_track):
    for n in range(length_of_s_master):
        s_master[n] += track[n, j]

master_volume = 0.5
s_master /= np.max(np.abs(s_master)) # 音声データを正規化（最大値が1になるように）
s_master *= master_volume # マスターボリュームを適用

# 出力
wave_write_16bit_mono(fs, s_master.copy(), "p3_1(output).wav")
