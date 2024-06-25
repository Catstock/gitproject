import glob
import subprocess
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import pandas as pd


def video_to_frames(video_path, output_dir):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取视频
    cap = cv2.VideoCapture(video_path)
    frame_count = 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 保存每一帧为.jpg文件
        output_path = os.path.join(output_dir, f"{frame_count}.jpg")
        cv2.imwrite(output_path, frame)
        frame_count += 1

    cap.release()
    print(f"Video frames have been saved to {output_dir}")


def frames_to_video(input_dir, output_video, fps):
    image_files = [f for f in os.listdir(input_dir) if f.endswith(".jpg")]
    # 从第一帧中获取图像尺寸
    frame = cv2.imread(os.path.join(input_dir, image_files[0]))
    h, w, layers = frame.shape

    # 定义编码、创建VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (w, h))

    # 为每个文件写入帧
    for image_file in image_files:
        image_path = os.path.join(input_dir, image_file)
        frame = cv2.imread(image_path)
        video.write(frame)  # 写入帧

    video.release()
    print(f"Video saved to {output_video}")


def cropPic():
    # for i in (1,117):
    cmd = "python ../Talking-Face_PC-AVS-main/scripts/align_01.py --folder_path ../PyQt-Sqlite-Project-CURD-master/pa_cropped/pa_21"
    subprocess.run(cmd, shell=True, check=True)


video_to_frames("train/pa_21/trial1/v2_1.mp4","pa_cropped/pa_21")
cropPic()

# # 使用函数huo
# input_dir = "pa_cropped/pa_21_cropped"  # 输入目录
# output_video = "pa_cropped/train.mp4"  # 输出视频路径
# fps = 24.0  # 视频帧率
# frames_to_video(input_dir, output_video, fps)

def calculate_psnr_ssim(video_path1, video_path2):
    cap1 = cv2.VideoCapture(video_path1)
    cap2 = cv2.VideoCapture(video_path2)

    psnr_values = []
    ssim_values = []

    while True:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # 计算当前帧的PSNR和SSIM
        psnr = cv2.PSNR(frame1, frame2)
        ssim_value = ssim(frame1, frame2, multichannel=True)

        psnr_values.append(psnr)
        ssim_values.append(ssim_value)

    cap1.release()
    cap2.release()

    # 计算平均PSNR和SSIM
    avg_psnr = np.mean(psnr_values)
    avg_ssim = np.mean(ssim_values)

    return avg_psnr, avg_ssim


# # 使用函数
# video_path1 = "pa_cropped/train.mp4"
# video_path2 = "pa_cropped/generate.mp4"
# avg_psnr, avg_ssim = calculate_psnr_ssim(video_path1, video_path2)
# print("Average PSNR:", avg_psnr)
# print("Average SSIM:", avg_ssim)

def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)  # 判断是否是文件
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)  # 删除文件
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        else:
            print(f"Skipping: {file_path} (not a file)")  # 要删除文件的文件夹路径
            folder_to_delete = '/path/to/your/folder'  # 调用函数删除文件夹下的所有文件
            delete_files_in_folder(folder_to_delete)


# cropPic()
# print("cropped")
# pa_no_set = ["21", "23", "27", "35", "37", "39"]
# psnr_arr = []
# final_psnr_arr = []
# ssim_arr = []
# final_ssim_arr = []
# for j in (0, len(pa_no_set)):
#     pa_no = pa_no_set[j]
#     train_folder_path = "analyze/" + pa_no + "/train"
#     train_files = glob.glob(os.path.join(train_folder_path, "*.mp4"))
#     generate_folder_path = "analyze/" + pa_no + "/generate"
#     generate_files = glob.glob(os.path.join(generate_folder_path, "*.mp4"))
#     n = len(train_files)
#     for i in (0, n):
#         train_path = train_files[i]
#         generate_path = generate_files[i]
#         cropped_path = "analyze/" + pa_no + "/cropped_train/" + str(i) + ".mp4"
#         temp_cropped_path = "temp_cropped"
#         video_to_frames(train_path, temp_cropped_path)
#         cropPic()
#         input_dir = temp_cropped_path  # 输入目录
#         output_video = cropped_path  # 输出视频路径
#         fps = 24.0  # 视频帧率
#         frames_to_video(input_dir, output_video, fps)
#         temp_avg_psnr, temp_avg_ssim = calculate_psnr_ssim(train_path, generate_path)
#         psnr_arr.append(temp_avg_psnr)
#         ssim_arr.append(temp_avg_ssim)
#     final_avg_psnr = np.mean(temp_avg_psnr)
#     final_avg_ssim = np.mean(temp_avg_ssim)
#     psnr_arr.clear()
#     ssim_arr.clear()
#
#     final_psnr_arr.append(final_avg_psnr)
#     final_ssim_arr.append(final_avg_ssim)
# data = {'患者编号': pa_no_set,
#         'SSIM': final_ssim_arr,
#         'PSNR': final_psnr_arr}
# df = pd.DataFrame(data)
# df.to_excel('analyze.xlsx')
#
# print("患者：", pa_no_set)
# print("Average PSNR:", final_psnr_arr)
# print("Average SSIM:", final_ssim_arr)
