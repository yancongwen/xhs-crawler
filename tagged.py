import time
import openai
import csv
import json

openai.api_type = "azure"
openai.api_key = "xxx"
openai.api_base = "https://seedlings.openai.azure.com"
openai.api_version = "2023-03-15-preview"

# 失败重试机制, 重试次数为参数
def retry(func, retry_times=3):
    def wrapper(*args, **kwargs):
        for i in range(retry_times):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                print(f'第{i+1}次请求失败, {e}')
    return wrapper

def get_tags(row):
    text = row['title'] + '\n' + row['content']
    response_content = ''
    completion = openai.ChatCompletion.create(
        engine='gpt-35-turbo',
        request_timeout=30,
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant.'
            },
            {
                'role': 'user',
                'content': '现在我有一批关于AI、或者人工智能的博文，需要你帮我标注其归属的应用领域。请以符合JSON规范的格式返回，返回结果示例：["标签1", "标签2"]，标签数量最多三个。注意，如果博文内容不是属于AI应用的请返回空数组。下面是一些已有的标签，你可以从这些标签中选择，也可以根据内容生成更适合的标签。已有标签：创作、教育、学习、旅游、法律、金融、医疗、写作、图像生成、情感、娱乐、社交、办公。'
            },
            {
                'role': 'assistant',
                'content': '好的，请发送第一条博文内容发给我。'
            },
            {
                'role': 'user',
                'content': '一半的学生用ChatGPT写出来论文给我读，连文风都一摸一样。 读起来逻辑清晰，不能说语言表达出彩但是足够流畅，信息量足够没有废话。 比他们自己写的好读多了 	 我读的津津有味，多么流畅的改论文体验'
            },
            {
                'role': 'assistant',
                'content': '["写作"]'
            },
            {
                'role': 'user',
                'content': text
            }
        ]
    )
    response_content = completion.choices[0].message.content
    try:
        result = json.loads(response_content)
        if isinstance(result, list) and all(isinstance(item, str) for item in result):
            return result
        else:
            raise Exception('返回结果不是数组')
    except Exception as e:
        print(f'{response_content}')
        print(f'error: {e}')
        return []

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows

def start(field_name):
    rows = read_csv(f'./downloads/{field_name}.csv')
    count = 0
    with open(f'./result/{field_name}_with_tags.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['id', 'title', 'content', 'likes', 'collects', 'date', 'tags'])
        writer.writeheader()
        for index, row in enumerate(rows):
            if 'tags' not in row or row['tags'] is None or row['tags'] == '':
                tags = retry(get_tags)(row)
                if type(tags) == list and len(tags) > 0:
                    row['tags'] = '、'.join(tags)
                    print(f"{index} -> {row['tags']}")
                    writer.writerow(row)
                else:
                    count += 1
                    print(f"{index} -> error")
                    writer.writerow(row)
            else:
                # print(f"{index} -> 跳过")
                writer.writerow(row)
    print(f'失败条数{count}')

start('result')
