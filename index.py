# -*- coding: utf-8 -*-

import csv
import json
import time
import requests
from bs4 import BeautifulSoup

request_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.xiaohongshu.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1"
}

# 失败重试机制, 重试次数为参数
def retry(func, retry_times=3):
    def wrapper(*args, **kwargs):
        for i in range(retry_times):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                print(f'第{i+1}次请求失败, {e}')
                time.sleep(1)
    return wrapper

def get_note_details(node_id):
    noteUrl = f'https://www.xiaohongshu.com/explore/{node_id}'
    response = requests.get(noteUrl, headers=request_headers, timeout=10)
    response.encoding = response.apparent_encoding

    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    json_str = soup.find(attrs={'type': 'application/ld+json'}).text

    # 去除换行 等字符 不然 json无法解析 ,Windows 正常 ，Linux 异常
    json_str = json_str.replace('\n', '').replace('\r\n', '')
    result = json.loads(json_str, strict=False)
    if result['name'] != '':
        return result
    else:
        raise Exception('获取详情失败：' + str(response))

def get_page(page_id, cursor='', sort_by='hot'):
    # 请求列表
    url = 'https://www.xiaohongshu.com/web_api/sns/v3/page/notes'
    params = {
        'page_size': 20,
        'sort': sort_by,
        'page_id': page_id,
        'cursor': cursor,
        'sid': ''
    }
    headers = {
        'authority': 'www.xiaohongshu.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': 'smidV2=202204232153470815582356eb14689cc3de5c1e9509c700d854701c3e3a830; gid.sig=J51gqQITVoxM93_so_lXzHqIjeEsRkRzwnpCG-HeHF4; gid.sign.sig=c3QsgEsA_7IIMWY5_glVUzb3NYboY2AOn4vAAIAyu28; gid.ss=gSMQ9UOnDuZwH2oRGJG6BW6e4grs67TaYpnrW+8Wmd2azBbPYqKXIdsuljVz7UBg; timestamp2=1673265619526e4926c09daf76250bf9aa1ed5c6196f6faa2de07c82866f657; timestamp2.sig=O7AvEb24cf7yh5PwyqhN_au9q62nBL_3BNgT9Ff3504; xhsTrackerId=2fc58f61-b4e6-4736-b3c3-696fcbe0ef62; xhsTrackerId.sig=H52BZu6eM9xIkZTwMYc8r8Jp282ITn1Oa7Y2c41H2B8; a1=18612f30083g3ag1rrkgq76869imyxeub8hc88kz730000246697; webId=14e17cb02fbef4963ab87952fd4e3b45; gid=yYKyJiq8JiD0yYKyJiq88YYTYqkq0kyFFTkAxuWWKYKj3Sq86vCd7Y888J4KKjW8iKjD242j; gid.sign=oB2LoOOCblZWcXwhc2Vs2OyJQNU=; xhsTracker=url=explore&searchengine=google; xhsTracker.sig=MRMGzEloSNQs_DaToApEc',
        'pragma': 'no-cache',
        'referer': 'https://www.xiaohongshu.com/explore',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    response = requests.get(url, params=params, headers=headers)

    try:
        response.raise_for_status()
        notes = response.json()['data']['notes']
        next_cursor = response.json()['data']['cursor']
        has_more = response.json()['data']['has_more']
        return {'notes': notes, 'next_cursor': next_cursor, 'has_more': has_more}
    except:
        print(response)
        raise Exception('请求接口失败')

def get_notes(page_id, file_name, min_size=10000, sort_by='hot'):
    # 获取笔记列表
    has_more = True
    next_cursor = ''
    success_count = 0
    failed_count = 0
    page_count = 0
    with open(f'downloads/{file_name}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'title', 'content', 'likes', 'collects', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while has_more and success_count < min_size:
            page_count += 1
            list_result = retry(get_page, 3)(page_id, next_cursor, sort_by)
            notes = list_result['notes']
            next_cursor = list_result['next_cursor']
            if next_cursor is not None:
                has_more = list_result['has_more']

            print(f'第{page_count}页')
            for note in notes:
                if note['type'] != 'video':
                    detail = retry(get_note_details, 3)(note['id'])
                    if detail is not None:
                        success_count += 1
                        title = detail['name']
                        content = detail['description']
                        date = detail['datePublished']
                        likes = note['likes']
                        collects = note['collects']
                        # 存储至 CSV 文件中
                        writer.writerow({'id': note['id'], 'title': title, 'content': content, 'likes': likes, 'collects': collects, 'date': date})
                        print(f'成功{success_count}条')
                    else:
                        failed_count += 1
                        print('爬取失败: ' + note['id'])
    print(f'爬取完成，共{success_count}条，失败{failed_count}条')

get_notes('62b20313e35fd70001011700', 'AIGC_hot', 1000, 'hot')
