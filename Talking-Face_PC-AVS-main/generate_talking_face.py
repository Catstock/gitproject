import csv

pa_head_path = ['../PyQt-Sqlite-Project-CURD-master/pa_head/pa_1', '../PyQt-Sqlite-Project-CURD-master/pa_head/pa_2']
audio_path = ['misc/Audio_Source/00001.mp3', 'misc/Audio_Source/00001.mp3']
def writecsv(pa_head_path,audio_path):
    # 将数据按照指定的格式组织为列表
    data = []
    for i in range(len(pa_head_path)):
        row = [pa_head_path[i], '1', 'None', '0', audio_path[i], 'None', '0', 'None']
        data.append(row)

    # 将数据写入csv文件
    with open('misc/demo2.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        writer.writerows(data)

import subprocess

def runAudio2Video():
    # 定义多条Git Bash命令
    commands = ['source activate py36',
                'cd /e/code/gitproject/Talking-Face_PC-AVS-main',
                'bash experiments/demo_vox.sh',
                'exit'
                ]
    # 唤起Git Bash并执行命令
    for cmd in commands:
        subprocess.call(['C:/Program Files/Git/bin/bash.exe', '-c', cmd])

import os
def transvideo(new_name,source_path,target_path):
    # 定义视频的名称和源路径、目标路径
    video_name = "avG_Pose_Driven_.mp4"
    source_path = "/path/to/source_folder"
    target_path = "/path/to/target_folder"

    # 将视频重命名为new_name.mp4
    os.rename(os.path.join(source_path, video_name), os.path.join(source_path, new_name+".mp4"))
    # 将视频剪切到目标路径下
    os.move(os.path.join(source_path, new_name+"mp4"), os.path.join(target_path, new_name+".mp4"))

    # 获取源路径下的所有文件列表
    files = os.listdir(source_path)
    # 遍历文件列表，使用os.remove()函数将每个文件删除
    for file in files:
        os.remove(os.path.join(source_path, file))

