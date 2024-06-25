import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ASRT')))
try:
    import os
    from ASRT.speech_model import ModelSpeech
    from ASRT.speech_model_zoo import SpeechModel251BN
    from ASRT.speech_features import Spectrogram
    from ASRT.language_model3 import ModelLanguage
except Exception as e:
    print(f'Error: {e}')
class ASRTSpeechRecognition:
    def __init__(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        self.audio_length = 1600
        self.audio_feature_length = 200
        self.channels = 1
        self.output_size = 1428
        self.sm251bn = SpeechModel251BN(
            input_shape=(self.audio_length, self.audio_feature_length, self.channels),
            output_size=self.output_size
        )
        self.feat = Spectrogram()
        self.ms = ModelSpeech(self.sm251bn, self.feat, max_label_length=64)
        self.ms.load_model('../ASRT/save_models/' + self.sm251bn.get_model_name() + '.model.h5')
        self.ml = ModelLanguage('../ASRT/model_language')
        self.ml.load_model()

    def speech_recognition(self, wav_file):
        res = self.ms.recognize_speech_from_file(wav_file)
        print('*[提示] 声学模型语音识别结果：\n', res)
        str_pinyin = res
        res = self.ml.pinyin_to_text(str_pinyin)
        print('语音识别最终结果：\n', res)
        return res