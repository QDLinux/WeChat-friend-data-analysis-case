# import tkinter as tk
# from tkinter import ttk, scrolledtext, messagebox, filedialog
# from PIL import Image, ImageTk
# import threading
# import queue # 用于线程间通信
# import pandas as pd
# import os

# # 假设 actions.py 包含了之前定义的各种功能函数
# import actions # 需要创建这个文件并放入功能代码

# class WeChatAnalyzerApp:
#     def __init__(self, master):
#         self.master = master
#         master.title("微信好友数据分析工具")
#         master.geometry("800x600")

#         self.message_queue = queue.Queue() # 用于从工作线程接收消息更新UI

#         # --- 数据存储 ---
#         self.friends_df = None
#         self.avatar_paths = []

#         # --- UI 控件 ---
#         self.setup_ui()

#         # --- 启动检查队列的循环 ---
#         self.master.after(100, self.process_queue)

#     def setup_ui(self):
#         # --- 控制面板 (左侧) ---
#         control_frame = ttk.Frame(self.master, padding="10")
#         control_frame.pack(side=tk.LEFT, fill=tk.Y)

#         ttk.Button(control_frame, text="登录微信", command=self.run_in_thread(actions.login_wechat)).pack(pady=5, fill=tk.X)
#         ttk.Button(control_frame, text="获取/刷新好友数据", command=self.run_in_thread(self.load_friend_data)).pack(pady=5, fill=tk.X)
#         ttk.Button(control_frame, text="保存好友数据到CSV", command=self.save_data).pack(pady=5, fill=tk.X)

#         ttk.Separator(control_frame, orient='horizontal').pack(pady=10, fill=tk.X)

#         ttk.Label(control_frame, text="数据分析与可视化:").pack(pady=5)
#         ttk.Button(control_frame, text="性别分布", command=self.run_in_thread(self.show_gender_viz)).pack(pady=2, fill=tk.X)
#         ttk.Button(control_frame, text="省份地图", command=self.run_in_thread(self.show_province_viz)).pack(pady=2, fill=tk.X)
#         # ... 其他可视化按钮 ...
#         ttk.Button(control_frame, text="签名词云", command=self.run_in_thread(self.show_wordcloud_viz)).pack(pady=2, fill=tk.X)

#         ttk.Separator(control_frame, orient='horizontal').pack(pady=10, fill=tk.X)

#         ttk.Label(control_frame, text="头像处理:").pack(pady=5)
#         ttk.Button(control_frame, text="下载头像", command=self.run_in_thread(self.download_avatars_action)).pack(pady=2, fill=tk.X)
#         ttk.Button(control_frame, text="生成头像墙", command=self.run_in_thread(self.show_montage_viz)).pack(pady=2, fill=tk.X)
#         ttk.Button(control_frame, text="人脸检测分析", command=self.run_in_thread(self.analyze_faces_action)).pack(pady=2, fill=tk.X)

#         # --- 显示区域 (右侧) ---
#         self.display_frame = ttk.Frame(self.master, padding="10")
#         self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#         # 使用 Notebook (选项卡) 来切换不同的显示内容
#         self.notebook = ttk.Notebook(self.display_frame)
#         self.notebook.pack(fill=tk.BOTH, expand=True)

#         # 日志/文本输出 Tab
#         self.log_tab = ttk.Frame(self.notebook)
#         self.notebook.add(self.log_tab, text='日志输出')
#         self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, height=10)
#         self.log_text.pack(fill=tk.BOTH, expand=True)

#         # 图表/图片显示 Tab (可以有多个)
#         self.image_tab = ttk.Frame(self.notebook)
#         self.notebook.add(self.image_tab, text='图表/图像')
#         self.image_label = ttk.Label(self.image_tab) # 用于显示图片
#         self.image_label.pack(pady=10)

#         # 可以在这里添加用于嵌入 Matplotlib 图表的 Canvas

#     def log(self, message):
#         """线程安全地向日志文本框添加消息"""
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END) # 滚动到底部

#     def process_queue(self):
#         """处理来自工作线程的消息"""
#         try:
#             message = self.message_queue.get_nowait()
#             # 根据消息类型执行操作，例如更新UI
#             if isinstance(message, str):
#                 self.log(message)
#             elif isinstance(message, dict) and 'type' in message:
#                 msg_type = message['type']
#                 if msg_type == 'login_status':
#                     self.log(f"登录状态: {'成功' if message['success'] else '失败'}")
#                 elif msg_type == 'friend_data':
#                     self.friends_df = message['data']
#                     self.log(f"成功获取 {len(self.friends_df)} 位好友数据。")
#                 elif msg_type == 'image_display':
#                     self.show_image_on_tab(message['path'])
#                     self.notebook.select(self.image_tab) # 切换到图像Tab
#                 elif msg_type == 'html_display':
#                     # Pyecharts 生成 html 后，可以在这里用 webbrowser 打开
#                     import webbrowser
#                     webbrowser.open(message['path'])
#                     self.log(f"已在浏览器中打开: {message['path']}")
#                 elif msg_type == 'avatar_paths':
#                     self.avatar_paths = message['data']
#                     self.log(f"获取到 {len(self.avatar_paths)} 个头像路径。")
#                 elif msg_type == 'face_analysis_result':
#                     result = message['data']
#                     self.log(f"人脸分析完成: 总数={result['total']}, 人脸={result['faces']}, 无人脸={result['no_faces']}, 错误={result['errors']}")

