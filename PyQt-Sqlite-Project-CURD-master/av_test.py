import os
import sys
import wave
import threading
from os import remove, mkdir, listdir
from datetime import datetime
from time import sleep
import pyaudio
import cv2
from PyQt5.QtWidgets import QApplication
from moviepy.editor import *


class VideoRecorder:
    CHUNK_SIZE = 1024
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    RATE = 16000

    def __init__(self):
        self.audio_filename = 'user_audio.mp3'
        self.webcam_video_filename = 'user_video.avi'
        self.allowRecording = True
        self.flag = False

        self.p = pyaudio.PyAudio()
        self.cap = cv2.VideoCapture(0)
        print("ready")

    def record_audio(self):
        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK_SIZE)
        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        while self.allowRecording:
            data = stream.read(self.CHUNK_SIZE)
            wf.writeframes(data)
        wf.close()
        stream.stop_stream()

    def record_webcam(self):
        aviFile = cv2.VideoWriter(self.webcam_video_filename,
                                  cv2.VideoWriter_fourcc(*'MJPG'),
                                  25, (640, 480))
        while self.allowRecording and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                aviFile.write(frame)
        aviFile.release()

    def start_recording(self, auto_stop_time=0, output_filepath=""):
        try:
            self.allowRecording = True

            t1 = threading.Thread(target=self.record_audio)
            t2 = threading.Thread(target=self.record_webcam)

            event = threading.Event()
            event.clear()

            for t in (t1, t2):
                t.start()

            print('3秒后开始录制，按q键结束录制')
            if auto_stop_time > 0:
                sleep(auto_stop_time)
                print('录制时间已到，自动停止录制')

            else:
                while True:
                    if self.flag == True:
                        break

            self.allowRecording = False
            for t in (t1, t2):
                t.join()

            audio = AudioFileClip(self.audio_filename)
            video = VideoFileClip(self.webcam_video_filename)

            ratio = audio.duration / video.duration
            video = (video.fl_time(lambda t: t / ratio, apply_to=['video'])
                     .set_fps(25)
                     .set_end(audio.duration)
                     .set_position(('right', 'bottom')))
            audio = audio.set_fps(25)
            audio = audio.set_duration(video.duration)
            final_video = CompositeVideoClip([video]).set_audio(audio)
            final_video.write_videofile(output_filepath, codec='libx264', fps=25)

            # remove(self.audio_filename)
            # remove(self.webcam_video_filename)
        except Exception as e:
            print(f'Error: {e}')

    def setflag(self, value):
        self.flag = value

    def close(self):
        self.cap.release()
        self.p.terminate()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pa_no = 0
    trial = 0
    stype = 'w'
    sno = 0

    folder_path = "pa_train/pa_" + str(pa_no) + "/trial_" + str(trial) + "/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filepath = folder_path + stype + str(sno) + ".mp4"

    vr = VideoRecorder()

    # Record the first video
    vr.start_recording(3, filepath)

    # Modify the file path for the second video
    sno = 1
    filepath = folder_path + stype + str(sno) + ".mp4"

    # Record the second video
    vr.start_recording(5, filepath)
    sys.exit(app.exec_())

