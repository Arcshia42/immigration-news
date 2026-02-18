import requests
from bs4 import BeautifulSoup
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def crawl_google_news():
    """抓取Google News移民相关新闻"""
    # Google News RSS搜索：移民、难民、签证相关
    queries = [
        "immigration+refugee+visa",
        "migration+asylum+border",
        "migrant+deportation+citizenship"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_news = []
    seen_titles = set()  # 去重
    
    for query in queries:
        try:
            # Google News RSS
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            print(f"抓取Google News: {query}")
            response = requests.get(url, headers=headers, timeout=30)
            
            # 解析RSS
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item'):
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    source_elem = item.find('source')
                    
                    title = title_elem.text if title_elem is not None else ''
                    link = link_elem.text if link_elem is not None else ''
                    source = source_elem.text if source_elem is not None else 'Google News'
                    
                    # 去重
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    
                    if title and len(title) > 10:
                        all_news.append({
                            'title': f"[{source}] {title}",
                            'link': link,
                            'source': f'Google News - {source}',
                            'date': datetime.now().strftime('%Y-%m-%d')
                        })
                        
                        if len(all_news) >= 10:
                            break
                            
                except:
                    continue
            
            if len(all_news) >= 10:
                break
                
        except Exception as e:
            print(f"Google News {query} 失败: {e}")
            continue
    
    print(f"Google News: {len(all_news)} 条")
    return all_news

def crawl_nia():
    """抓取中国国家移民管理局"""
    url = "https://www.nia.gov.cn/n741440/n741547/index.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    keywords = ['移民', '出入境', '签证', '护照', '边检', '口岸', '外国人', '居留']
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        items = soup.select('.news-list li a') or soup.select('.list li a')
        
        for item in items:
            try:
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                if not title or len(title) < 5:
                    continue
                
                if not any(kw in title for kw in keywords):
                    continue
                
                if link and not link.startswith('http'):
                    link = 'https://www.nia.gov.cn' + link
                
                news_list.append({
                    'title': f"[NIA] {title}",
                    'link': link,
                    'source': '中国国家移民管理局',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
                if len(news_list) >= 3:
                    break
            except:
                continue
        
        print(f"NIA: {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"NIA失败: {e}")
        return []

def save_data(all_news):
    os.makedirs('data', exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    
    with open(f'data/news_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n总计: {len(all_news)} 条")

def main():
    print(f"开始: {datetime.now()}\n")
    all_news = []
    
    all_news.extend(crawl_google_news())
    all_news.extend(crawl_nia())
    
    save_data(all_news)
    print("完成!")

if __name__ == '__main__':
    main()
