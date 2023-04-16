"""
dibaeck

# about
- pdf에서 text로 저장할 때, 원하는 형식으로 저장하기(index, query(context, question), answer, note)
- input : (1개 파라미터 : 실행할 파일 있는 폴더) file_dir_path
- output : ( text로 변환된 파일 저장 위치 폴더) saved_path

# Environment
- 파이썬 3.9 이상(최신버젼 ok)

# Prerequisite
- pip install PyMuPDF

"""

import fitz
import re
from collections import defaultdict
import sys
import os

def answering_dict(document):
    '''
    해설 및 답지 딕셔너리
    '''
    answer_doc = fitz.open(f'{dir_path}/{document}')

    answer = defaultdict()
    for page in answer_doc:
        page = page.get_text("blocks")
        # blocks(list) : page
        answer_list = []
        
        for line in page:
            if line[-2] ==0 and "전국연합학력평가" not in line[-3] :
                return None
            
            if line[-2] <= 3:
                continue

            if line[-2] > 12 :
                while answer_list:
                    value, key = answer_list.pop(),answer_list.pop()
                    answer[int(key)] = value
                return answer
            
            answer_list += line[-3].strip('\n').split('\n')

def query_dict(document, answer):
    """
    
    """
    num_patten = re.compile("([0-9]+)(\.)")
    option_patten = re.compile('(\[)+(\d)+(.\S)+(\d)+(\])')

    doc = fitz.open(f'{dir_path}/{document}')
    result = defaultdict()
    for page in doc:
        page = page.get_text("blocks")
        # blocks(list) : page
        
        text = ''
        
        for line in page:
            # line
            # (x0, y0, x1, y1, "lines in the block", block_no, block_type)
            # line[-1] == 0:  # Text
            # line[-3] # "lines in the block"
            if line[-2] <=1 :             
                continue

            if line[-1] == 0 :  # Text
                current_line = line[-3]  # "lines in the block"
                current_line = re.sub('(\S)*(\[[0-9]+점])','',current_line)  # \\[3점]\\ 텍스트 제거
                current_line = re.sub('(\*)+(.+)','',current_line)  # \\* morphology: 형태\\ 제거
                current_line = current_line.replace('\xad','-')  # \\* morphology: 형태\\ 제거
                
                is_pass = True if re.search('학년도|\확인 사항|이제 듣기 문제가 끝났습니다.|답을 하시기|답안지의|로그인 필요 없는 학습 자료 무료 제공 사이트!|로그인 필요 없는 학습 자료 무료 제공 사이트!|www.LegendStudy.com',current_line) else False
                
                current_line_is_query_num = True if num_patten.search(current_line[:3]) else False
                current_line_is_query_common = True if option_patten.search(current_line) else False
                
                # 현재 라인에서 숫자 발견 or [] 발견했으면,            
                if current_line_is_query_num or is_pass or current_line_is_query_common:
                    if option_patten.search(text) and '다음을 듣고,' not in text :
                        number_s,number_e = re.findall('\d+',text[:8])
                        number_s,number_e = int(number_s),int(number_e)
                                            
                        for key in range(number_s,number_e+1):
                            result[key] = {'query': text}
                        
                        text = ''
                        
                    if num_patten.search(text) : ## 여기서 elif 로 수정?
                        s_ind,e_ind = num_patten.search(text).span()
                        key = int(text[s_ind:e_ind].replace('.','').strip())
                        query = text[e_ind:]
                        if key in result.keys() :
                            result[key]['query'] +=query
                            result[key]['answer'] = answer[key]
                        else :
                            result[key]=({'query': query})
                            result[key]['answer'] = answer[key]
                        
                        text =''

                    if is_pass :
                        continue
                
                text += current_line.replace('\n','')
                
            else:
                text +="<!image>"
        else :
            if num_patten.search(text) : ## 여기서 elif 로 수정?
                s_ind,e_ind = num_patten.search(text).span()
                key = int(text[s_ind:e_ind].replace('.','').strip())
                query = text[e_ind:]
                if key in result.keys() :
                    result[key]['query'] +=query
                    result[key]['answer'] = answer[key]
                else :
                    result[key]=({'query': query})
                    result[key]['answer'] = answer[key]
                    
    return result

def run(file_name):
    source_,year_,number_,type_ = file_name.split('.')
    make_file = open('{source_}.{year_}.{number_}.txt','w',encoding='utf-8')
    
    
    answer_file ='{source_}.{year_}.{number_}.해설.pdf'
    answer = answering_dict(answer_file)
    result = query_dict(file_name, answer)
    
    for key,value in result.items():
        if re.search("밑줄|표|<!image>",value['query']):
            note = re.search("밑줄|표|<!image>",value['query']).group()
            make_file.write(str(key)+'\t'+value['query']+'\t'+note+'\n')
            continue
        
        print(key,value['query'])
        make_file.write(str(key)+'\t'+value['query']+'\tNone\n')
        
    make_file.close()
    
if __name__ == "__main__":
    global dir_path
    
    
    for file_name in os.listdir():
        run(file_name)
    