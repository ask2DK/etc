"""
dibaeck

# about
- 레전드스터디 닷컴("https://legendstudy.com") 크롤링
- input : (3개 파라미터) url, max_page, save_dir_path
- output : 다운로드 파일들, 에러로그 출력

# Environment
- 파이썬 3.9 이하

# Prerequisite
$ pip install request
$ pip install beautifulsoup
"""

import os
from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests

def get_download(url, fname):
    try:
        os.chdir(save_dir_path)
        request.urlretrieve(url,f'{fname}.pdf')
        print(f'{fname}.pdf 다운로드 완료')
    except HTTPError as e:
        print('error')
        return
    
def processing_post(posts,count):
    for post in posts:
        post_title = post.get_text()    # 게시물 제목
        post_num = post.get('href')     # 게시물 주소 번호
        post_in_url = home_url+post_num # 게시물 주소
        
        respond_in = requests.get(post_in_url)
        soup_in = BeautifulSoup(respond_in.text, "html.parser")
        
        post_in_pdf_type01 = soup_in.select("#jbContent > div > div.jbArticle > div.tt_article_useless_p_margin.contents_style > p > figure > a")
        post_in_pdf_type02 = soup_in.select("#jbContent > div > div.jbArticle > div.tt_article_useless_p_margin.contents_style > p > span > a")
        post_in_pdf = post_in_pdf_type01 if post_in_pdf_type01 else post_in_pdf_type02 if post_in_pdf_type02 else None
        
        if not post_in_pdf:
            # ERROR : 코드 수정이 필요한 게시물
            print(f">>>>>>>>>>>>>>>>> {post_title} - {post_in_url}")
            continue
        
        for info in post_in_pdf :
            down_link = info.get("href")
            origin_title = info.get_text()
            title = origin_title.strip().split('.pdf')[0]
            if not title :
                 # ERROR : 확인하기
                print(f"title ERROR : {post_title} - {post_in_url} > {origin_title}")
                continue
            get_download(down_link,title)
            count +=1

    return count

def run(url,max_page):
    
    page_url = url
    pageoffset = max_page
    
    page = 1
    done_count = 0  # 다운로드 파일 수
    while page <=pageoffset:
        # request 모듈을 사용하여 웹 페이지의 내용을 가져온다
        respond = requests.get(page_url+str(page))
        # beautiful soup 초기화
        soup = BeautifulSoup(respond.text, "html.parser")
        # posts : 해당 url의 게시물 리스트
        posts = soup.select("#jbContent > div.jbSearchResult > ul > li > span > a")
        done_count += processing_post(posts,done_count)
        
        # 페이지 이동
        page +=1
        
    return done_count


if __name__ == "__main__":
    
    global home_url
    global save_dir_path
    
    home_url = "https://legendstudy.com"
    save_dir_path = "C:\\Users\\DANIK\\github_dk\\Study_Team_CL\\test"
    
    input_url = "https://legendstudy.com/category/%E2%97%86%EF%BB%BF%20%22%EA%B3%A03%22%EC%9D%84%20%EC%9C%84%ED%95%9C%20%EA%B3%B5%EA%B0%84%20/3%ED%95%99%EB%85%84%20%EB%AA%A8%EC%9D%98%EA%B3%A0%EC%82%AC%20%EC%A0%84%EA%B3%BC%EB%AA%A9%20%EC%9E%90%EB%A3%8C?page="
    m_page = 1
    
    download_file_num = run(input_url,m_page)
    print(f"========== Done ========== total Download file : {download_file_num}")