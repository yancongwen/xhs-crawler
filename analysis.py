# -*- encoding:utf-8 -*-
import csv
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

from textrank4zh import TextRank4Keyword, TextRank4Sentence

tr4w = TextRank4Keyword()

with open(f'./downloads/result/chatgpt_hot.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    column_values = [row['content'] for row in reader]

content = '\n'.join(column_values)

# py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
tr4w.analyze(text=content, lower=True, window=2)

print('关键词：')
for item in tr4w.get_keywords(50, word_min_len=2):
    print(item.word, item.weight)

print()
print('关键短语：')
for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num=2):
    print(phrase)

# tr4s = TextRank4Sentence()
# tr4s.analyze(text=text, lower=True, source='all_filters')

# print()
# print('摘要：')
# for item in tr4s.get_key_sentences(num=3):
#     print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
