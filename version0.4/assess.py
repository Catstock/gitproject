import math
import os
import sys
import speechpy
import numpy as np
import jieba
import difflib

import wavio
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from pydub import AudioSegment
import speech_recognition as sr
import ffmpeg

class AudioAssess(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口大小和标题
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle('中文口语自动评估')

        # 添加标签和文本框
        self.standard_text_edit = QTextEdit('张三是一位大学老师')
        self.standard_audio_edit = QTextEdit('audio/sentence/0.mp3')
        self.user_audio_edit = QTextEdit('pa_audio/pa15/sentence/0.mp3')
        self.user_text_edit = QTextEdit('')# 标红不标准
        self.user_text_edit.setReadOnly(True)
        self.real_user_text_edit = QTextEdit('')# 用户的实际发音
        self.real_user_text_edit.setReadOnly(True)
        # 结果
        self.result_label=QLabel("")
        font = QFont()
        font.setPixelSize(40)
        self.result_label.setFont(font)
        self.user_text_edit.setFont(font)
        self.real_user_text_edit.setFont(font)

        # 添加按钮
        self.evaluate_button = QPushButton('开始评估')
        self.evaluate_button.clicked.connect(self.evaluate)

        # 添加布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.standard_text_edit)
        vbox.addWidget(self.standard_audio_edit)
        vbox.addWidget(self.user_audio_edit)
        vbox.addWidget(self.user_text_edit)
        vbox.addWidget(self.real_user_text_edit)
        vbox.addWidget(self.result_label)
        vbox.addWidget(self.evaluate_button)
        self.setLayout(vbox)

    def evaluate(self):
        try:
            wrong_num=0
            # 加载标准语音和对应的中文
            self.standard_text = self.standard_text_edit.toPlainText()
            standard_audio_file = self.standard_audio_edit.toPlainText()

            # 加载用户发音的音频文件
            user_audio_file = self.user_audio_edit.toPlainText()

            # 加载停用词列表
            stopwords_file = 'stopwords.txt'
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                stopwords = set(f.read().split())

            # 将MP3格式音频转换成wav格式
            self.convert_mp3_to_wav(standard_audio_file, 'standard_audio.wav')
            self.convert_mp3_to_wav(user_audio_file, 'user_audio.wav')
            # 提取标准语音的MFCC特征
            standard_audio = wavio.read('standard_audio.wav')
            standard_mfcc = speechpy.feature.mfcc(standard_audio.data.flatten(), standard_audio.rate)
            # 提取用户发音的MFCC特征
            user_audio = wavio.read('user_audio.wav')
            user_mfcc = speechpy.feature.mfcc(user_audio.data.flatten(), user_audio.rate)
            # 填充MFCC长度
            standard_mfcc, user_mfcc = self.pad_mfcc(standard_mfcc, user_mfcc)

            # 计算MFCC特征之间的欧氏距离
            distances = np.sqrt(np.sum((standard_mfcc - user_mfcc) ** 2, axis=1))

            # 计算平均欧氏距离，用于
            mean_distance = np.mean(distances)

            # 使用结巴分词对中文进行分词
            seg_list = jieba.lcut(self.standard_text)

            # 去除停用词
            seg_list = [word for word in seg_list if word not in stopwords]

            # 根据平均欧氏距离给出相应的评分和反馈
            if mean_distance < 15:
                result_text = '得分：'+str(100-int(mean_distance))+' 发音非常准确！'
            elif mean_distance < 30:
                result_text = '得分：'+str(100-int(mean_distance))+' 发音基本正确，还需继续努力。'
            else:
                result_text = '得分：'+str(100-int(mean_distance))+' 发音有较大误差，需要加强练习。'
            # 更新评估结果和文本框
            self.result_label.setText(result_text)
            # 对用户语音进行语音识别
            # recognizer = sr.Recognizer()
            # with sr.AudioFile('user_audio.wav') as source:
            #     audio = recognizer.record(source)
            #     self.user_text = recognizer.recognize_sphinx(audio, language='zh-CN')
            if not self.standard_text=="":
                from asrt_wrapper import ASRTSpeechRecognition
                asr = ASRTSpeechRecognition()
                # 设置音频长度限制为16秒
                MAX_AUDIO_LENGTH = 15 * 1000  # 单位是毫秒
                # 读取音频文件
                audio_file = AudioSegment.from_wav('user_audio.wav')
                # 计算音频长度
                audio_length = len(audio_file)
                # 如果音频长度小于或等于16秒，则直接进行语音识别
                if audio_length <= MAX_AUDIO_LENGTH:
                    self.user_text = asr.speech_recognition('user_audio.wav')
                else:
                    # 否则，将音频拆分为小于等于16秒的部分并保存到临时文件夹中
                    temp_folder = 'temp_audio'
                    os.makedirs(temp_folder, exist_ok=True)
                    num_parts = math.ceil(audio_length / MAX_AUDIO_LENGTH)
                    for i in range(num_parts):
                        start = i * MAX_AUDIO_LENGTH
                        end = min((i + 1) * MAX_AUDIO_LENGTH, audio_length)
                        part_audio = audio_file[start:end]
                        part_audio.export(f'{temp_folder}/part_{i}.wav', format='wav')

                    # 读取每个拆分后的音频并进行语音识别
                    results = []
                    for i in range(num_parts):
                        part_audio_file = f'{temp_folder}/part_{i}.wav'
                        result = asr.speech_recognition(part_audio_file)
                        results.append(result)
                        # 将结果拼接起来
                        self.user_text = ' '.join(results)
                        # 删除临时文件夹
                        os.system(f'rm -rf {temp_folder}')

                print(self.user_text)
                # 将文本与标准文本进行比较，找出不准确的字
                diff = difflib.SequenceMatcher(None, self.standard_text, self.user_text).get_opcodes()
                sum_num=len(self.standard_text)
                highlighted_text = ''
                for opcode, start1, end1, start2, end2 in diff:
                    if opcode == 'replace':
                        highlighted_text += '<font color="red"><b>'+self.standard_text[start1:end1]+'</b></font>'
                        wrong_num += (end1 - start1)  # 计算被标红的字符的长度
                    elif opcode == 'delete':
                        highlighted_text += '<font color="red"><b>'+self.standard_text[start1:end1]+'</b></font>'
                        wrong_num += (end1 - start1)  # 计算被标红的字符的长度
                    else:
                        highlighted_text += self.standard_text[start1:end1]
                self.user_text_edit.setHtml("红色部分的发音不够准确："+highlighted_text)
                if self.user_text=="":
                    self.real_user_text_edit.setText("声音太轻了！请大声朗读！")
                else:
                    self.real_user_text_edit.setText("用户发音为："+self.user_text)
                return result_text,highlighted_text,wrong_num,sum_num
            else:
                return result_text
        except Exception as e:
            print(f'Error: {e}')

    # 将MP3格式音频转换成wav格式
    def convert_mp3_to_wav(self,input_file, output_file):
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(stream, output_file, format='wav')
        ffmpeg.run(stream, overwrite_output=True)

    def pad_mfcc(self,mfcc1, mfcc2):
        if mfcc1.shape[0] > mfcc2.shape[0]:
            mfcc2 = np.pad(mfcc2, ((0, mfcc1.shape[0] - mfcc2.shape[0]), (0, 0)))
        else:
            mfcc1 = np.pad(mfcc1, ((0, mfcc2.shape[0] - mfcc1.shape[0]), (0, 0)))
        return mfcc1, mfcc2

    def set_file(self,standard_text,standard_file,user_file):
        self.standard_text_edit.setText(standard_text)
        self.standard_audio_edit.setText(standard_file)
        self.user_audio_edit.setText(user_file)
        self.standard_text_edit.hide()
        self.standard_audio_edit.hide()
        self.user_audio_edit.hide()
        self.user_text_edit.setText(standard_text)
        self.evaluate_button.hide()
        if standard_text=="":
            result_text=self.evaluate()
            return result_text
        else:
            result_text,highlighted_text,wrong_num,sum_num=self.evaluate()
            return result_text,highlighted_text,wrong_num,sum_num

    def set_hide(self):
        self.standard_text_edit.hide()
        self.standard_audio_edit.hide()
        self.user_audio_edit.hide()
        self.evaluate_button.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioAssess()
    window.show()
    sys.exit(app.exec_())