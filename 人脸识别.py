import face_recognition
import os
from PIL import Image
import numpy as np

def analyze_faces_in_avatars(avatar_paths):
    face_count = 0
    no_face_count = 0
    error_count = 0
    total_avatars = len(avatar_paths)

    print("开始分析头像中的人脸...")
    for img_path in avatar_paths:
        try:
            # face_recognition 需要 numpy 数组
            image = face_recognition.load_image_file(img_path)
            face_locations = face_recognition.face_locations(image) # 使用cnn模型会更准但慢 face_locations(image, model='cnn')

            if len(face_locations) > 0:
                face_count += 1
            else:
                no_face_count += 1
        except Exception as e:
            # 可能遇到图片损坏或格式问题
            print(f"处理图片 {img_path} 时发生错误: {e}")
            error_count += 1

    print("\n人脸分析结果:")
    print(f"总头像数: {total_avatars}")
    print(f"检测到人脸的头像数: {face_count}")
    print(f"未检测到人脸的头像数: {no_face_count}")
    print(f"处理出错的头像数: {error_count}")

    if total_avatars - error_count > 0:
         face_ratio = face_count / (total_avatars - error_count) * 100
         print(f"人脸头像占比 (在成功处理的图片中): {face_ratio:.2f}%")
    return {'total': total_avatars, 'faces': face_count, 'no_faces': no_face_count, 'errors': error_count}

# --- 使用 ---
# avatar_paths = [os.path.join('avatars', f) for f in os.listdir('avatars') if f.endswith('.jpg')] # 获取已下载头像列表
# face_analysis_results = analyze_faces_in_avatars(avatar_paths)
