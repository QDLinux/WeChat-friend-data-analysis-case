import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import re

# 准备停用词列表 (可以网上找更全的)
stopwords = set(['的', '了', '我', '你', '他', '她', '是', '在', '不', '就', '都', '也', '还', '说', '这个', '那个', '一个', '什么', ' ',',','.', '，','。','?','？','!','！','~','…'])

def generate_signature_wordcloud(df, output_path='signature_wordcloud.png', font_path='simhei.ttf'): # 需要指定中文字体文件路径
    if df is None: return
    signatures = df['Signature'].dropna().astype(str)
    text = ' '.join(signatures)

    # 清洗文本，去除无关字符 (可选，已在获取数据时做了一部分)
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z ]', '', text) # 只保留中文、英文和空格

    # 分词
    word_list = jieba.lcut(text, cut_all=False)
    # 过滤停用词和单字
    meaningful_words = [word for word in word_list if word not in stopwords and len(word) > 1]
    words_text = ' '.join(meaningful_words)

    if not words_text:
        print("没有足够的有效词语生成词云。")
        return

    wc = WordCloud(
        font_path=font_path, # 指定中文字体文件路径
        background_color="white",
        max_words=200,
        width=800,
        height=400,
        stopwords=stopwords # WordCloud内部也可过滤
    )
    wc.generate(words_text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title('好友签名词云')
    plt.savefig(output_path)
    plt.show()
    print(f"签名词云图已保存到 {output_path}")

# --- 使用 ---
# friends_df = pd.read_csv('wechat_friends.csv')
# # 确保你有 simhei.ttf 字体文件，或者换成你系统有的中文字体路径
# generate_signature_wordcloud(friends_df, font_path='C:/Windows/Fonts/simhei.ttf') # Windows 示例路径
