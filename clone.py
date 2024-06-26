import os
import re

import soundfile as sf

import numpy as np
from pathlib import Path
from models.synthesizer.inference import Synthesizer
from models.vocoder.hifigan import inference as vocoder
from models.encoder import inference as encoder
from control.toolbox.utterance import Utterance
from pydub import AudioSegment


class MockingbirdInterface:
    def __init__(self):
        synthesizer_model = Path("data/ckpt/synthesizer/ferret_70k.pt")
        vocoder_model = Path("data/ckpt/vocoder/pretrained/g_hifigan.pt")
        encoder_model = Path("data/ckpt/encoder/pretrained.pt")
        self.synthesizer = Synthesizer(synthesizer_model)
        encoder.load_model(encoder_model)
        vocoder.load_model(vocoder_model)

    def generate_audio(self, source_audio, data,pa_no,stype):
        wav = Synthesizer.load_preprocess_wav(source_audio)
        # Compute the mel spectrogram
        spec = Synthesizer.make_spectrogram(wav)
        # Compute the embedding
        encoder_wav = encoder.preprocess_wav(wav)
        embed, partial_embeds, _ = encoder.embed_utterance(encoder_wav, return_partials=True)

        # Add the utterance
        utterance = Utterance("name", "speaker", wav, spec, embed, partial_embeds, False)
        for row in data:
            text=row[0]
            no=row[1]
            filepath="../PyQt-Sqlite-Project-CURD-master/pa_audio/pa"+str(pa_no)+"/"+stype+"/"+str(no)+".wav"
            # Synthesize the mel spectrogram
            texts = text.split("\n")
            punctuation = '！，。、,'  # punctuate and split/clean text
            processed_texts = []
            for text in texts:
                for processed_text in re.sub(r'[{}]+'.format(punctuation), '\n', text).split('\n'):
                    if processed_text:
                        processed_texts.append(processed_text.strip())
            texts = processed_texts
            embeds = [embed] * len(texts)

            specs = self.synthesizer.synthesize_spectrograms(texts, embeds,style_idx=-1,min_stop_token=4,steps=400)
            breaks = [spec.shape[1] for spec in specs]
            spec = np.concatenate(specs, axis=1)

            def vocoder_progress(i, seq_len, b_size, gen_rate):
                real_time_factor = (gen_rate / Synthesizer.sample_rate) * 1000
                line = "Waveform generation: %d/%d (batch size: %d, rate: %.1fkHz - %.2fx real time)" \
                       % (i * b_size, seq_len * b_size, b_size, gen_rate, real_time_factor)
                self.ui.log(line, "overwrite")
                self.ui.set_loading(i, seq_len)
            # Generate the waveform
            wav, sample_rate= vocoder.infer_waveform(spec)
            # Add breaks
            b_ends = np.cumsum(np.array(breaks) * Synthesizer.hparams.hop_size)
            b_starts = np.concatenate(([0], b_ends[:-1]))
            wavs = [wav[start:end] for start, end, in zip(b_starts, b_ends)]
            breaks = [np.zeros(int(0.15 * sample_rate))] * len(breaks)
            wav = np.concatenate([i for w, b in zip(wavs, breaks) for i in (w, b)])
            wav = wav / np.abs(wav).max() * 0.97

            sf.write(filepath, wav, sample_rate)
            # 打开WAV文件
            wav_file = AudioSegment.from_wav(filepath)
            # 将WAV文件转换为MP3并保存到本地
            mp3_file="../PyQt-Sqlite-Project-CURD-master/pa_audio/pa"+str(pa_no)+"/"+stype+"/"+str(no)+".mp3"
            wav_file.export(mp3_file, format='mp3')
            os.remove(filepath)

        return



if __name__ =="__main__":
    mockingbird = MockingbirdInterface()

    source_audio = "../PyQt-Sqlite-Project-CURD-master/audio/sentence/1.mp3"
    text = "啊"
    filepath="../PyQt-Sqlite-Project-CURD-master/pa_audio/pa10.wav"
    generated_audio = mockingbird.generate_audio(source_audio, text,filepath)
    text="哦"
    filepath="../PyQt-Sqlite-Project-CURD-master/pa_audio/pa11.wav"
    generated_audio = mockingbird.generate_audio(source_audio, text,filepath)



