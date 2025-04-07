import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import queue # 用于线程间通信
import pandas as pd
import os

# 假设 actions.py 包含了之前定义的各种功能函数
import actions # 需要创建这个文件并放入功能代码

class WeChatAnalyzerApp:
    def __init__(self, master):
        self.master = master
        master.title("微信好友数据分析工具")
        master.geometry("800x600")

        self.message_queue = queue.Queue() # 用于从工作线程接收消息更新UI

        # --- 数据存储 ---
        self.friends_df = None
        self.avatar_paths = []

        # --- UI 控件 ---
        self.setup_ui()

        # --- 启动检查队列的循环 ---
        self.master.after(100, self.process_queue)

    def setup_ui(self):
        # --- 控制面板 (左侧) ---
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(control_frame, text="登录微信", command=self.run_in_thread(actions.login_wechat)).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="获取/刷新好友数据", command=self.run_in_thread(self.load_friend_data)).pack(pady=5, fill=tk.X)
        ttk.Button(control_frame, text="保存好友数据到CSV", command=self.save_data).pack(pady=5, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(pady=10, fill=tk.X)

        ttk.Label(control_frame, text="数据分析与可视化:").pack(pady=5)
        ttk.Button(control_frame, text="性别分布", command=self.run_in_thread(self.show_gender_viz)).pack(pady=2, fill=tk.X)
        ttk.Button(control_frame, text="省份地图", command=self.run_in_thread(self.show_province_viz)).pack(pady=2, fill=tk.X)
        # ... 其他可视化按钮 ...
        ttk.Button(control_frame, text="签名词云", command=self.run_in_thread(self.show_wordcloud_viz)).pack(pady=2, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(pady=10, fill=tk.X)

        ttk.Label(control_frame, text="头像处理:").pack(pady=5)
        ttk.Button(control_frame, text="下载头像", command=self.run_in_thread(self.download_avatars_action)).pack(pady=2, fill=tk.X)
        ttk.Button(control_frame, text="生成头像墙", command=self.run_in_thread(self.show_montage_viz)).pack(pady=2, fill=tk.X)
        ttk.Button(control_frame, text="人脸检测分析", command=self.run_in_thread(self.analyze_faces_action)).pack(pady=2, fill=tk.X)

        # --- 显示区域 (右侧) ---
        self.display_frame = ttk.Frame(self.master, padding="10")
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 使用 Notebook (选项卡) 来切换不同的显示内容
        self.notebook = ttk.Notebook(self.display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 日志/文本输出 Tab
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text='日志输出')
        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 图表/图片显示 Tab (可以有多个)
        self.image_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text='图表/图像')
        self.image_label = ttk.Label(self.image_tab) # 用于显示图片
        self.image_label.pack(pady=10)

        # 可以在这里添加用于嵌入 Matplotlib 图表的 Canvas

    def log(self, message):
        """线程安全地向日志文本框添加消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END) # 滚动到底部

    def process_queue(self):
        """处理来自工作线程的消息"""
        try:
            message = self.message_queue.get_nowait()
            # 根据消息类型执行操作，例如更新UI
            if isinstance(message, str):
                self.log(message)
            elif isinstance(message, dict) and 'type' in message:
                msg_type = message['type']
                if msg_type == 'login_status':
                    self.log(f"登录状态: {'成功' if message['success'] else '失败'}")
                elif msg_type == 'friend_data':
                    self.friends_df = message['data']
                    self.log(f"成功获取 {len(self.friends_df)} 位好友数据。")
                elif msg_type == 'image_display':
                    self.show_image_on_tab(message['path'])
                    self.notebook.select(self.image_tab) # 切换到图像Tab
                elif msg_type == 'html_display':
                    # Pyecharts 生成 html 后，可以在这里用 webbrowser 打开
                    import webbrowser
                    webbrowser.open(message['path'])
                    self.log(f"已在浏览器中打开: {message['path']}")
                elif msg_type == 'avatar_paths':
                    self.avatar_paths = message['data']
                    self.log(f"获取到 {len(self.avatar_paths)} 个头像路径。")
                elif msg_type == 'face_analysis_result':
                    result = message['data']
                    self.log(f"人脸分析完成: 总数={result['total']}, 人脸={result['faces']}, 无人脸={result['no_faces']}, 错误={result['errors']}")

                # 可以添加更多消息类型处理...
            else:
                 self.log(f"未知消息类型: {message}")

        except queue.Empty:
            pass # 队列为空，什么都不做
        finally:
            # 持续检查队列
            self.master.after(100, self.process_queue)

    def run_in_thread(self, target_func, *args):
        """返回一个启动线程运行目标函数的函数"""
        def wrapper():
            # 可以加一个简单的防止重复点击的机制 (可选)
            thread = threading.Thread(target=target_func, args=args, daemon=True)
            thread.start()
        return wrapper

    # --- Action Wrappers (调用 actions.py 中的函数，并通过 queue 返回结果) ---

    def load_friend_data(self):
        self.log("开始获取好友数据...")
        # 假设 actions.get_friends_info() 返回 DataFrame 或 None
        df = actions.get_friends_info() # 这需要能访问 itchat 实例
        if df is not None:
            self.message_queue.put({'type': 'friend_data', 'data': df})
        else:
            self.message_queue.put("获取好友数据失败。")

    def save_data(self):
        if self.friends_df is None:
            messagebox.showwarning("提示", "请先获取好友数据！")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                                  filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filepath:
            try:
                actions.save_friends_to_file(self.friends_df, filepath)
                self.log(f"数据已保存到: {filepath}")
            except Exception as e:
                self.log(f"保存失败: {e}")
                messagebox.showerror("错误", f"保存文件失败:\n{e}")

    def show_gender_viz(self):
        if self.friends_df is None:
            self.log("无好友数据，无法生成性别分布图。")
            return
        self.log("正在生成性别分布图...")
        output_path = 'temp_gender_distribution.png' # 临时文件
        try:
            actions.visualize_gender(self.friends_df, output_path) # 让它保存但不显示 plt.show()
            self.message_queue.put({'type': 'image_display', 'path': output_path})
        except Exception as e:
            self.log(f"生成性别图失败: {e}")

    def show_province_viz(self):
        if self.friends_df is None:
             self.log("无好友数据，无法生成省份地图。")
             return
        self.log("正在生成省份分布地图...")
        output_path = 'temp_province_distribution.html'
        try:
            actions.visualize_province(self.friends_df, output_path)
            # 对于html，选择在浏览器打开
            self.message_queue.put({'type': 'html_display', 'path': output_path})
        except Exception as e:
            self.log(f"生成省份地图失败: {e}")


    def show_wordcloud_viz(self):
        if self.friends_df is None:
             self.log("无好友数据，无法生成词云。")
             return
        self.log("正在生成签名词云...")
        output_path = 'temp_signature_wordcloud.png'
        font_path = actions.find_font() # 需要一个函数找到可用的中文字体
        if not font_path:
             self.log("错误：未找到可用的中文字体，无法生成词云。")
             messagebox.showerror("错误", "未找到中文字体！请确保系统中有 SimHei 或其他常见中文字体，或在代码中指定路径。")
             return
        try:
            actions.generate_signature_wordcloud(self.friends_df, output_path, font_path=font_path)
            self.message_queue.put({'type': 'image_display', 'path': output_path})
        except Exception as e:
            self.log(f"生成词云失败: {e}")


    def download_avatars_action(self):
         if self.friends_df is None:
             self.log("无好友数据，无法下载头像。")
             return
         self.log("开始下载头像...")
         paths = actions.download_avatars(self.friends_df)
         self.message_queue.put({'type': 'avatar_paths', 'data': paths})
         self.log("头像下载任务完成。") # 注意下载是异步的


    def show_montage_viz(self):
        if not self.avatar_paths:
             self.log("请先下载头像。")
             return
        self.log("正在生成头像墙...")
        output_path = 'temp_avatar_montage.png'
        try:
            actions.create_avatar_montage(self.avatar_paths, output_path)
            self.message_queue.put({'type': 'image_display', 'path': output_path})
        except Exception as e:
            self.log(f"生成头像墙失败: {e}")


    def analyze_faces_action(self):
         if not self.avatar_paths:
              self.log("请先下载头像。")
              return
         self.log("开始进行人脸检测分析...")
         results = actions.analyze_faces_in_avatars(self.avatar_paths)
         self.message_queue.put({'type': 'face_analysis_result', 'data': results})


    def show_image_on_tab(self, image_path):
        """在图片标签页显示图片"""
        try:
            img = Image.open(image_path)
            # 调整图片大小以适应标签页 (可选)
            img.thumbnail((self.image_tab.winfo_width() - 20, self.image_tab.winfo_height() - 40)) # 减去一些padding
            photo = ImageTk.PhotoImage(img)

            self.image_label.config(image=photo)
            self.image_label.image = photo # 保持引用，防止被垃圾回收
            self.log(f"已显示图片: {os.path.basename(image_path)}")
        except Exception as e:
            self.log(f"加载图片失败 {image_path}: {e}")
            messagebox.showerror("错误", f"无法加载或显示图片:\n{e}")


if __name__ == '__main__':
    # 在 main.py 中运行
    root = tk.Tk()
    app = WeChatAnalyzerApp(root)
    root.mainloop()

    # 程序退出前尝试登出微信 (如果需要)
    # try:
    #     if actions.is_wechat_logged_in(): # 需要一个判断是否登录的函数
    #         actions.logout_wechat()
    # except Exception as e:
    #     print(f"尝试登出微信时出错: {e}")
