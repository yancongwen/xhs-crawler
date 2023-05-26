import csv
from collections import Counter

# 打开CSV文件并读取tags列
with open('./result/result_with_tags.csv', 'r') as f:
    reader = csv.DictReader(f)
    tags = []
    for row in reader:
        if row['tags'] != '':
            tags += row['tags'].split('、')

# 统计词频并输出
tag_counts = Counter(tags)

with open(f'./result/result_with_tags_statistics.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['tag', 'count'])
    writer.writeheader()
    for tag, count in tag_counts.most_common():
        writer.writerow({'tag': tag, 'count': count})
        print(f'{tag}: {count}')
