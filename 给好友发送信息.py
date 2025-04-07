def send_message_to_friend(name, message):
    if not itchat.instance.alive:
        print("微信未登录！")
        return False
    try:
        # 优先按备注名查找，其次按昵称
        users = itchat.search_friends(name=name)
        if not users:
            print(f"未找到好友: {name}")
            return False

        target_user_name = users[0]['UserName']
        itchat.send(message, toUserName=target_user_name)
        print(f"已向 {name} 发送消息: {message}")
        time.sleep(2) # 避免发送过快
        return True
    except Exception as e:
        print(f"发送消息失败: {e}")
        return False

# --- 使用 ---
# send_message_to_friend("好友备注或昵称", "你好！这是一条测试消息。")
