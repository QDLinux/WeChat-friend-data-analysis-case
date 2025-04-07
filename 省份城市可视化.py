from pyecharts import options as opts
from pyecharts.charts import Map
import pandas as pd

def visualize_province(df, output_path='province_distribution.html'):
    if df is None: return
    # 清理空值和无效值
    df_filtered = df[df['Province'].notna() & (df['Province'] != '')]
    province_counts = df_filtered['Province'].value_counts().reset_index()
    province_counts.columns = ['province', 'count']
    data_pair = [list(z) for z in zip(province_counts['province'], province_counts['count'])]

    c = (
        Map()
        .add("好友数量", data_pair, "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="微信好友省份分布"),
            visualmap_opts=opts.VisualMapOpts(max_=int(province_counts['count'].max()), is_piecewise=False), # 根据最大值调整
        )
        .render(output_path)
    )
    print(f"省份分布地图已保存到 {output_path}")
    # 可以考虑在GUI中嵌入浏览器控件显示html，或直接打开文件

# --- 使用 ---
# friends_df = pd.read_csv('wechat_friends.csv')
# visualize_province(friends_df)
# 城市可视化类似，但地图需要选择 'china-cities' 或具体省份地图，数据处理更复杂
