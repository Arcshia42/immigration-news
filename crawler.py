import requests
from bs4 import BeautifulSoup
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def crawl_iom_rss():
    """抓取IOM RSS"""
    url = "https://www.iom.int/rss/news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        root = ET.fromstring(response.content)
        news_list = []
        
        for item in root.findall('.//item')[:5]:
            try:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                date = datetime.now().strftime('%Y-%m-%d')
                
                if title and len(title) > 10:
                    news_list.append({
                        'title': f"[IOM] {title}",
                        'link': link,
                        'source': '国际移民组织(IOM)',
                        'date': date
                    })
            except:
                continue
        
        print(f"IOM: {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"IOM失败: {e}")
        return []

def crawl_unhcr_rss():
    """抓取联合国难民署RSS（替代Reuters）"""
    url = "https://www.unhcr.org/news-feed.xml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        root = ET.fromstring(response.content)
        news_list = []
        
        for item in root.findall('.//item')[:5]:
            try:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                date = datetime.now().strftime('%Y-%m-%d')
                
                if title and len(title) > 10:
                    news_list.append({
                        'title': f"[UNHCR] {title}",
                        'link': link,
                        'source': '联合国难民署',
                        'date': date
                    })
            except:
                continue
        
        print(f"UNHCR: {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"UNHCR失败: {e}")
        return []

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
    
    all_news.extend(crawl_iom_rss())
    all_news.extend(crawl_unhcr_rss())
    all_news.extend(crawl_nia())
    
    save_data(all_news)
    print("完成!")

if __name__ == '__main__':
    main()
