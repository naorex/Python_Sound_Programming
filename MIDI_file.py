"""MIDIファイルを読み込み、その内容を解析して、楽譜データ（score）を抽出する。
MIDIファイルは音楽情報をデジタル形式で保存するための標準フォーマットで、
このスクリプトは、MIDIファイルのバイナリデータをバイト単位で読み解き、
時間、音符番号、ベロシティ（音の強さ）、ゲート（音の長さ）といった音楽イベントを抽出する。
演奏に最低限必要な情報のみを読み取るモジュールとしている。
"""

import numpy as np

def read_variable_length_data(data, offset):
    """この関数は、MIDIファイル内で頻繁に使用される可変長データを読み取るためのものです。
    MIDIファイルでは、時間差（デルタタイム）などの値が可変長の形式でエンコードされており、
    この関数はそのバイト列をデコードして整数値と、そのデータが占めるバイト数を返します。
    可変長データは、各バイトの最上位ビット（MSB）が1の場合はデータが続くことを示し、
    0の場合はそのバイトでデータが終了することを示します。
    """
    d = 0
    n = 0
    while 1:
        if data[offset + n] >= 0x80:
            d = (d << 7) + data[offset + n] - 0x80
            n += 1
        else:
            d = (d << 7) + data[offset + n]
            n += 1
            break
    return d, n


def decode(file_name):
    """ファイルの読み込みと初期オフセット設定:
    指定されたMIDIファイルをバイナリモードで開き、全バイトを読み込みます。
    その後、MIDIファイルのヘッダーチャンク（MThd）の固定長部分をスキップするためにオフセットを初期化します。
    """
    file = open(file_name, "rb")
    data = file.read()
    file.close

    offset = 0
    offset += 4 # MThd
    offset += 4 # data size

    format_type = (data[8] << 8) + data[11]
    number_of_track = (data[10] << 8) + data[11]
    division = (data[12] << 8) + data[13]
    offset += 6

    note = np.zeros((256, 3), dtype = int)
    score = np.empty(0, dtype = int)
    end_of_track = 0
    i = 0

    for j in range(number_of_track):
        offset += 4 # MTrk

        MTrk_size = 0
        for n in range(4):
            MTrk_size = (MTrk_size << 8) + data[offset + n]

        offset += 4

        end_of_data = offset + MTrk_size
        time = 0
        m = 0
        while offset < end_of_data:
            delta_time, n = read_variable_length_data(data, offset)
            offset += n
            time += delta_time

            if data[offset] == 0xFF: # meta event
                type = 16
                offset += 1
            elif data[offset] >= 0xF0: # system exclusive message
                type = 15
                offset += 1
            elif data[offset] >= 0xE0: # pitch bend
                type = 14
                channel = data[offset] & 0x0F
                offset += 1
            elif data[offset] >= 0xD0: # channel pressure
                type = 13
                channel = data[offset] & 0x0F
                offset += 1
            elif data[offset] >= 0xC0: # program change
                type = 12
                channel = data[offset] & 0x0F
                offset += 1
            elif data[offset] >= 0xB0: # control change
                type = 11
                channel = data[offset] & 0x0F
                offset += 1
            elif data[offset] >= 0xA0: # polyphonic key pressure
                type = 10
                channel = data[offset] & 0xF0
                offset += 1
            elif data[offset] >= 0x90: # note on
                type = 9
                channel = data[offset] & 0xF0
                offset += 1
            elif data[offset] >= 0x80: # note off
                type = 8
                channel = data[offset] & 0xF0
                offset += 1
            if type == 16:
                if data[offset] == 0x51:
                    tempo = 0
                    for n in range(3):
                        tempo = (tempo << 8) + data[offset + 2 + n]

                    offset += 5

                elif data[offset] == 0x2F and data[offset + 1] == 0x00:
                    if time > end_of_track:
                        end_of_track = time

                    offset += 2

                else:
                    d, n = read_variable_length_data(data, offset + 1)
                    offset += 1 + n + d

            elif type == 15:
                d, n = read_variable_length_data(data, offset)
                offset += n + d
            elif type == 14:
                offset += 2
            elif type == 13:
                offset += 1
            elif type == 12:
                program_number = data[offset]
                offset += 1
            elif type == 11:
                offset += 2
            elif type == 10:
                offset += 2
            elif type == 9 or type == 8:
                note_number = data[offset]
                velocity = data[offset + 1]
                if type == 9 and velocity > 0:
                    m = np.mod(m + 1, 256)
                    note[m, 0] = time
                    note[m, 1] = note_number
                    note[m, 2] = velocity
                else:
                    for m in range(256):
                        if note[m, 1] == note_number:
                            break

                    score = np.append(score, j) # track
                    score = np.append(score, note[m, 0]) # onset
                    score = np.append(score, note[m, 1]) # note_number
                    score = np.append(score, note[m, 2]) # velocity
                    score = np.append(score, time - note[m, 0]) # gate
                    i += 1

                    note[m, 0] = 0
                    note[m, 1] = 0
                    note[m, 2] = 0

                offset += 2

    score = score.reshape(i, 5)

    return division, tempo, number_of_track, end_of_track, score
