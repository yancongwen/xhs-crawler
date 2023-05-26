import csv
from collections import Counter

# 打开CSV文件并读取tags列
tags = []
with open('./result/result_with_tags.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['tags'] != '':
            tags += row['tags'].split('、')

with open(f'./result/result_with_tags_tag.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['tag'])
    writer.writeheader()
    for tag in tags:
        writer.writerow({'tag': tag})
