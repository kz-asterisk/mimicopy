import wave
import struct
import numpy as np
import structlog

_LOGGER = structlog.get_logger()


# TODO: 別モジュール化
# https://github.com/katieshiqihe/music_in_python/blob/main/utils.py#L10-L32
def getPianoNotes():
    """
    Get the frequency in hertz for all keys on a standard piano.
    Returns
    -------
    note_freqs : dict
        Mapping between note name and corresponding frequency.
    """

    # White keys are in Uppercase and black keys (sharps) are in #
    octave = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    base_freq = 440  # Frequency of Note A4
    keys = np.array([x + str(y) for y in range(0, 9) for x in octave])

    # Trim to standard 88 keys
    start = np.where(keys == "A0")[0][0]
    end = np.where(keys == "C8")[0][0]
    keys = keys[start : end + 1]

    note_freqs = dict(
        zip(keys, [2 ** ((n + 1 - 49) / 12) * base_freq for n in range(len(keys))])
    )
    # Rest is R
    note_freqs["R"] = 0.0

    return note_freqs


class Tone:
    def __init__(self):
        self.key = '' 
        self.beat = 0 

class wavGenerator:
    def __init__(self, track1, track2):
        self.track1 = track1
        self.track2 = track2
        self.fname = "song.wav"
        self.ch = 2  # チャンネル数:モノラルなら1，ステレオなら2
        self.width = 2  # サンプル幅(bit深度):バイト数 (1byte=8bit) -> 一般的に16bit
        self.samplerate = 44100  # サンプルレート: -> 44100Hz
        # ex.)16bitの場合であればPCM規格の範囲としては−2の16乗/2 - 1が最大値、つまり32768〜+32767となる
        self.pcm_max_param = ((2 ** (self.width * 8)) / 2) - 1  # bit深度に応じたPCM規格時のMAX値
        self.bpm = 120  # 1分間の四分音符の数


    def _generateSinWave(self, tone, beat):
        note_freqs = getPianoNotes()

        # 1四分音符当たりの秒数を計算(本来的には4なのだが後続処理的に2倍する必要あり(要調査))
        duration = (60 / self.bpm * 4 * 2) * beat

        # 時間軸の点をサンプル数分用意
        time_axis = np.arange(0, self.samplerate * duration)

        freq = (
            note_freqs[tone]
            if tone in note_freqs
            else _LOGGER.warning("some tone is invalid", tone=tone)
        )
        sin_waves_list = np.sin(2 * np.pi * freq * time_axis / self.samplerate)

        return sin_waves_list.tolist()

    def saveAsWave(self, sin_waves):
        wf = wave.Wave_write(self.fname)
        wf.setparams(
            (
                self.ch,
                self.width,
                self.samplerate,
                len(sin_waves),
                "NONE",
                "not compressed",
            )
        )

        # bitレートに応じたPCM規格化
        max_num = self.pcm_max_param / max(sin_waves)
        standardized_sin_waves = [int(x * max_num) for x in sin_waves]

        # byteデータへ変換
        data = struct.pack("h" * len(sin_waves), *standardized_sin_waves)

        wf.writeframes(data)
        wf.close()

    def orchestrateMelody(self):
        # # TIPS: song = song + song2 とするとappendとなる、songの後にsong2の音が鳴る
        # song = np.array(song) + np.array(song2)

        track1_waves = []
        for note in self.track1:
            track1_waves += self._generateSinWave(*note)

        track2_waves = []
        for note in self.track2:
            track2_waves += self._generateSinWave(*note)

        orchestrated_melody = np.array(track1_waves) + np.array(track2_waves)

        return orchestrated_melody


def main():
    track1 = [
        ["E4", 1 / 8],
        ["F#4", 1 / 8],
        ["G#4", 1 / 8],
        ["E4", 1 / 8],
        ["F#4", 1 / 8],
        ["G#4", 1 / 8],
        ["A4", 1 / 8],
        ["F#4", 1 / 8],
        ["G#4", 1 / 8],
        ["A4", 1 / 8],
        ["B4", 1 / 8],
        ["C#5", 1 / 8],
        ["B4", 1 / 4],
        ["R", 1 / 4],
        ["B4", 1 / 8],
        ["G#4", 1 / 8],
        ["B4", 1 / 8],
        ["G#4", 1 / 8],
        ["A4", 1 / 8],
        ["F#4", 1 / 8],
        ["A4", 1 / 8],
        ["F#4", 1 / 8],
        ["G#4", 1 / 8],
        ["E4", 1 / 8],
        ["F#4", 1 / 8],
        ["D#4", 1 / 8],
        ["E4", 1 / 4],
        ["E5", 1 / 2],
    ]

    track2 = [
        ["E4", 1 / 8],
        ["R", 1 / 8],
        ["D#4", 1 / 8],
        ["R", 1 / 8],
        ["F#4", 1 / 8],
        ["R", 1 / 8],
        ["E4", 1 / 8],
        ["R", 1 / 8],
        ["B4", 1 / 8],
        ["R", 1 / 8],
        ["A4", 1 / 8],
        ["R", 1 / 8],
        ["F#4", 1 / 4],
        ["R", 1 / 4],
        ["G#4", 1 / 2],
        ["F#4", 1 / 2],
        ["B4", 1 / 8],
        ["R", 1 / 8],
        ["A4", 1 / 8],
        ["R", 1 / 8],
        ["G#4", 3 / 4],
    ]

    wg = wavGenerator(track1, track2)
    song = wg.orchestrateMelody()
    wg.saveAsWave(song)


if __name__ == "__main__":
    main()