#                 # 可以添加更多消息类型处理...
#             else:
#                  self.log(f"未知消息类型: {message}")

#         except queue.Empty:
#             pass # 队列为空，什么都不做
#         finally:
#             # 持续检查队列
#             self.master.after(100, self.process_queue)

#     def run_in_thread(self, target_func, *args):
#         """返回一个启动线程运行目标函数的函数"""
#         def wrapper():
#             # 可以加一个简单的防止重复点击的机制 (可选)
#             thread = threading.Thread(target=target_func, args=args, daemon=True)
#             thread.start()
#         return wrapper

#     # --- Action Wrappers (调用 actions.py 中的函数，并通过 queue 返回结果) ---

#     def load_friend_data(self):
#         self.log("开始获取好友数据...")
#         # 假设 actions.get_friends_info() 返回 DataFrame 或 None
#         df = actions.get_friends_info() # 这需要能访问 itchat 实例
#         if df is not None:
#             self.message_queue.put({'type': 'friend_data', 'data': df})
#         else:
#             self.message_queue.put("获取好友数据失败。")

#     def save_data(self):
#         if self.friends_df is None:
#             messagebox.showwarning("提示", "请先获取好友数据！")
#             return
#         filepath = filedialog.asksaveasfilename(defaultextension=".csv",
#                                                   filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
#         if filepath:
#             try:
#                 actions.save_friends_to_file(self.friends_df, filepath)
#                 self.log(f"数据已保存到: {filepath}")
#             except Exception as e:
#                 self.log(f"保存失败: {e}")
#                 messagebox.showerror("错误", f"保存文件失败:\n{e}")

#     def show_gender_viz(self):
#         if self.friends_df is None:
#             self.log("无好友数据，无法生成性别分布图。")
#             return
#         self.log("正在生成性别分布图...")
#         output_path = 'temp_gender_distribution.png' # 临时文件
#         try:
#             actions.visualize_gender(self.friends_df, output_path) # 让它保存但不显示 plt.show()
#             self.message_queue.put({'type': 'image_display', 'path': output_path})
#         except Exception as e:
#             self.log(f"生成性别图失败: {e}")

#     def show_province_viz(self):
#         if self.friends_df is None:
#              self.log("无好友数据，无法生成省份地图。")
#              return
#         self.log("正在生成省份分布地图...")
#         output_path = 'temp_province_distribution.html'
#         try:
#             actions.visualize_province(self.friends_df, output_path)
#             # 对于html，选择在浏览器打开
#             self.message_queue.put({'type': 'html_display', 'path': output_path})
#         except Exception as e:
#             self.log(f"生成省份地图失败: {e}")


#     def show_wordcloud_viz(self):
#         if self.friends_df is None:
#              self.log("无好友数据，无法生成词云。")
#              return
#         self.log("正在生成签名词云...")
#         output_path = 'temp_signature_wordcloud.png'
#         font_path = actions.find_font() # 需要一个函数找到可用的中文字体
#         if not font_path:
#              self.log("错误：未找到可用的中文字体，无法生成词云。")
#              messagebox.showerror("错误", "未找到中文字体！请确保系统中有 SimHei 或其他常见中文字体，或在代码中指定路径。")
#              return
#         try:
#             actions.generate_signature_wordcloud(self.friends_df, output_path, font_path=font_path)
#             self.message_queue.put({'type': 'image_display', 'path': output_path})
#         except Exception as e:
#             self.log(f"生成词云失败: {e}")


#     def download_avatars_action(self):
#          if self.friends_df is None:
#              self.log("无好友数据，无法下载头像。")
#              return
#          self.log("开始下载头像...")
#          paths = actions.download_avatars(self.friends_df)
#          self.message_queue.put({'type': 'avatar_paths', 'data': paths})
#          self.log("头像下载任务完成。") # 注意下载是异步的


#     def show_montage_viz(self):
#         if not self.avatar_paths:
#              self.log("请先下载头像。")
#              return
#         self.log("正在生成头像墙...")
#         output_path = 'temp_avatar_montage.png'
#         try:
#             actions.create_avatar_montage(self.avatar_paths, output_path)
#             self.message_queue.put({'type': 'image_display', 'path': output_path})
#         except Exception as e:
#             self.log(f"生成头像墙失败: {e}")


#     def analyze_faces_action(self):
#          if not self.avatar_paths:
#               self.log("请先下载头像。")
#               return
#          self.log("开始进行人脸检测分析...")
#          results = actions.analyze_faces_in_avatars(self.avatar_paths)
#          self.message_queue.put({'type': 'face_analysis_result', 'data': results})


