import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def crawl_nia():
    """抓取国家移民管理局新闻"""
    url = "https://www.nia.gov.cn/n741440/n741547/index.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        
        # 尝试多种可能的选择器适配网站结构
        items = soup.select('.news-list li a') or soup.select('.list li a') or soup.select('a[title]')
        
        for item in items[:10]:  # 只取前10条
            try:
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                # 过滤无效数据
                if not title or len(title) < 10 or 'javascript' in link.lower():
                    continue
                
                # 补全链接
                if link and not link.startswith('http'):
                    link = 'https://www.nia.gov.cn' + link
                
                news_list.append({
                    'title': title,
                    'link': link,
                    'source': '国家移民管理局',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            except:
                continue
                
        return news_list
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def save_data(all_news):
    """保存数据到JSON文件"""
    # 确保目录存在
    os.makedirs('data', exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'data/news_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    # 同时更新最新数据文件供网页读取
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"已保存 {len(all_news)} 条新闻到 {filename}")

def main():
    print(f"开始抓取: {datetime.now()}")
    
    all_news = []
    
    # 抓取国家移民管理局
    nia_news = crawl_nia()
    all_news.extend(nia_news)
    print(f"国家移民管理局: {len(nia_news)} 条")
    
    save_data(all_news)
    print("完成!")

if __name__ == '__main__':
    main()
