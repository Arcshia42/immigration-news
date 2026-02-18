import requests
from bs4 import BeautifulSoup
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def crawl_iom():
    """抓取国际移民组织(IOM)新闻"""
    url = "https://www.iom.int/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        
        # IOM新闻列表选择器
        items = soup.select('.views-row') or soup.select('.node--type-news') or soup.select('article')
        
        for item in items[:5]:
            try:
                title_tag = item.select_one('h2 a') or item.select_one('.field--name-title a') or item.select_one('a')
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                
                date_tag = item.select_one('.field--name-field-date') or item.select_one('time')
                date = date_tag.get_text(strip=True) if date_tag else datetime.now().strftime('%Y-%m-%d')
                
                if link and not link.startswith('http'):
                    link = 'https://www.iom.int' + link
                
                if len(title) < 10:
                    continue
                
                news_list.append({
                    'title': f"[IOM] {title}",
                    'link': link,
                    'source': '国际移民组织(IOM)',
                    'date': date
                })
                    
            except Exception as e:
                print(f"解析IOM单条失败: {e}")
                continue
                
        print(f"IOM: {len(news_list)} 条")
        return news_list
        
    except Exception as e:
        print(f"IOM抓取失败: {e}")
        return []

def crawl_reuters_rss():
    """抓取路透社RSS移民相关新闻"""
    url = "https://www.reuters.com/rssfeed/world/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    keywords = ['migration', 'migrant', 'immigration', 'immigrant', 'refugee', 'asylum', 'visa', 'border', 'deportation', 'citizenship']
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        root = ET.fromstring(response.content)
        
        news_list = []
        
        for item in root.findall('.//item'):
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                date_elem = item.find('pubDate')
                
                title = title_elem.text if title_elem is not None else ''
                link = link_elem.text if link_elem is not None else ''
                pub_date = date_elem.text if date_elem is not None else ''
                
                content = title.lower()
                if not any(keyword in content for keyword in keywords):
                    continue
                
                if pub_date:
                    try:
                        date_obj = datetime.strptime(pub_date[:16], '%a, %d %b %Y')
                        date = date_obj.strftime('%Y-%m-%d')
                    except:
                        date = datetime.now().strftime('%Y-%m-%d')
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
                
                if title and len(title) > 10:
                    news_list.append({
                        'title': f"[Reuters] {title}",
                        'link': link,
                        'source': '路透社',
                        'date': date
                    })
                    
                    if len(news_list) >= 5:
                        break
                        
            except Exception as e:
                print(f"解析Reuters单条失败: {e}")
                continue
        
        print(f"Reuters: {len(news_list)} 条")
        return news_list
        
    except Exception as e:
        print(f"Reuters抓取失败: {e}")
        return []

def crawl_nia():
    """抓取中国国家移民管理局新闻"""
    url = "https://www.nia.gov.cn/n741440/n741547/index.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    keywords = ['移民', '出入境', '签证', '护照', '边检', '口岸', '外国人', '居留', '国籍', '难民', '遣返']
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        items = soup.select('.news-list li a') or soup.select('.list li a') or soup.select('a[title]')
        
        for item in items:
            try:
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                if not title or len(title) < 5 or 'javascript' in link.lower():
                    continue
                
                if not any(keyword in title for keyword in keywords):
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
        print(f"NIA抓取失败: {e}")
        return []

def save_data(all_news):
    """保存数据到JSON文件"""
    os.makedirs('data', exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'data/news_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    with open('data/latest.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n总计保存 {len(all_news)} 条新闻")

def main():
    print(f"开始抓取: {datetime.now()}\n")
    
    all_news = []
    
    iom_news = crawl_iom()
    all_news.extend(iom_news)
    
    reuters_news = crawl_reuters_rss()
    all_news.extend(reuters_news)
    
    nia_news = crawl_nia()
    all_news.extend(nia_news)
    
    save_data(all_news)
    print("完成!")

if __name__ == '__main__':
    main()
