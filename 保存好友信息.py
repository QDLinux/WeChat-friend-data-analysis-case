import itchat
import pandas as pd
import time
import re

def login_wechat():
    # 扫码登录，hotReload=True可以缓存登录状态
    try:
        itchat.auto_login(hotReload=True)
        print("登录成功！")
        return True
    except Exception as e:
        print(f"登录失败: {e}")
        return False

def get_friends_info():
    if not itchat.instance.alive:
        print("微信未登录，请先登录！")
        return None
    try:
        friends = itchat.get_friends(update=True)[0:] # 获取所有好友信息
        friend_list = []
        for friend in friends:
            # 清理emoji等特殊字符（可选）
            cleaned_nick = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_-]', '', friend['NickName'])
            cleaned_remark = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_-]', '', friend['RemarkName'])
            cleaned_sign = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_,\.?!，。？！ -]', '', friend['Signature']) # 保留一些标点

            friend_info = {
                'UserName': friend['UserName'], # 用户唯一标识，重要！
                'NickName': cleaned_nick,
                'RemarkName': cleaned_remark,
                'Sex': friend['Sex'], # 1:男, 2:女, 0:未知
                'Province': friend['Province'],
                'City': friend['City'],
                'Signature': cleaned_sign,
                # 其他信息如 'HeadImgUrl', 'StarFriend' 等根据需要添加
            }
            friend_list.append(friend_info)

        df = pd.DataFrame(friend_list)
        return df
    except Exception as e:
        print(f"获取好友信息失败: {e}")
        return None

def save_friends_to_file(df, filename='wechat_friends.csv'):
    if df is not None:
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig') # utf-8-sig 防止中文乱码
            print(f"好友信息已保存到 {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")

# --- 主流程 ---
# if login_wechat():
#     friends_df = get_friends_info()
#     if friends_df is not None:
#         save_friends_to_file(friends_df)
#     itchat.logout() # 退出登录
