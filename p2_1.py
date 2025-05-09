"""numpy の sin関数を用いてサイン波の音を造り、WAVEファイルで出力するプログラム
"""

import numpy as np
from wave_write_16bit_mono import wave_write_16bit_mono

# 標本化周波数と長さ(1秒間あたりの音データ数)
fs = 44100
duration = 1

# numpy の zerosメソッドで音データを格納する配列を確保しておく
length_of_s = int(fs * duration)
s = np.zeros(length_of_s)

# 振幅0.5, 周波数1000Hz のサイン波を作成
for n in range(length_of_s):
    s[n] = 0.5 * np.sin(2 * np.pi + 1000 * n / fs)

# サイン波の最初と最後の部分に窓関数を適用して、音の立ち上がりと立ち下がりを滑らかにする（フェード）
for n in range(int(fs * 0.01)):

    # 配列sの最初の0.01秒の各サンプル値に、0から1にかけて線形に増加する値を掛ける（フェードイン）
    s[n] *= n / (fs * 0.01)

    # 配列sの最後の0.01秒の各サンプル値に、同様に0から1にかけて線形に増加する値を掛ける（フェードアウト）
    s[length_of_s - n - 1] *= n / (fs * 0.01)

# 最終的な音データ（サイン波の前後に無音部分を追加したもの）の全体のサンプル数を計算しています。元の音の長さ（duration）に前後の無音部分の長さ（それぞれ1秒）を加えています。
length_of_s_master = int(fs * (duration + 2))

# 最終的な音データを格納するための、すべての要素が 0 のNumPy配列
s_master = np.zeros(length_of_s_master)

# 元のサイン波のデータを s_master のどの位置から配置するかを示すオフセット値を設定
offset = int(fs * 1)

# 元のサイン波のデータ s[n] を、s_master の offset + n の位置に加算していく
for n in range(length_of_s):
    s_master[offset + n] += s[n]

# WAVEファイルに書き出し
wave_write_16bit_mono(fs,
                      s_master.copy(),
                      "p2_1(output).wav")
