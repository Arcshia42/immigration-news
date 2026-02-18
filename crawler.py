import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def crawl_iom():
    """直接抓取IOM网页新闻"""
    url = "https://www.iom.int/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        
        # IOM网站新闻选择器（多种尝试）
        articles = soup.find_all('article', class_=lambda x: x and 'news' in x.lower() if x else False)
        if not articles:
            articles = soup.select('.node--type-news')
        if not articles:
            articles = soup.select('.views-row')
        if not articles:
            # 最后尝试所有h2标题
            articles = soup.find_all('h2')
        
        for article in articles[:5]:
            try:
                # 找标题链接
                a_tag = article.find('a') if article.name != 'a' else article
                if not a_tag:
                    a_tag = article.find_parent('a') or article.find('a')
                
                if not a_tag or not a_tag.get('href'):
                    continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href', '')
                
                # 清理标题
                if not title or len(title) < 15:
                    continue
                
                # 补全链接
                if link.startswith('/'):
                    link = 'https://www.iom.int' + link
                elif not link.startswith('http'):
                    link = 'https://www.iom.int/' + link
                
                news_list.append({
                    'title': f"[IOM] {title}",
                    'link': link,
                    'source': '国际移民组织(IOM)',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                print(f"解析单条失败: {e}")
                continue
        
        print(f"IOM: {len(news_list)} 条")
        return news_list
        
    except Exception as e:
        print(f"IOM抓取失败: {e}")
        return []

def crawl_dhs():
    """抓取美国国土安全部新闻"""
    url = "https://www.dhs.gov/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        
        # DHS新闻选择器
        items = soup.select('.views-row') or soup.select('.node--type-news') or soup.find_all('h3')
        
        for item in items[:5]:
            try:
                a_tag = item.find('a') if item.name != 'a' else item
                if not a_tag:
                    continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href', '')
                
                if not title or len(title) < 15:
                    continue
                
                # 只保留移民相关
                keywords = ['immigration', 'immigrant', 'border', 'citizenship', 'visa', 'asylum', 'refugee', 'migrant']
                if not any(kw in title.lower() for kw in keywords):
                    continue
                
                if link.startswith('/'):
                    link = 'https://www.dhs.gov' + link
                
                news_list.append({
                    'title': f"[DHS] {title}",
                    'link': link,
                    'source': '美国国土安全部',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                
            except:
                continue
        
        print(f"DHS: {len(news_list)} 条")
        return news_list
        
    except Exception as e:
        print(f"DHS抓取失败: {e}")
        return []

def crawl_nia():
    """抓取中国国家移民管理局"""
    url = "https://www.nia.gov.cn/n741440/n741547/index.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
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
    
    all_news.extend(crawl_iom())
    all_news.extend(crawl_dhs())
    all_news.extend(crawl_nia())
    
    save_data(all_news)
    print("完成!")

if __name__ == '__main__':
    main()
