"""
从网站爬去诗歌数据
"""
import requests
from bs4  import BeautifulSoup
from urllib.parse import urljoin
import time
import json

# 记录所有诗人的链接并等后续拉取
all_author_link = {}

def clearText(text):
    """
    去掉文章的杂乱字符
    空格、全角空格、换行符、中文占位符
    """
    return text.strip().replace(" ", "").replace("\n", "").replace("", "").replace("　", "")

def doRequest(base_url):
    """
    简单封装下请求
    """
    try:
        response = requests.get(base_url)
        response.encoding = "gb18030"
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Error fetching {base_url}: {e}")
        return None

def get_hyperlinks(base_url):
    """
    获取超链接地址
    """
    poetry_links = {}
    soup = doRequest(base_url)
    if(soup == None):
        return None

    # 获取页面区块
    material_block = soup.find_all('div', class_='material_block clear taglist2-border')
    for block in material_block:
        # 诗歌类型
        type = block.find('h2').text.strip()
        # 类型下的超链接
        links = block.find_all('a', href=True)
        if(len(links) != 0):
            poetry_links[type] = {urljoin(base_url, link['href']) for link in links}
    return poetry_links


def scrape_text_from_url(url, type=None):
    """
    爬取对应文本
    """
    soup = doRequest(url)
    if(soup == None):
        return None
    # 诗歌标题
    title = soup.find('h1').text.strip()
    # 获取和更新作者超链接
    try:
        author_link_node = soup.find('div', id='detail_article_info').find('a')
        author = author_link_node.text.strip()
        author_link = urljoin(url, author_link_node['href'])
    except:
        author_link = ''
        author = soup.find('div', id='detail_article_info').text.strip().split('作者：')[1].split('更新日期')[0].strip()
    all_author_link[author] = author_link
    # 获取诗歌内容
    article = soup.find('div', id='article')
    # 主题等获取
    article_text = article.text.strip()
    try:
        poem = article.find('p', align='center').text.strip()
    except:
        poem = article_text.split('注释')[0].split('注解')[0].strip()
    try:
        translate = article_text.split('译文')[1].split('赏析')[0].split('注释')[0].split('注解')[0].strip()
    except:
        translate = ''
    try:
        analysis = article_text.split('赏析')[1].strip()
    except:
        analysis = ''
    print(f'In {type} found {title}, with author: {author}...')
    return {
        'url': url,
        'type': type,
        'title': title,
        'author': author,
        'poem': clearText(poem),
        'translate': clearText(translate),
        'analysis': clearText(analysis)
    }

def get_author_details(author, author_link):
    """
    获取作者详情
    """
    if(author_link == ''):
        return {
            "author": author,
            "author_info": "",
        }
    soup = doRequest(author_link)
    if(soup == None):
        return None
    author_info = soup.find('div', id='article').text.strip()
    print(f'Get author: {author} details')
    return {
        'author': author,
        'author_info': clearText(author_info)
    }

def main():
    # 初始化信息
    base_url = 'https://www.kxue.com/gushi/tangshi300shou.html'
    poetry_type = 'tangshisanbaishou'

    print(f'Fetching {poetry_type} from {base_url}...')
    hyperlinks = get_hyperlinks(base_url)

    results = []
    for type, links in hyperlinks.items():
        print(f'Getting type {type}...')
        for link in links:
            data = scrape_text_from_url(link, type)
            results.append(data)
            time.sleep(0.5)
    print(f'Done! get all poetry data!')

    author_results = []
    print(f'Getting author ...')

    for author, author_links in all_author_link.items():
        data = get_author_details(author, author_links)
        author_results.append(data)
        time.sleep(0.5)
    print(f'Done! get all author detail!')

    with open(f'./data/poetry/{poetry_type}.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
    with open(f'./data/poetry/{poetry_type}_author.json', 'w', encoding='utf-8') as file:
        json.dump(author_results, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()