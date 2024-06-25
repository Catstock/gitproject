
from PyQt5.QtWidgets import QApplication

import wave
import threading
from os import remove, mkdir, listdir
from datetime import datetime
from time import sleep
import pyaudio
import cv2
from moviepy.editor import *


class VideoRecorder:
    CHUNK_SIZE = 1024
    CHANNELS = 2
    FORMAT = pyaudio.paInt16
    RATE = 16000

    def __init__(self):
        self.now = str(datetime.now())[:19].replace(':', '_')
        self.audio_filename = 'user_audio.mp3'
        self.webcam_video_filename = 'user_video.avi'
        self.allowRecording = True
        self.flag=False

    def record_audio(self):
        p = pyaudio.PyAudio()
        #sleep(3)
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK_SIZE)
        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        while self.allowRecording:
            data = stream.read(self.CHUNK_SIZE)
            wf.writeframes(data)
        wf.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def record_webcam(self):
        cap = cv2.VideoCapture(0)
        #sleep(3)
        aviFile = cv2.VideoWriter(self.webcam_video_filename,
                                  cv2.VideoWriter_fourcc(*'MJPG'),
                                  25, (640, 480))
        while self.allowRecording and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                aviFile.write(frame)
        aviFile.release()
        cap.release()

    def start_recording(self,auto_stop_time=0,output_filepath=""):
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
        remove(self.webcam_video_filename)
    def setflag(self,value):
        self.flag=value


if __name__ =='__main__':
    app = QApplication(sys.argv)
    pa_no=0
    trial=0
    stype='w'
    sno=0

    folder_path="pa_train/pa_"+str(pa_no)+"/trial_"+str(trial)+"/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filepath=folder_path+stype+str(sno)+".mp4"
    vr = VideoRecorder()
    vr.start_recording(3,filepath)
    sys.exit(app.exec_())
