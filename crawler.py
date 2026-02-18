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
        
        for item in items[:5]:  # 取前5条
            try:
                # 提取标题
                title_tag = item.select_one('h2 a') or item.select_one('.field--name-title a') or item.select_one('a')
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                
                # 提取日期
                date_tag = item.select_one('.field--name-field-date') or item.select_one('time')
                date = date_tag.get_text(strip=True) if date_tag else datetime.now().strftime('%Y-%m-%d')
                
                # 补全链接
                if link and not link.startswith('http'):
                    link = 'https://www.iom.int' + link
                
                # 过滤非移民内容（IOM都是移民相关，简单过滤即可）
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
    # 路透社世界新闻RSS
    url = "https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best"
    # 备用：直接世界新闻
    url = "https://www.reuters.com/rssfeed/world/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 移民相关关键词
    keywords = ['migration', 'migrant', 'immigration', 'immigrant', 'refugee', 'asylum', 'visa', 'border', 'deportation', 'citizenship']
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 解析XML
        root = ET.fromstring(response.content)
        
        news_list = []
        
        # RSS格式：channel -> item
        for item in root.findall('.//item'):
            try:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').
