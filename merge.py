import pandas as pd
import glob

# 获取所有 CSV 文件的文件名
csv_files = glob.glob("./downloads/*.csv")

# 读取所有 CSV 文件并合并为一个 DataFrame
df_list = []
for f in csv_files:
    # 读取 CSV 文件
    df = pd.read_csv(f)
    # 输出文件名和记录数量
    print(f"{f}: {len(df)} records")
    # 将 DataFrame 添加到列表中
    df_list.append(df)

# 合并所有 DataFrame
df = pd.concat(df_list)

print(f"Total: {len(df)} records")
# 根据 ID 去重
df.drop_duplicates(subset="id", inplace=True)
print(f"Total after drop duplicates: {len(df)} records")

# 将合并后的 DataFrame 保存为 CSV 文件
df.to_csv("./result/result.csv", index=False)
