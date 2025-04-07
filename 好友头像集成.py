import itchat
import os
import math
from PIL import Image
import requests # 用于下载图片

def download_avatars(friends_df, save_dir='avatars'):
    if friends_df is None: return []
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    avatar_paths = []
    print("开始下载头像...")
    # 注意：itchat的get_head_img可能直接返回图片二进制数据或需要UserName
    for index, row in friends_df.iterrows():
        user_name = row['UserName']
        # 假设 itchat.get_head_img 可以获取头像
        try:
            # 方式一：itchat直接获取 (根据实际库调整)
            img_data = itchat.get_head_img(userName=user_name)
            img_path = os.path.join(save_dir, f"{user_name}.jpg")
            with open(img_path, 'wb') as f:
                f.write(img_data)
            avatar_paths.append(img_path)

            # # 方式二：如果能获取到 HeadImgUrl (需要requests库)
            # url = row['HeadImgUrl']
            # if url:
            #     response = requests.get(url, stream=True)
            #     if response.status_code == 200:
            #         img_path = os.path.join(save_dir, f"{user_name}.jpg")
            #         with open(img_path, 'wb') as f:
            #             f.write(response.content)
            #         avatar_paths.append(img_path)
            #     else:
            #         print(f"下载失败: {user_name}, status code: {response.status_code}")
            # else:
            #      print(f"无头像URL: {user_name}")

        except Exception as e:
            print(f"下载头像失败 for {row.get('NickName', user_name)}: {e}") # 使用get避免KeyError
        # 加个延时防止请求过快
        # time.sleep(0.1)

    print(f"头像下载完成，共 {len(avatar_paths)} 张。")
    return avatar_paths

def create_avatar_montage(avatar_paths, output_path='avatar_montage.png', img_per_row=10):
    if not avatar_paths: return

    images = [Image.open(p) for p in avatar_paths if os.path.exists(p)]
    if not images:
        print("没有有效的头像图片来创建蒙太奇。")
        return

    # 假设所有头像大小一致，取第一个的大小；否则需要resize
    img_size = images[0].size
    width, height = img_size

    num_images = len(images)
    num_rows = math.ceil(num_images / img_per_row)
    montage_width = width * img_per_row
    montage_height = height * num_rows

    montage = Image.new('RGB', (montage_width, montage_height), color='white')

    x_offset, y_offset = 0, 0
    for i, img in enumerate(images):
        try:
            # 如果尺寸不一致，需要先 resize
            if img.size != img_size:
                img = img.resize(img_size)
            montage.paste(img, (x_offset, y_offset))
            x_offset += width
            if (i + 1) % img_per_row == 0:
                x_offset = 0
                y_offset += height
        except Exception as e:
            print(f"处理图片 {avatar_paths[i]} 时出错: {e}")
            continue # 跳过损坏或格式错误的图片

    montage.save(output_path)
    print(f"头像墙已保存到 {output_path}")

# --- 使用 ---
# friends_df = pd.read_csv('wechat_friends.csv')
# avatar_paths = download_avatars(friends_df)
# if avatar_paths:
#     create_avatar_montage(avatar_paths)
