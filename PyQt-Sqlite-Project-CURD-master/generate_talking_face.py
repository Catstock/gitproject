import csv

pa_head_path = ['../PyQt-Sqlite-Project-CURD-master/pa_head/pa_11', '../PyQt-Sqlite-Project-CURD-master/pa_head/pa_2']
audio_path = ['misc/Audio_Source\\00001.mp3', 'misc/Audio_Source\\00001.mp3']
def writecsv(pa_head_path,audio_path):
    # 将数据按照指定的格式组织为列表
    data = []
    for i in range(len(pa_head_path)):
        row = [pa_head_path[i], '1', 'None', '0', audio_path[i], 'None', '0', 'None']
        data.append(row)

    # 将数据写入csv文件

    with open('../Talking-Face_PC-AVS-main/misc/demo2.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        writer.writerows(data)

import subprocess
def runAudio2Video():
    # 定义多条Git Bash命令
    commands = ['pwd && cd ../Talking-Face_PC-AVS-main && pwd && bash experiments/demo_vox.sh',
                'exit'
                ]
    # 唤起Git Bash并执行命令
    for cmd in commands:
        subprocess.call(['C:/Program Files/Git/bin/bash.exe', '-c', cmd])

import shutil
import os
def transVideo(new_name,pa_no,audio_no,target_path= "pa_video"):
    # 定义视频的名称和源路径、目标路径
    video_name = "avG_Pose_Driven_.mp4"
    source_path = "pa_video/results/id_pa_"+str(pa_no)+"_pose_pa_"+str(pa_no)+"_audio_"+str(audio_no)

    # 将视频重命名为new_name.mp4
    os.rename(os.path.join(source_path, video_name), os.path.join(source_path, new_name+".mp4"))
    # 将视频剪切到目标路径下
    shutil.move(os.path.join(source_path, new_name+".mp4"), os.path.join(target_path, new_name+".mp4"))


def deleteVideo(folder_path="pa_video/results"):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 使用shutil.rmtree()删除非空目录
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

#transVideo("pa_test","1","00001")
#transVideo("pa_test2","2","00001")
# deleteVideo()

import subprocess
def cropPic():
    cmd = "python ../Talking-Face_PC-AVS-main/scripts/align_68.py --folder_path ../PyQt-Sqlite-Project-CURD-master/pa_head/pa_11"
    subprocess.run(cmd, shell=True, check=True)


writecsv(pa_head_path,audio_path)
# from ../Talking-Face_PC-AVS-main/generate_talking_face import
runAudio2Video()