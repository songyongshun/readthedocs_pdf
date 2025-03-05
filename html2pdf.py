from bs4 import BeautifulSoup
import os
import shutil
import requests
from requests.exceptions import RequestException
import pdfkit
from PyPDF2 import PdfWriter, PdfReader

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""



# 全局变量
base_url = 'https://gpaw.readthedocs.io/'
book_name = ''
chapter_info = []


def get_one_page(url):
    """
    获取网页html内容并返回
    :param url:目标网址
    :return html
    """
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }

    try:
        # 获取网页内容, 返回html格式数据
        response = requests.get(url, headers=headers)
        # 通过状态码判断是否获取成功
        if response.status_code == 200:
            # 指定编码，否则中文出现乱码
            response.encoding = 'utf-8'
            return response.text
        return None
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_title_and_url(html):
    """
    解析全部章节的标题和url
    :param html: 需要解析的网页内容
    :return None
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 获取书名
    global book_name
    book_name = soup.find('div', class_='wy-side-nav-search').a.text.strip()
    #menu = soup.find_all('div', class_='wy-menu wy-menu-vertical')
    menu = soup.find_all('div', class_='toctree-wrapper compound')
    # 检查是否找到菜单
    if not menu:
        print("Warning: No 'section' div found in the HTML.")
        return
    
    chapters = menu[0].find_all('li', class_='toctree-l1')
    child_chapters = menu[0].find_all('li', class_='toctree-l2')
    # 从chapters的第7个元素开始，前6个跳过
    for chapter in chapters:
        #if index >= 0:
        #    continue
        info = {}
        # 获取一级标题和url
        # 标题中含有'/'和'*'会保存失败
        info['title'] = chapter.a.text.replace('/', '').replace('*', '')
        # webpage, like https://gpaw.readthedocs.io/algorithms.html
        chapter_url = chapter.a.get('href')
        info['url'] = base_url + chapter_url
        info['child_chapters'] = []
        #print(info['title'])

        # 获取.html前面的字符，再检查下是否有"/",如果有的话，取"/"前面的字符
        chapter_name = chapter_url.split('.')[0]
        if '/' in chapter_name:
            chapter_name = chapter_name.split('/')[-1]
        #print(chapter_name)
        for child in child_chapters:
            # 如果不是.html结尾，则跳过，不做任何处理
            url = child.a.get('href')
            if not url.endswith('.html'):
                continue
            # 比较是否是该一级标题下的二级标题
            if chapter_name == url.split('/')[0]:
                child_info = {
                    'title': child.a.text.replace('/', '').replace('*', ''),
                    'url': base_url + url,
                }
                info['child_chapters'].append(child_info)
                #print(f"Added child chapter: {child_info['title']} at URL: {child_info['url']}")

        chapter_info.append(info)


def save_pdf(html, filename):
    """
    把所有html文件保存到pdf文件
    :param html:  html内容
    :param file_name: pdf文件名
    :return:
    """
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }

    try:
        # 查找html里是否有src="_images"，如果有，则替换成绝对路径 "https://gpaw.readthedocs.io/_images"
        html = html.replace('src="_images/', f'src="{base_url}_images/')
        html = html.replace('src="../_images/', f'src="{base_url}_images/')        
        html = html.replace('src="../../_images/', f'src="{base_url}_images/')        
        
        #print(html)
        # 找到第一个 <html> 标签的位置  
        start_index = html.find('<html')  # 找到第一个 <html> 标签的位置  

        # 找到第二个 <html> 标签的位置  
        if start_index != -1:  # 确保找到了第一个 <html> 标签  
            second_start_index = html.find('<html', start_index + 1)  
        else:  
            second_start_index = -1  # 没有找到第一个 <html> 标签  

        # 截取从第一个 <html> 到第二个 <html> 标签之间的内容  
        if second_start_index != -1:  # 确保找到了第二个 <html> 标签  
            html_first = html[start_index:second_start_index]  
        else:  
            html_first = html[start_index:]  # 只有一个 <html>，保留剩余所有内容  

        # 找到最后一个 </html> 标签的位置并包括它  
        last_end_index = html.rfind('</html>') + len('</html>')  # 找到最后一个 </html> 标签的位置并包括它  

        # 找到倒数第二个 </html> 标签的位置  
        if last_end_index != -1:  # 确保找到了最后一个 </html> 标签  
            second_last_end_index = html.rfind('</html>', 0, last_end_index - len('</html>'))  
        else:  
            second_last_end_index = -1  # 没有找到最后一个 </html> 标签  

        # 截取从倒数第二个 </html> 标签到最后一个 </html> 标签之间的内容  
        if second_last_end_index != -1:  # 确保找到了倒数第二个 </html> 标签  
            html_second = html[second_last_end_index+len('</html>'):last_end_index]  
        else:  
            html_second = ''  # 若没有找到，则为空  

        # 合并最外层 <html> 和 </html> 标签内容  
        html = html_first + html_second  
        #print(html)
 
        # 使用 pdfkit 将 HTML 内容保存为 PDF 文件        
        pdfkit.from_string(html, filename, options=options)
    except Exception as e:
        print(f"Error saving PDF {filename}: {e}")
        raise SystemExit(f"Failed to save PDF: {e}")

def get_content(url):
    """
    解析URL, 获取需要的html内容
    :param url: 目标网址
    :return: html
    """
    # 获取网页内容并解析HTML，忽略class为plotly-graph-div的元素
    html = get_one_page(url)    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 忽略class为plotly-graph-div的元素
    for plotly_div in soup.find_all('div', class_='plotly-graph-div'):
        plotly_div.decompose()
    
    # 查找包含文章主体内容的div
    content = soup.find('div', attrs={'itemprop': 'articleBody'})
    if content:
        formatted_html = html_template.format(content=str(content))
        return formatted_html
    else:
        print(f"No content found at {url}")
        return ""


def parse_html_to_pdf():
    """
    解析URL,获取html,保存成pdf文件
    :return: None
    """
    try:
        for chapter in chapter_info:
            ctitle = chapter['title']
            url = chapter['url']
            # 文件夹不存在则创建（多级目录）
            dir_name = os.path.join(os.path.dirname(__file__), 'gen', ctitle)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            html = get_content(url)
            print(url)

            padf_path = os.path.join(dir_name, ctitle + '.pdf')
            save_pdf(html, padf_path)

            children = chapter['child_chapters']
            if children:
                for child in children:
                    html = get_content(child['url'])
                    pdf_path = os.path.join(dir_name, child['title'] + '.pdf')
                    save_pdf(html, pdf_path)

    except Exception as e:
        print(f"Error parsing HTML to PDF: {e}")


def merge_pdf(infnList, outfn):
    """
    合并pdf
    :param infnList: 要合并的PDF文件路径列表
    :param outfn: 保存的PDF文件名
    :return: None
    """
    pagenum = 0
    pdf_output = PdfWriter()

    for pdf in infnList:
        # 先合并一级目录的内容
        first_level_title = pdf['title']
        dir_name = os.path.join(os.path.dirname(__file__), 'gen', first_level_title)
        padf_path = os.path.join(dir_name, first_level_title + '.pdf')
        #print(first_level_title)

        try:
            with open(padf_path, 'rb') as f:
                pdf_input = PdfReader(f)
                #print("here")
                # 获取 pdf 共用多少页
                page_count = len(pdf_input.pages)
                for i in range(page_count):
                    pdf_output.add_page(pdf_input.pages[i])

                # 添加书签
                parent_bookmark = pdf_output.add_outline_item(first_level_title, page_number=pagenum)

                # 页数增加
                pagenum += page_count

                # 存在子章节
                if pdf['child_chapters']:
                    for child in pdf['child_chapters']:
                        second_level_title = child['title']
                        padf_path = os.path.join(dir_name, second_level_title + '.pdf')

                        with open(padf_path, 'rb') as cf:
                            pdf_input = PdfReader(cf)
                            # 获取 pdf 共用多少页
                            page_count = len(pdf_input.pages)                          
                            for i in range(page_count):
                                # 确保页面对象是有效的，再添加到输出PDF中
                                if pdf_input.pages[i] is not None:
                                    pdf_output.add_page(pdf_input.pages[i])                                    
                            # 添加书签
                            pdf_output.add_outline_item(second_level_title, page_number=pagenum, parent=parent_bookmark)
                            # 增加页数
                            pagenum += page_count

        except FileNotFoundError as e:
            print(f"File not found: {padf_path}")

    # 合并
    try:
        with open(outfn, 'wb') as f:
            pdf_output.write(f)
    except Exception as e:
        print(f"Error writing merged PDF: {e}")

    # # 删除所有章节文件 
    # try:
    #     shutil.rmtree(os.path.join(os.path.dirname(__file__), 'gen'))
    # except Exception as e:
    #     print(f"Error removing temporary files: {e}")

def main():
    html = get_one_page(base_url)
    if html:
        parse_title_and_url(html)
        parse_html_to_pdf()
        output_file = os.path.join(os.path.dirname(__file__), book_name + '.pdf')
        merge_pdf(chapter_info, output_file)
        print(f"Merged PDF saved as {output_file}")
    else:
        print("Failed to fetch the base URL.")

if __name__ == '__main__':
    main()