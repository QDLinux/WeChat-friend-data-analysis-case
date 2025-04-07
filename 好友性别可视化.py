import matplotlib.pyplot as plt
import pandas as pd

# 设置中文字体，否则matplotlib会显示乱码
plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题

def visualize_gender(df, output_path='gender_distribution.png'):
    if df is None: return
    gender_counts = df['Sex'].value_counts()
    gender_labels = {1: '男性', 2: '女性', 0: '未知'}
    labels = [gender_labels.get(x, '未知') for x in gender_counts.index]
    sizes = gender_counts.values

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral', 'lightgrey'])
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('微信好友性别分布')
    plt.savefig(output_path)
    plt.show() # 直接显示图表
    print(f"性别分布图已保存到 {output_path}")

# --- 使用 ---
# friends_df = pd.read_csv('wechat_friends.csv')
# visualize_gender(friends_df)
