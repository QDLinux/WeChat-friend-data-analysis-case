import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import math
from PIL import Image
import jieba
from wordcloud import WordCloud
import re
import webbrowser
from pyecharts import options as opts
from pyecharts.charts import Map

class WeChatDataAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("微信好友数据分析工具")
        self.root.geometry("900x700")
        
        self.friends_df = None
        self.avatar_paths = []
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 停用词
        self.stopwords = set(['的', '了', '我', '你', '他', '她', '是', '在', '不', '就', '都', '也', '还', '说', 
                            '这个', '那个', '一个', '什么', ' ', ',', '.', '，', '。', '?', '？', '!', '！', '~', '…'])\
        
        self.create_widgets()\
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="微信好友数据分析工具", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 数据加载区域
        load_frame = ttk.LabelFrame(main_frame, text="数据加载", padding="10")
        load_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(load_frame, text="加载CSV文件", command=self.load_csv).grid(row=0, column=0, padx=5)
        ttk.Button(load_frame, text="加载Excel文件", command=self.load_excel).grid(row=0, column=1, padx=5)
        ttk.Button(load_frame, text="生成示例数据", command=self.generate_sample_data).grid(row=0, column=2, padx=5)
        ttk.Button(load_frame, text="保存数据", command=self.save_data).grid(row=0, column=3, padx=5)
        
        # 数据信息显示
        info_frame = ttk.LabelFrame(main_frame, text="数据信息", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, text="未加载数据", foreground="red")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
        # 分析功能区域
        analysis_frame = ttk.LabelFrame(main_frame, text="数据分析功能", padding="10")
        analysis_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行按钮
        ttk.Button(analysis_frame, text="性别分布图", command=self.show_gender_analysis).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(analysis_frame, text="省份分布图", command=self.show_province_analysis).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(analysis_frame, text="城市分布图", command=self.show_city_analysis).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(analysis_frame, text="签名词云", command=self.show_wordcloud).grid(row=0, column=3, padx=5, pady=5)
        
        # 第二行按钮
        ttk.Button(analysis_frame, text="头像墙", command=self.create_avatar_montage).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(analysis_frame, text="数据统计", command=self.show_statistics).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(analysis_frame, text="导出报告", command=self.export_report).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(analysis_frame, text="清空日志", command=self.clear_log).grid(row=1, column=3, padx=5, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_info_label(self):
        """更新数据信息标签"""
        if self.friends_df is not None:
            total = len(self.friends_df)
            male = len(self.friends_df[self.friends_df['Sex'] == 1]) if 'Sex' in self.friends_df.columns else 0
            female = len(self.friends_df[self.friends_df['Sex'] == 2]) if 'Sex' in self.friends_df.columns else 0
            self.info_label.config(text=f"已加载 {total} 条数据 (男:{male}, 女:{female})", foreground="green")
        else:
            self.info_label.config(text="未加载数据", foreground="red")
    
    def load_csv(self):
        """加载CSV文件"""
        filename = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.friends_df = pd.read_csv(filename, encoding='utf-8-sig')
                self.log(f"成功加载CSV文件: {filename}")
                self.log(f"数据行数: {len(self.friends_df)}")
                self.log(f"数据列: {list(self.friends_df.columns)}")
                self.update_info_label()
            except Exception as e:
                self.log(f"加载CSV文件失败: {e}")
                messagebox.showerror("错误", f"加载CSV文件失败:\n{e}")
    
    def load_excel(self):
        """加载Excel文件"""
        filename = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx"), ("Excel files", "*.xls"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.friends_df = pd.read_excel(filename)
                self.log(f"成功加载Excel文件: {filename}")
                self.log(f"数据行数: {len(self.friends_df)}")
                self.log(f"数据列: {list(self.friends_df.columns)}")
                self.update_info_label()
            except Exception as e:
                self.log(f"加载Excel文件失败: {e}")
                messagebox.showerror("错误", f"加载Excel文件失败:\n{e}")
    
    def generate_sample_data(self):
        """生成示例数据"""
        self.log("正在生成示例数据...")
        
        np.random.seed(42)
        n_friends = 200
        
        provinces = ['北京', '上海', '广东', '浙江', '江苏', '山东', '河南', '四川', '湖北', '湖南', 
                    '福建', '安徽', '河北', '陕西', '重庆', '天津', '辽宁', '江西', '广西', '云南']
        cities = ['北京', '上海', '深圳', '杭州', '南京', '济南', '郑州', '成都', '武汉', '长沙',
                 '福州', '合肥', '石家庄', '西安', '重庆', '天津', '沈阳', '南昌', '南宁', '昆明']
        
        signatures = [
            '生活就像一盒巧克力', '做最好的自己', '努力工作，快乐生活', '心若向阳，无畏悲伤',
            '简单生活，快乐工作', '每天都是新的开始', '保持微笑', '相信美好的事情即将发生',
            '做一个温暖的人', '岁月静好', '愿你被这个世界温柔以待', '不忘初心，方得始终',
            '生活需要仪式感', '做自己的太阳', '愿所有美好如期而至', '平凡而不平庸',
            '热爱生活，拥抱未来', '做一个有趣的人', '保持好奇心', '用心生活'
        ]
        
        data = {
            'UserName': [f'user_{i+1}' for i in range(n_friends)],
            'NickName': [f'好友{i+1}' for i in range(n_friends)],
            'RemarkName': [f'备注{i+1}' if i % 3 == 0 else '' for i in range(n_friends)],
            'Sex': np.random.choice([0, 1, 2], n_friends, p=[0.1, 0.45, 0.45]),
            'Province': np.random.choice(provinces, n_friends),
            'City': np.random.choice(cities, n_friends),
            'Signature': np.random.choice(signatures, n_friends)
        }
        
        self.friends_df = pd.DataFrame(data)
        self.log(f"已生成 {len(self.friends_df)} 条示例数据")
        self.update_info_label()
        messagebox.showinfo("成功", f"已生成 {len(self.friends_df)} 条示例数据")
    
    def save_data(self):
        """保存数据"""
        if self.friends_df is None:
            messagebox.showerror("错误", "没有数据可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存数据文件",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            try:
                if filename.endswith('.xlsx'):
                    self.friends_df.to_excel(filename, index=False)
                else:
                    self.friends_df.to_csv(filename, index=False, encoding='utf-8-sig')
                self.log(f"数据已保存到: {filename}")
                messagebox.showinfo("成功", "数据保存成功")
            except Exception as e:
                self.log(f"保存失败: {e}")
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def show_gender_analysis(self):
        """显示性别分布分析"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        if 'Sex' not in self.friends_df.columns:
            messagebox.showerror("错误", "数据中没有性别信息")
            return
        
        try:
            gender_counts = self.friends_df['Sex'].value_counts()
            gender_labels = {1: '男性', 2: '女性', 0: '未知'}
            labels = [gender_labels.get(x, '未知') for x in gender_counts.index]
            sizes = gender_counts.values
            colors = ['skyblue', 'lightcoral', 'lightgrey']
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # 饼图
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.set_title('好友性别分布')
            ax1.axis('equal')
            
            # 柱状图
            ax2.bar(labels, sizes, color=colors)
            ax2.set_title('好友性别统计')
            ax2.set_ylabel('人数')
            
            plt.tight_layout()
            plt.savefig('gender_distribution.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            self.log("性别分布图已生成并显示")
        except Exception as e:
            self.log(f"生成性别分布图失败: {e}")
            messagebox.showerror("错误", f"生成性别分布图失败: {e}")
    
    def show_province_analysis(self):
        """显示省份分布分析"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        if 'Province' not in self.friends_df.columns:
            messagebox.showerror("错误", "数据中没有省份信息")
            return
        
        try:
            # 清理数据
            df_filtered = self.friends_df[self.friends_df['Province'].notna() & (self.friends_df['Province'] != '')]
            if len(df_filtered) == 0:
                messagebox.showwarning("警告", "没有有效的省份数据")
                return
            
            province_counts = df_filtered['Province'].value_counts().reset_index()
            province_counts.columns = ['province', 'count']
            
            # 生成地图
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
            
            # 生成柱状图
            top_provinces = province_counts.head(15)
            plt.figure(figsize=(12, 6))
            bars = plt.bar(range(len(top_provinces)), top_provinces['count'], color='steelblue')
            plt.xlabel('省份')
            plt.ylabel('好友数量')
            plt.title('好友省份分布（前15名）')
            plt.xticks(range(len(top_provinces)), top_provinces['province'], rotation=45)
            
            # 在柱子上显示数值
            for bar, value in zip(bars, top_provinces['count']):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(value), ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig('province_distribution.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # 打开地图文件
            webbrowser.open('province_distribution.html')
            
            self.log("省份分布图已生成并显示")
            self.log("省份分布地图已保存到 province_distribution.html")
        except Exception as e:
            self.log(f"生成省份分布图失败: {e}")
            messagebox.showerror("错误", f"生成省份分布图失败: {e}")
    
    def show_city_analysis(self):
        """显示城市分布分析"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        if 'City' not in self.friends_df.columns:
            messagebox.showerror("错误", "数据中没有城市信息")
            return
        
        try:
            df_filtered = self.friends_df[self.friends_df['City'].notna() & (self.friends_df['City'] != '')]
            if len(df_filtered) == 0:
                messagebox.showwarning("警告", "没有有效的城市数据")
                return
            
            city_counts = df_filtered['City'].value_counts().head(20)
            
            plt.figure(figsize=(14, 8))
            bars = plt.bar(range(len(city_counts)), city_counts.values, color='lightgreen')
            plt.xlabel('城市')
            plt.ylabel('好友数量')
            plt.title('好友城市分布（前20名）')
            plt.xticks(range(len(city_counts)), city_counts.index, rotation=45)
            
            # 在柱子上显示数值
            for bar, value in zip(bars, city_counts.values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(value), ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig('city_distribution.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            self.log("城市分布图已生成并显示")
        except Exception as e:
            self.log(f"生成城市分布图失败: {e}")
            messagebox.showerror("错误", f"生成城市分布图失败: {e}")
    
    def show_wordcloud(self):
        """生成签名词云"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        if 'Signature' not in self.friends_df.columns:
            messagebox.showerror("错误", "数据中没有签名信息")
            return
        
        try:
            signatures = self.friends_df['Signature'].dropna().astype(str)
            if len(signatures) == 0:
                messagebox.showwarning("警告", "没有有效的签名数据")
                return
            
            text = ' '.join(signatures)
            text = re.sub(r'[^\\u4e00-\\u9fa5a-zA-Z ]', '', text)
            
            # 分词
            word_list = jieba.lcut(text, cut_all=False)
            meaningful_words = [word for word in word_list if word not in self.stopwords and len(word) > 1]
            words_text = ' '.join(meaningful_words)
            
            if not words_text:
                messagebox.showwarning("警告", "没有足够的有效词语生成词云")
                return
            
            # 尝试使用系统字体
            font_path = None
            if os.name == 'nt':  # Windows
                font_paths = ['C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/msyh.ttc']
                for path in font_paths:
                    if os.path.exists(path):
                        font_path = path
                        break
            
            wc = WordCloud(
                font_path=font_path,
                background_color="white",
                max_words=200,
                width=800,
                height=400,
                stopwords=self.stopwords
            )
            wc.generate(words_text)
            
            plt.figure(figsize=(12, 6))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            plt.title('好友签名词云')
            plt.tight_layout()
            plt.savefig('signature_wordcloud.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            self.log("签名词云图已生成并显示")
        except Exception as e:
            self.log(f"生成词云失败: {e}")
            messagebox.showerror("错误", f"生成词云失败: {e}")
    
    def create_avatar_montage(self):
        """创建头像墙（使用默认头像）"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        try:
            # 由于没有真实头像，创建彩色方块代替
            num_friends = min(len(self.friends_df), 100)  # 限制数量
            img_per_row = 10
            img_size = (64, 64)
            width, height = img_size
            
            num_rows = math.ceil(num_friends / img_per_row)
            montage_width = width * img_per_row
            montage_height = height * num_rows
            
            montage = Image.new('RGB', (montage_width, montage_height), color='white')
            
            # 生成随机颜色头像
            np.random.seed(42)
            colors = np.random.randint(0, 256, (num_friends, 3))
            
            x_offset, y_offset = 0, 0
            for i in range(num_friends):
                # 创建彩色方块
                color = tuple(colors[i])
                img = Image.new('RGB', img_size, color=color)
                
                montage.paste(img, (x_offset, y_offset))
                x_offset += width
                if (i + 1) % img_per_row == 0:
                    x_offset = 0
                    y_offset += height
            
            montage.save('avatar_montage.png')
            montage.show()
            
            self.log(f"头像墙已生成，包含 {num_friends} 个头像")
        except Exception as e:
            self.log(f"创建头像墙失败: {e}")
            messagebox.showerror("错误", f"创建头像墙失败: {e}")
    
    def show_statistics(self):
        """显示数据统计"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("数据统计报告")
            stats_window.geometry("500x400")
            
            text_widget = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 基本统计
            total = len(self.friends_df)
            stats_text = f"微信好友数据统计报告\n{'='*40}\n\n"
            stats_text += f"总好友数：{total}\n\n"
            
            # 性别统计
            if 'Sex' in self.friends_df.columns:
                male = len(self.friends_df[self.friends_df['Sex'] == 1])
                female = len(self.friends_df[self.friends_df['Sex'] == 2])
                unknown = len(self.friends_df[self.friends_df['Sex'] == 0])
                
                stats_text += "性别分布：\n"
                stats_text += f"- 男性：{male} ({male/total*100:.1f}%)\n"
                stats_text += f"- 女性：{female} ({female/total*100:.1f}%)\n"
                stats_text += f"- 未知：{unknown} ({unknown/total*100:.1f}%)\n\n"
            
            # 省份统计
            if 'Province' in self.friends_df.columns:
                province_stats = self.friends_df['Province'].value_counts().head(10)
                stats_text += "省份分布（前10名）：\n"
                for province, count in province_stats.items():
                    if pd.notna(province) and province != '':
                        stats_text += f"- {province}：{count}人 ({count/total*100:.1f}%)\n"
                stats_text += "\n"
            
            # 城市统计
            if 'City' in self.friends_df.columns:
                city_stats = self.friends_df['City'].value_counts().head(10)
                stats_text += "城市分布（前10名）：\n"
                for city, count in city_stats.items():
                    if pd.notna(city) and city != '':
                        stats_text += f"- {city}：{count}人 ({count/total*100:.1f}%)\n"
            
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)
            
            self.log("数据统计报告已显示")
        except Exception as e:
            self.log(f"生成统计报告失败: {e}")
            messagebox.showerror("错误", f"生成统计报告失败: {e}")
    
    def export_report(self):
        """导出分析报告"""
        if self.friends_df is None:
            messagebox.showerror("错误", "请先加载数据")
            return
        
        filename = filedialog.asksaveasfilename(
            title="导出报告",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("微信好友数据分析报告\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    total = len(self.friends_df)
                    f.write(f"总好友数：{total}\n\n")
                    
                    # 性别统计
                    if 'Sex' in self.friends_df.columns:
                        male = len(self.friends_df[self.friends_df['Sex'] == 1])
                        female = len(self.friends_df[self.friends_df['Sex'] == 2])
                        unknown = len(self.friends_df[self.friends_df['Sex'] == 0])
                        
                        f.write("性别分布：\n")
                        f.write(f"男性：{male} ({male/total*100:.1f}%)\n")
                        f.write(f"女性：{female} ({female/total*100:.1f}%)\n")
                        f.write(f"未知：{unknown} ({unknown/total*100:.1f}%)\n\n")
                    
                    # 省份统计
                    if 'Province' in self.friends_df.columns:
                        province_stats = self.friends_df['Province'].value_counts()
                        f.write("省份分布：\n")
                        for province, count in province_stats.items():
                            if pd.notna(province) and province != '':
                                f.write(f"{province}：{count}人 ({count/total*100:.1f}%)\n")
                
                self.log(f"分析报告已导出到：{filename}")
                messagebox.showinfo("成功", "报告导出成功")
            except Exception as e:
                self.log(f"导出报告失败: {e}")
                messagebox.showerror("错误", f"导出报告失败: {e}")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = WeChatDataAnalyzer(root)
    
    # 启动时显示使用说明
    messagebox.showinfo("使用说明", 
        "微信好友数据分析工具\n\n"
        "功能说明：\n"
        "1. 支持加载CSV和Excel格式的好友数据\n"
        "2. 可生成示例数据进行测试\n"
        "3. 提供性别、地区分布分析\n"
        "4. 支持签名词云生成\n"
        "5. 可导出分析报告\n\n"
        "数据格式要求：\n"
        "- Sex: 性别 (0:未知, 1:男, 2:女)\n"
        "- Province: 省份\n"
        "- City: 城市\n"
        "- Signature: 个性签名\n\n"
        "点击'生成示例数据'开始体验！")
    
    root.mainloop()

if __name__ == "__main__":
    main()