#     def show_image_on_tab(self, image_path):
#         """在图片标签页显示图片"""
#         try:
#             img = Image.open(image_path)
#             # 调整图片大小以适应标签页 (可选)
#             img.thumbnail((self.image_tab.winfo_width() - 20, self.image_tab.winfo_height() - 40)) # 减去一些padding
#             photo = ImageTk.PhotoImage(img)

#             self.image_label.config(image=photo)
#             self.image_label.image = photo # 保持引用，防止被垃圾回收
#             self.log(f"已显示图片: {os.path.basename(image_path)}")
#         except Exception as e:
#             self.log(f"加载图片失败 {image_path}: {e}")
#             messagebox.showerror("错误", f"无法加载或显示图片:\n{e}")


# if __name__ == '__main__':
#     # 在 main.py 中运行
#     root = tk.Tk()
#     app = WeChatAnalyzerApp(root)
#     root.mainloop()

#     # 程序退出前尝试登出微信 (如果需要)
#     # try:
#     #     if actions.is_wechat_logged_in(): # 需要一个判断是否登录的函数
#     #         actions.logout_wechat()
#     # except Exception as e:
#     #     print(f"尝试登出微信时出错: {e}")


import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import pandas as pd
from datetime import datetime
import webbrowser

# 导入所有功能模块
try:
    import itchat
except ImportError:
    # 如果itchat不可用，尝试使用itchat-uos
    try:
        import itchat_uos as itchat
    except ImportError:
        print("请安装itchat或itchat-uos: pip install itchat-uos")
        exit(1)
import time
import re
import math
from PIL import Image, ImageTk
import requests
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud
from pyecharts import options as opts
from pyecharts.charts import Map
import io
import base64

class WeChatFriendsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("微信好友管理系统")
        self.root.geometry("800x600")
        
        # 数据存储
        self.friends_df = None
        self.avatar_paths = []
        self.qr_window = None
        
        # 创建界面
        self.create_widgets()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 准备停用词
        self.stopwords = set(['的', '了', '我', '你', '他', '她', '是', '在', '不', '就', '都', '也', '还', '说', 
                            '这个', '那个', '一个', '什么', ' ', ',', '.', '，', '。', '?', '？', '!', '！', '~', '…'])
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="微信好友管理系统", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 微信登录区域
        login_frame = ttk.LabelFrame(main_frame, text="微信登录", padding="10")
        login_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        login_frame.columnconfigure(1, weight=1)
        
        self.login_status = ttk.Label(login_frame, text="未登录", foreground="red")
        self.login_status.grid(row=0, column=0, padx=(0, 10))
        
        self.login_btn = ttk.Button(login_frame, text="扫码登录", command=self.login_wechat_thread)
        self.login_btn.grid(row=0, column=1, padx=5)
        
        self.logout_btn = ttk.Button(login_frame, text="退出登录", command=self.logout_wechat, state="disabled")
        self.logout_btn.grid(row=0, column=2, padx=5)
        
        # 数据管理区域
        data_frame = ttk.LabelFrame(main_frame, text="数据管理", padding="10")
        data_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(data_frame, text="获取好友信息", command=self.get_friends_thread).grid(row=0, column=0, padx=5)
        ttk.Button(data_frame, text="保存到文件", command=self.save_friends).grid(row=0, column=1, padx=5)
        ttk.Button(data_frame, text="加载文件", command=self.load_friends).grid(row=0, column=2, padx=5)
        ttk.Button(data_frame, text="下载头像", command=self.download_avatars_thread).grid(row=0, column=3, padx=5)
        
        # 功能区域
        function_frame = ttk.LabelFrame(main_frame, text="分析功能", padding="10")
        function_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行功能按钮
        ttk.Button(function_frame, text="性别分布图", command=self.visualize_gender).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(function_frame, text="省份分布图", command=self.visualize_province).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(function_frame, text="签名词云", command=self.generate_wordcloud).grid(row=0, column=2, padx=5, pady=5)
        
        # 第二行功能按钮
        ttk.Button(function_frame, text="头像墙", command=self.create_avatar_montage).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(function_frame, text="发送消息", command=self.open_send_message_dialog).grid(row=1, column=1, padx=5, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def login_wechat_thread(self):
        """在新线程中登录微信"""
        # 重置登录相关状态
        self.reset_login_state()
        threading.Thread(target=self.login_wechat_simple, daemon=True).start()
    
    def reset_login_state(self):
        """重置登录状态"""
        try:
            # 确保先退出之前的登录状态
            try:
                itchat.logout()
            except:
                pass
                
            # 关闭之前的二维码窗口
            if self.qr_window and self.qr_window.winfo_exists():
                self.qr_window.destroy()
                self.qr_window = None
                
            self.log("已重置登录状态")
        except Exception as e:
            self.log(f"重置登录状态时出错: {e}")
    
    def login_wechat_simple(self):
        """简化的微信登录方式"""
        self.log("开始微信登录...")
        self.login_btn.config(state="disabled")
        self.status_var.set("正在登录...")
        
        try:
            # 显示登录提示
            self.log("正在启动微信登录，请稍候...")
            
            # 方案1: 使用UOS协议（如果可用）
            try:
                self.log("尝试UOS协议登录...")
                # 如果是itchat-uos，尝试使用UOS模式
                if hasattr(itchat, 'set_logging'):
                    itchat.set_logging(loggingLevel=40)  # 减少日志输出
                
                result = itchat.auto_login(
                    hotReload=False,
                    enableCmdQR=2,  # 使用更兼容的二维码显示方式
                    picDir='qr_code.png',
                    qrCallback=self.qr_callback if hasattr(self, 'qr_callback') else None
                )
                
                if result and self.check_login_status():
                    self.root.after(0, self.login_success)
                    return
                        
            except Exception as e:
                self.log(f"UOS协议登录失败: {e}")
            
            # 方案2: 传统登录方式
            try:
                self.log("尝试传统登录方式...")
                result = itchat.auto_login(
                    hotReload=False,
                    enableCmdQR=True,
                    picDir='qr_backup.png'
                )
                
                if result and self.check_login_status():
                    self.root.after(0, self.login_success)
                    return
                    
            except Exception as e:
                self.log(f"传统登录方式失败: {e}")
            
            # 方案3: 最简单的登录方式
            try:
                self.log("尝试最简单的登录方式...")
                result = itchat.auto_login(hotReload=False)
                
                if result and self.check_login_status():
                    self.root.after(0, self.login_success)
                    return
                    
            except Exception as e:
                self.log(f"最简单登录方式也失败: {e}")
            
            # 所有方案都失败
            error_suggestions = (
                "所有登录方案都失败。\n\n"
                "建议解决方案：\n"
                "1. 安装itchat-uos: pip install itchat-uos\n"
                "2. 检查网络连接\n"
                "3. 关闭防火墙或代理\n"
                "4. 更新Python和tkinter"
            )
            self.root.after(0, self.login_failed, error_suggestions)
                
        except Exception as e:
            error_msg = str(e)
            if "mismatched tag" in error_msg:
                error_msg = "微信服务器响应异常，请稍后重试"
            elif "network" in error_msg.lower():
                error_msg = "网络连接失败，请检查网络"
            elif "SSL" in error_msg or "certificate" in error_msg:
                error_msg = "SSL证书错误，请检查系统时间或网络设置"
            
            self.root.after(0, self.login_failed, error_msg)
    
    def login_wechat(self):
        """使用图片二维码的登录方式（备用）"""
        self.log("开始微信登录...")
        self.login_btn.config(state="disabled")
        self.status_var.set("正在登录...")
        
        try:
            # 先显示等待窗口
            self.root.after(0, self.create_login_wait_window)
            
            # 使用简单登录，保存二维码为图片文件
            result = itchat.auto_login(
                hotReload=False,
                picDir='qr_code.png'  # 保存二维码到文件
            )
            
            if result:
                # 验证登录状态
                if self.check_login_status():
                    self.root.after(0, self.login_success)
                else:
                    self.root.after(0, self.login_failed, "登录验证失败")
            else:
                self.root.after(0, self.login_failed, "登录返回False")
                
        except Exception as e:
            self.root.after(0, self.login_failed, str(e))
    
    def login_success(self):
        """登录成功后的UI更新"""
        self.log("登录成功！正在验证...")
        
        # 再次验证登录状态
        if self.check_login_status():
            self.log("登录验证成功！")
            self.login_status.config(text="已登录", foreground="green")
            self.login_btn.config(state="disabled")
            self.logout_btn.config(state="normal")
            self.status_var.set("已登录")
            
            # 关闭登录窗口
            if self.qr_window and self.qr_window.winfo_exists():
                self.qr_window.destroy()
                self.qr_window = None
            
            # 显示登录成功消息
            try:
                user_info = itchat.search_friends()
                if user_info and len(user_info) > 0:
                    nickname = user_info[0].get('NickName', '用户')
                    self.log(f"欢迎, {nickname}！")
                    messagebox.showinfo("登录成功", f"欢迎, {nickname}！\n现在可以使用各项功能了。")
            except:
                messagebox.showinfo("登录成功", "登录成功！现在可以使用各项功能了。")
        else:
            self.log("登录验证失败，请重试")
            self.login_failed("登录验证失败")
    
    def login_failed(self, error_msg):
        """登录失败后的UI更新"""
        self.log(f"登录失败: {error_msg}")
        
        # 提供解决方案建议
        if "mismatched tag" in error_msg:
            self.log("建议解决方案：")
            self.log("1. 检查网络连接")
            self.log("2. 稍后重试")
            self.log("3. 如果问题持续，可能需要更新itchat库")
            suggestion = ("登录失败：微信服务器响应异常\n\n"
                         "可能的解决方案：\n"
                         "1. 检查网络连接是否正常\n"
                         "2. 稍等几分钟后重试\n"
                         "3. 重启程序后再试\n"
                         "4. 如问题持续，可能是itchat库版本问题")
            messagebox.showerror("登录失败", suggestion)
            
        elif "network" in error_msg.lower():
            suggestion = ("网络连接失败\n\n"
                         "请检查：\n"
                         "1. 网络连接是否正常\n"
                         "2. 防火墙设置\n"
                         "3. 代理设置")
            messagebox.showerror("网络错误", suggestion)
        else:
            messagebox.showerror("登录失败", f"登录失败：{error_msg}")
        
        self.login_status.config(text="登录失败", foreground="red")
        self.login_btn.config(state="normal")
        self.status_var.set("登录失败")
        
        # 关闭登录窗口
        if self.qr_window and self.qr_window.winfo_exists():
            self.qr_window.destroy()
            self.qr_window = None
    
    def show_qrcode(self, uuid, status, qrcode):
        """显示二维码的回调函数"""
        def update_qr():
            try:
                if status == '0':
                    self.log("请使用微信扫描二维码登录")
                    # 确保二维码窗口存在
                    if self.qr_window is None or not self.qr_window.winfo_exists():
                        self.create_qr_window()
                        time.sleep(0.1)  # 等待窗口创建
                    
                    # 将二维码数据转换为图片
                    try:
                        # qrcode参数是base64编码的PNG图片数据
                        qr_img = Image.open(io.BytesIO(qrcode))
                        # 调整大小
                        qr_img = qr_img.resize((300, 300), Image.Resampling.LANCZOS)
                        # 转换为PhotoImage
                        self.qr_photo = ImageTk.PhotoImage(qr_img)
                        # 显示在标签中
                        if hasattr(self, 'qr_label') and self.qr_label.winfo_exists():
                            self.qr_label.config(image=self.qr_photo)
                            if hasattr(self, 'qr_status_label') and self.qr_status_label.winfo_exists():
                                self.qr_status_label.config(text="请扫描二维码", foreground="blue")
                    except Exception as e:
                        self.log(f"显示二维码失败: {e}")
                        
                elif status == '201':
                    self.log("二维码已扫描，请在手机上确认登录")
                    if hasattr(self, 'qr_tip_label') and self.qr_tip_label.winfo_exists():
                        self.qr_tip_label.config(text="已扫描，请在手机上确认登录", foreground="blue")
                    if hasattr(self, 'qr_status_label') and self.qr_status_label.winfo_exists():
                        self.qr_status_label.config(text="等待确认...", foreground="orange")
                        
                elif status == '200':
                    self.log("登录确认中...")
                    if hasattr(self, 'qr_tip_label') and self.qr_tip_label.winfo_exists():
                        self.qr_tip_label.config(text="登录确认中...", foreground="green")
                    if hasattr(self, 'qr_status_label') and self.qr_status_label.winfo_exists():
                        self.qr_status_label.config(text="登录中...", foreground="green")
                        
                elif status == '408':
                    self.log("二维码超时，请重新登录")
                    if hasattr(self, 'qr_status_label') and self.qr_status_label.winfo_exists():
                        self.qr_status_label.config(text="二维码已超时", foreground="red")
                        
            except Exception as e:
                self.log(f"更新二维码状态失败: {e}")
        
        # 在主线程中更新UI
        try:
            self.root.after(0, update_qr)
        except:
            pass
    
    def create_login_wait_window(self):
        """创建登录等待窗口"""
        if self.qr_window is not None and self.qr_window.winfo_exists():
            return
            
        self.qr_window = tk.Toplevel(self.root)
        self.qr_window.title("微信登录")
        self.qr_window.geometry("400x400")
        self.qr_window.resizable(False, False)
        
        # 居中显示
        self.qr_window.transient(self.root)
        x = (self.qr_window.winfo_screenwidth() // 2) - (200)
        y = (self.qr_window.winfo_screenheight() // 2) - (200)
        self.qr_window.geometry(f"400x400+{x}+{y}")
        
        # 标题
        title_label = ttk.Label(self.qr_window, text="微信登录", font=('Arial', 16, 'bold'))
        title_label.pack(pady=30)
        
        # 说明文字
        info_label = ttk.Label(self.qr_window, text="请按以下步骤操作：", font=('Arial', 12))
        info_label.pack(pady=10)
        
        # 步骤说明
        steps = [
            "1. 查看控制台窗口中的二维码",
            "2. 或点击下方按钮查看二维码图片",
            "3. 使用微信扫描二维码", 
            "4. 在手机上确认登录",
            "5. 程序将自动检测登录状态"
        ]
        
        for step in steps:
            step_label = ttk.Label(self.qr_window, text=step, font=('Arial', 10))
            step_label.pack(pady=2, anchor='w', padx=50)
        
        # 故障排除提示
        trouble_frame = ttk.LabelFrame(self.qr_window, text="如果遇到问题", padding="5")
        trouble_frame.pack(pady=10, padx=20, fill='x')
        
        trouble_tips = [
            "• 检查网络连接",
            "• 确保微信版本是最新的",
            "• 如果长时间无响应，点击取消后重试"
        ]
        
        for tip in trouble_tips:
            tip_label = ttk.Label(trouble_frame, text=tip, font=('Arial', 9), foreground="gray")
            tip_label.pack(anchor='w')
        
        # 状态显示
        self.login_status_label = ttk.Label(self.qr_window, text="正在获取二维码...", 
                                           font=('Arial', 10), foreground="blue")
        self.login_status_label.pack(pady=20)
        
        # 按钮框架
        btn_frame = ttk.Frame(self.qr_window)
        btn_frame.pack(pady=10)
        
        # 打开二维码图片按钮
        open_qr_btn = ttk.Button(btn_frame, text="打开二维码图片", command=self.open_qr_image)
        open_qr_btn.pack(side=tk.LEFT, padx=10)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消登录", command=self.cancel_login)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 窗口关闭事件
        self.qr_window.protocol("WM_DELETE_WINDOW", self.cancel_login)
        
        # 定期检查登录状态
        self.check_login_status_periodically()
    
    def open_qr_image(self):
        """打开二维码图片"""
        import subprocess
        import sys
        
        qr_files = ['qr_code.png', 'qr_backup.png', 'qr.png', 'QR.png']
        
        for qr_file in qr_files:
            if os.path.exists(qr_file):
                try:
                    if sys.platform.startswith('darwin'):  # macOS
                        subprocess.call(['open', qr_file])
                    elif sys.platform.startswith('win'):   # Windows
                        os.startfile(qr_file)
                    else:  # Linux
                        subprocess.call(['xdg-open', qr_file])
                    self.log(f"已打开二维码图片: {qr_file}")
                    return
                except Exception as e:
                    self.log(f"打开图片失败: {e}")
        
        # 如果没有找到图片，尝试刷新
        self.log("未找到二维码图片，尝试重新生成...")
        try:
            # 简单的重新生成二维码的尝试
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data("请重新点击登录按钮")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save("temp_qr.png")
            self.log("已生成临时二维码，请重新点击登录按钮获取真实二维码")
        except:
            pass
        
        messagebox.showwarning("提示", 
            "未找到二维码图片文件。\n\n可能的原因：\n"
            "1. 登录过程还未生成二维码\n"
            "2. 登录过程出现错误\n\n"
            "建议：\n"
            "1. 点击'取消登录'后重新尝试\n"
            "2. 检查控制台是否有二维码显示\n"
            "3. 检查网络连接")
    
    def check_login_status_periodically(self):
        """定期检查登录状态"""
        if self.qr_window and self.qr_window.winfo_exists():
            if self.check_login_status():
                # 登录成功
                self.login_success()
                return
            else:
                # 更新状态显示
                if hasattr(self, 'login_status_label') and self.login_status_label.winfo_exists():
                    self.login_status_label.config(text="等待扫码登录...")
                
                # 3秒后再次检查
                self.root.after(3000, self.check_login_status_periodically)
    
    def cancel_login(self):
        """取消登录"""
        try:
            self.log("正在取消登录...")
            
            # 关闭登录窗口
            if self.qr_window and self.qr_window.winfo_exists():
                self.qr_window.destroy()
                self.qr_window = None
            
            # 尝试停止itchat登录过程
            try:
                itchat.logout()
            except Exception as e:
                self.log(f"清理itchat状态时出错: {e}")
            
            # 重置登录按钮状态
            self.login_btn.config(state="normal")
            self.login_status.config(text="未登录", foreground="red")
            self.status_var.set("已取消登录")
            self.log("用户取消登录")
            
        except Exception as e:
            self.log(f"取消登录失败: {e}")
            # 即使出错也要重置按钮状态
            self.login_btn.config(state="normal")
    
    def check_login_status(self):
        """检查登录状态"""
        try:
            # 多种方式检查登录状态
            if hasattr(itchat, 'instance') and hasattr(itchat.instance, 'alive'):
                if itchat.instance.alive:
                    # 进一步验证登录状态
                    try:
                        # 尝试获取自己的信息来验证登录
                        user_info = itchat.search_friends()
                        if user_info and len(user_info) > 0:
                            return True
                    except:
                        pass
            
            # 备用检查方法
            try:
                friends = itchat.get_friends(update=False)
                return len(friends) > 0
            except:
                pass
            
            return False
        except:
            return False
    
    def logout_wechat(self):
        """退出微信登录"""
        try:
            itchat.logout()
            self.log("已退出登录")
            self.login_status.config(text="未登录", foreground="red")
            self.login_btn.config(state="normal")
            self.logout_btn.config(state="disabled")
            self.status_var.set("未登录")
            # 关闭二维码窗口
            if self.qr_window:
                self.qr_window.destroy()
                self.qr_window = None
        except Exception as e:
            self.log(f"退出登录失败: {e}")
    
    def get_friends_thread(self):
        """在新线程中获取好友信息"""
        threading.Thread(target=self.get_friends_info, daemon=True).start()
    
    def get_friends_info(self):
        """获取好友信息"""
        # 先检查登录状态
        if not self.check_login_status():
            messagebox.showerror("错误", "请先登录微信！")
            return
        
        self.log("开始获取好友信息...")
        self.status_var.set("正在获取好友信息...")
        
        try:
            friends = itchat.get_friends(update=True)[0:]
            friend_list = []
            
            self.log(f"正在处理 {len(friends)} 个好友信息...")
            
            for i, friend in enumerate(friends):
                try:
                    cleaned_nick = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_-]', '', friend.get('NickName', ''))
                    cleaned_remark = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_-]', '', friend.get('RemarkName', ''))
                    cleaned_sign = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_,\.?!，。？！ -]', '', friend.get('Signature', ''))
                    
                    friend_info = {
                        'UserName': friend.get('UserName', ''),
                        'NickName': cleaned_nick,
                        'RemarkName': cleaned_remark,
                        'Sex': friend.get('Sex', 0),
                        'Province': friend.get('Province', ''),
                        'City': friend.get('City', ''),
                        'Signature': cleaned_sign,
                    }
                    friend_list.append(friend_info)
                    
                    # 每处理50个好友更新一次状态
                    if (i + 1) % 50 == 0:
                        self.status_var.set(f"正在获取好友信息... {i+1}/{len(friends)}")
                        self.root.update()
                        
                except Exception as e:
                    self.log(f"处理好友信息时出错 (索引 {i}): {e}")
                    continue
            
            if friend_list:
                self.friends_df = pd.DataFrame(friend_list)
                self.log(f"成功获取 {len(friend_list)} 个好友信息")
                self.status_var.set(f"已获取 {len(friend_list)} 个好友信息")
                
                # 显示一些统计信息
                male_count = len(self.friends_df[self.friends_df['Sex'] == 1])
                female_count = len(self.friends_df[self.friends_df['Sex'] == 2])
                unknown_count = len(self.friends_df[self.friends_df['Sex'] == 0])
                
                self.log(f"性别统计 - 男性: {male_count}, 女性: {female_count}, 未知: {unknown_count}")
            else:
                self.log("未获取到任何好友信息")
                self.status_var.set("未获取到好友信息")
            
        except Exception as e:
            self.log(f"获取好友信息失败: {e}")
            self.status_var.set("获取失败")
            messagebox.showerror("错误", f"获取好友信息失败: {e}")
    
    def save_friends(self):
        """保存好友信息到文件"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有好友数据！请先获取好友信息。")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.friends_df.to_csv(filename, index=False, encoding='utf-8-sig')
                self.log(f"好友信息已保存到 {filename}")
            except Exception as e:
                self.log(f"保存文件失败: {e}")
    
    def load_friends(self):
        """从文件加载好友信息"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.friends_df = pd.read_csv(filename)
                self.log(f"从 {filename} 加载了 {len(self.friends_df)} 个好友信息")
                self.status_var.set(f"已加载 {len(self.friends_df)} 个好友信息")
            except Exception as e:
                self.log(f"加载文件失败: {e}")
    
    def download_avatars_thread(self):
        """在新线程中下载头像"""
        threading.Thread(target=self.download_avatars, daemon=True).start()
    
    def download_avatars(self):
        """下载好友头像"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有好友数据！")
            return
        
        if not itchat.instance.alive:
            messagebox.showerror("错误", "请先登录微信！")
            return
        
        save_dir = 'avatars'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        self.avatar_paths = []
        self.log("开始下载头像...")
        self.status_var.set("正在下载头像...")
        
        for index, row in self.friends_df.iterrows():
            user_name = row['UserName']
            try:
                img_data = itchat.get_head_img(userName=user_name)
                img_path = os.path.join(save_dir, f"{user_name}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                self.avatar_paths.append(img_path)
                self.log(f"已下载: {row.get('NickName', user_name)}")
            except Exception as e:
                self.log(f"下载头像失败 {row.get('NickName', user_name)}: {e}")
        
        self.log(f"头像下载完成，共 {len(self.avatar_paths)} 张")
        self.status_var.set("头像下载完成")
    
    def visualize_gender(self):
        """可视化性别分布"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有好友数据！")
            return
        
        try:
            gender_counts = self.friends_df['Sex'].value_counts()
            gender_labels = {1: '男性', 2: '女性', 0: '未知'}
            labels = [gender_labels.get(x, '未知') for x in gender_counts.index]
            sizes = gender_counts.values
            
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                   colors=['skyblue', 'lightcoral', 'lightgrey'])
            ax.axis('equal')
            plt.title('微信好友性别分布')
            
            output_path = 'gender_distribution.png'
            plt.savefig(output_path)
            plt.show()
            
            self.log(f"性别分布图已保存到 {output_path}")
        except Exception as e:
            self.log(f"生成性别分布图失败: {e}")
    
    def visualize_province(self):
        """可视化省份分布"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有好友数据！")
            return
        
        try:
            df_filtered = self.friends_df[self.friends_df['Province'].notna() & (self.friends_df['Province'] != '')]
            province_counts = df_filtered['Province'].value_counts().reset_index()
            province_counts.columns = ['province', 'count']
            data_pair = [list(z) for z in zip(province_counts['province'], province_counts['count'])]
            
            c = (
                Map()
                .add("好友数量", data_pair, "china")
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="微信好友省份分布"),
                    visualmap_opts=opts.VisualMapOpts(max_=int(province_counts['count'].max()), is_piecewise=False),
                )
                .render('province_distribution.html')
            )
            
            # 在浏览器中打开
            webbrowser.open('province_distribution.html')
            self.log("省份分布地图已保存到 province_distribution.html")
        except Exception as e:
            self.log(f"生成省份分布图失败: {e}")
    
    def generate_wordcloud(self):
        """生成签名词云"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有好友数据！")
            return
        
        try:
            signatures = self.friends_df['Signature'].dropna().astype(str)
            text = ' '.join(signatures)
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z ]', '', text)
            
            word_list = jieba.lcut(text, cut_all=False)
            meaningful_words = [word for word in word_list if word not in self.stopwords and len(word) > 1]
            words_text = ' '.join(meaningful_words)
            
            if not words_text:
                messagebox.showwarning("警告", "没有足够的有效词语生成词云")
                return
            
            # 尝试使用系统字体
            font_path = None
            if os.name == 'nt':  # Windows
                font_path = 'C:/Windows/Fonts/simhei.ttf'
            
            wc = WordCloud(
                font_path=font_path,
                background_color="white",
                max_words=200,
                width=800,
                height=400,
                stopwords=self.stopwords
            )
            wc.generate(words_text)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.title('好友签名词云')
            
            output_path = 'signature_wordcloud.png'
            plt.savefig(output_path)
            plt.show()
            
            self.log(f"签名词云图已保存到 {output_path}")
        except Exception as e:
            self.log(f"生成词云失败: {e}")
    
    def create_avatar_montage(self):
        """创建头像墙"""
        if not self.avatar_paths:
            messagebox.showerror("错误", "没有头像数据！请先下载头像。")
            return
        
        try:
            images = [Image.open(p) for p in self.avatar_paths if os.path.exists(p)]
            if not images:
                messagebox.showerror("错误", "没有有效的头像图片")
                return
            
            img_per_row = 10
            img_size = (64, 64)  # 统一大小
            width, height = img_size
            
            num_images = len(images)
            num_rows = math.ceil(num_images / img_per_row)
            montage_width = width * img_per_row
            montage_height = height * num_rows
            
            montage = Image.new('RGB', (montage_width, montage_height), color='white')
            
            x_offset, y_offset = 0, 0
            for i, img in enumerate(images):
                try:
                    img = img.resize(img_size)
                    montage.paste(img, (x_offset, y_offset))
                    x_offset += width
                    if (i + 1) % img_per_row == 0:
                        x_offset = 0
                        y_offset += height
                except Exception as e:
                    self.log(f"处理图片时出错: {e}")
                    continue
            
            output_path = 'avatar_montage.png'
            montage.save(output_path)
            montage.show()
            self.log(f"头像墙已保存到 {output_path}")
            
        except Exception as e:
            self.log(f"创建头像墙失败: {e}")
    
    def open_send_message_dialog(self):
        """打开发送消息对话框"""
        if not itchat.instance.alive:
            messagebox.showerror("错误", "请先登录微信！")
            return
        
        dialog = SendMessageDialog(self.root, self.send_message_callback)
    
    def send_message_callback(self, name, message):
        """发送消息回调函数"""
        try:
            users = itchat.search_friends(name=name)
            if not users:
                self.log(f"未找到好友: {name}")
                return False
            
            target_user_name = users[0]['UserName']
            itchat.send(message, toUserName=target_user_name)
            self.log(f"已向 {name} 发送消息: {message}")
            time.sleep(2)
            return True
        except Exception as e:
            self.log(f"发送消息失败: {e}")
            return False

class SendMessageDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("发送消息")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 好友名称
        ttk.Label(frame, text="好友名称（备注名或昵称）:").pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 消息内容
        ttk.Label(frame, text="消息内容:").pack(anchor=tk.W, pady=(0, 5))
        self.message_text = tk.Text(frame, height=8, width=40)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="发送", command=self.send_message).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def send_message(self):
        name = self.name_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not name or not message:
            messagebox.showerror("错误", "请填写好友名称和消息内容！")
            return
        
        success = self.callback(name, message)
        if success:
            messagebox.showinfo("成功", "消息发送成功！")
            self.dialog.destroy()
        else:
            messagebox.showerror("失败", "消息发送失败！")

def main():
    root = tk.Tk()
    app = WeChatFriendsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
