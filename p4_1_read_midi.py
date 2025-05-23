import numpy as np
from wave_write_16bit_mono import wave_write_16bit_mono
import MIDI_file

def sine_wave(fs, note_number, velocity, gate):
    """実際に音を生成してWAVEファイルとして出力するものです。
    MIDIデータは音符の情報を表すだけで、それ自体は音を持たないため、
    このスクリプトはMIDIの情報を解釈してサイン波を生成し、それを合成することで音を作り出します。
    """
    length_of_s = int(fs * gate)
    s = np.zeros(length_of_s)
    f = 440 * np.power(2, (note_number -69) / 12)
    for n in range(length_of_s):
        s[n] = np.sin(2 * np.pi * f * n / fs)

    for n in range(int(fs * 0.01)):
        s[n] *= n / (fs * 0.01)
        s[length_of_s - n - 1] *= n / (fs * 0.01)

    gain = velocity / 127 / np.max(np.abs(s))
    s *= gain
    return s

division, tempo, number_of_track, end_of_track, score = MIDI_file.decode("canon.mid")

tempo = 60 / (tempo / 1000000)
number_of_track = int(number_of_track - 1)
end_of_track = (end_of_track / division) * (60 / tempo)
number_of_note = score.shape[0]

fs = 44100
length_of_s_master = int(fs * ((end_of_track + 2)))
track = np.zeros((length_of_s_master, number_of_track))
s_master = np.zeros(length_of_s_master)

for i in range(number_of_note):
    j = int(score[i, 0] - 1)
    onset = (score[i, 1] / division) * (60 / tempo)
    note_number = score[i, 2]
    velocity = score[i, 3]
    gate = (score[i, 4] / division) * (60 / tempo)
    s = sine_wave(fs, note_number, velocity, gate)
    length_of_s = len(s)
    offset = int(fs * onset)
    for n in range(length_of_s):
        track[offset + n, j] += s[n]

for j in range(number_of_track):
    for n in range(length_of_s_master):
        s_master[n] += track[n, j]

master_volume = 0.5
s_master /= np.max(np.abs(s_master))
s_master *= master_volume

wave_write_16bit_mono(fs, s_master.copy(), "p4_1(output).wav")
