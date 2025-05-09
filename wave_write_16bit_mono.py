import numpy as np
from scipy.io import wavfile

def wave_write_16bit_mono(fs, s, file_name):
    """量子化bit を 16bit に設定し、-1 ~ +1 までの実数データを -32768 ~ +32768 までの整数データに変換し、WAVEファイルに保存するモジュール

    Args:
        fs (int): 標本化周波数（sampling rate）
        s (np.array): 書き出し対象の配列
        file_name (str): 書き出す際のファイル名称
    """

    length_of_s = len(s)

    for n in range(length_of_s):

        # -1 ~ +1の範囲にある浮動小数点数の音データ（サイン波の値）を、0 ~ 65536 の範囲の整数に変換
        s[n] = (s[n] + 1) / 2 * 65536

        # 浮動小数点数を四捨五入して整数に変換
        s[n] = int(s[n] + 0.5)

        # 変換後に範囲外になった値のクリップ処理
        if s[n] > 65536:
            s[n] = 65536
        elif s[n] < 0:
            s[n] = 0

        # 0 から 65536 の範囲の整数値を、16ビットの符号付き整数表現である -32768 ~ +32767 の範囲にシフト
        s[n] -= 32768

    # WAVEファイルに書き出し
    wavfile.write(file_name,
                  fs,
                  s.astype(np.int16))
