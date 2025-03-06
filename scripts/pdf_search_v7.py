import csv,os,time
import pandas as pd

import fitz  # PyMuPDF
# import pdfplumber

import shutil
import re
import  pdf2doi

# import regex
# from fuzzysearch import find_near_matches
# from multiprocessing import Pool

import argparse



pdf2doi.config.set('verbose',False)
pdf2doi.config.set('save_identifier_metadata',False)
pdf2doi.config.set('websearch', False) 
pdf2doi.config.set('webvalidation', False)#DOI 在线验证
pdf2doi.config.set('replace_arxivID_by_DOI_when_available',False)
pd.set_option('display.max_columns', None)
pd.options.display.max_colwidth = 400 
pdf2doi.config.print()
print(f'PyMuPDF Version:{fitz.VersionBind}')

escape_dict = { 
    " ": "%20",
    '"': "%22",
    "#": "%23",
    "(": "%28",
    ")": "%29",
    "*": "%2A",
    "+": "%2B",
    "/": "%2F",
    ":": "%3A",
    ";": "%3B",
    "<": "%3C",
    ">": "%3E", 
    "?": "%3F",
    "{": "%7B",
    "}": "%7D",
    "^": "%5E",
    "[": "%5B",
    "]": "%5D",
    "`": "%60",
    "|": "%7C",
    "\\": "%5C",
    "%": "%25",
}

unescape_dict = {v: k for k, v in escape_dict.items()}

def escape_doi(doi):
    pattern = re.escape(''.join(escape_dict.keys()))
    regex = re.compile(r'([' + pattern + r'])')
    # 使用re.sub替换匹配到的字符
    return regex.sub(lambda match: escape_dict[match.group()], doi)


def unescape_doi(doi2filename):
    pattern = '|'.join(re.escape(k) for k in unescape_dict.keys())
    regex = re.compile(pattern)
    # 使用正则表达式替换编码字符串为原始字符串
    return regex.sub(lambda match: unescape_dict[match.group()], doi2filename)


def transform_doi(doi):
    doi = doi.strip()
    if doi.startswith('10.'):
        parts = doi.split('/')
        pre_doi = parts[0]
        suf_doi = '/'.join(parts[1:])
        suf_doi = escape_doi(suf_doi)
        return pre_doi + '/' + suf_doi
        
    elif doi.endswith('.pdf'):
        path = doi.rsplit('.', 1)[0]
        parts = path.rsplit('/',2)
        pre_doi = parts[1]
        suf_doi = unescape_doi(parts[2])
        return pre_doi + '/' + suf_doi
    else:
        print(f'{doi} is not a valid format.')
        
    return doi   


def read_pdf_list(pdf_list_file):
    with open(pdf_list_file, 'r', encoding='utf-8', errors='ignore') as f:
        pdf_paths = [line.strip() for line in f]
    return pdf_paths
 
def check_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        page_count = len(doc)
        text_length = sum([len(page.get_text()) for page in doc])
        doc.close()
        return True, page_count, text_length
    except Exception as e:
        return False, 0, 0


def is_italic(flags):
    # 检查 flags 中的某个特定位是否表示斜体
    # return (flags & (1 << 1)) != 0  # 假定斜体标志是第二位
    return flags & (1 << 1)  # 假设斜体的标志位是1
    # """根据字体flags判断是否为斜体，这里假设斜体的flag包含64"""
    # return flags & (1 << 6) != 0  # 通常斜体字体的flag位
 
def extract_italic(pdf_path, output_dir, obj):
    doc = fitz.open(pdf_path)
    italic_texts = []
    carry_over_text = ""  # 用于存储需要从上一行携带到下一行的文本
    exclude_chars_count = 500  # 排除每篇论文开头的字符数量

    for page_num, page in enumerate(doc):
        try:
            text = page.get_text("text")
            if "References" in text and page_num > 0:
                break

            if page_num == 0: 
                text = text[exclude_chars_count:]
                
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if 'lines' in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            if is_italic(span['flags']):  # 检查是否为斜体
                                text = span["text"]
                                # 如果前面有携带过来的文本，尝试合并
                                if carry_over_text:
                                    text = carry_over_text + text
                                    carry_over_text = ""  # 重置携带文本
                                # 如果当前片段以连字符结束，准备将其与下一行合并
                                if text.endswith('-'):
                                    carry_over_text = text[:-1]  # 存储去掉连字符的文本以便与下一行合并
                                else:
                                    line_text += text + " "  # 添加到行文本中
                        if line_text:  # 如果这一行有斜体文本，加入结果列表
                            italic_texts.append(line_text.strip())
            # 处理完一页后，如果有未处理的携带文本，也加入结果列表（防止文章最后一行断字）
            if carry_over_text:
                italic_texts.append(carry_over_text)
                carry_over_text = ""  # 重置携带文本
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            with open(f'{output_dir}/{obj}_error.txt', 'a', encoding='utf-8') as error_file:
                error_file.write(pdf_path + '\n')

    doc.close()
    return italic_texts


def check_output_files(output_dir, obj):
    skip_files = set()
    primer_file = os.path.join(output_dir, f"{obj}_primer_file.txt")
    
    # 清空 primer_file.txt
    with open(primer_file, "w") as f:
        pass
    
    # 合并其他文件到 skip_files 集合
    for filename in [f"{obj}_destory.txt", f"{obj}_drop.txt", f"{obj}_useless.txt", f"{obj}_zero.txt", f"{obj}_non_pdf.txt"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding='utf-8') as f:
                skip_files.update(f.read().splitlines())
    
    return skip_files
    
    def file_rename(filename):
    # Split based on '_' and process according to the number of parts.
    filename = os.path.basename(file_path).rsplit('.', 1)[0]
    parts = filename.split('_')
    if len(parts) >= 3:
        filename = '/'.join(parts[:2])
    elif len(parts) == 2:
        filename = '/'.join(parts)
    
    # Ensure the filename ends with ".pdf" extension
    # if not filename.lower().endswith('.pdf'):
    #     filename += ".pdf"
        
    # Replace specified substrings independently
    filename = filename.replace('%28', '(').replace('%29', ')')
    filename = filename.replace('a%3A', 'A:')
    filename = filename.replace('%2F', '/')
    filename = filename.replace('@', '/')
    # Check if filename starts with "10."
    if not filename.startswith("10"):
        filename = "10.xxxx/" + filename
    return filename


def extract_Doi(pdf_path):
    result = None
    try:
        result = pdf2doi.pdf2doi(pdf_path)
    except Exception as e:
        print(f"{pdf_path} occurred while extracting DOI: {e}")
        return None, None
    
    if result is None or 'identifier' not in result:
        return None, None
    Doi = result['identifier']
    # Type = result['identifier_type']
    Type = result.get('identifier_type', None)

    return Doi, Type
    
    
def extract_primers(file_path, microbe_name='None',
                    DOI='None',TYPE='None'):
    doc = fitz.open(file_path)#, check_extractable=True)
    data = []  
    f_name = transform_doi(file_path)
    microbe = microbe_name 
    Doi = DOI
    Type = TYPE

    primer_pattern = re.compile(r'([ATCG][RYSWKMBDHVN]?\s?\*?){9,}(\s\*{0,3})?')
       
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").replace("-", "")
        # text = text.replace("\n", "")
        primer_matches = list(primer_pattern.finditer(text))
        
        for i in range(0, len(primer_matches), 2):
            forward_match = primer_matches[i]
            reverse_match = primer_matches[i+1] if i + 1 < len(primer_matches) else None
            
            surrounding_text = text[max(0, forward_match.start() - 100):min(len(text), forward_match.end() + 100)]
         
            data.append({
                "Microbe_name": microbe,
                "Forward": forward_match.group().replace(" ", "").rstrip("\n"),
                "Reverse": reverse_match.group().replace(" ", "").rstrip("\n") if reverse_match else 'None',
                "Page": page_num + 1,
                "f_name": f_name,
                "Doi": Doi,
                "Type": Type,
                "Note": surrounding_text.replace("\n", "")
            })
    
    doc.close()
    return data  
    
def process_pdf_files(pdf_paths, output_dir,obj='None'):
    all_data = pd.DataFrame()
    ex_char = [',', '/', ':', '-', '(',')', '.', '?', ';','*', '\\', "'",'\n',
               '~', '+','$','#','&','%','^','@','!','[',']','{','}','"','•']
    ex_word = ['Abstract','Journal','Subjects','Cell','Isolation',
                'in','Animals','Solution','Microscopy','Immunohistochemistry',
               'Cytometry', 'et al', 'Key words','Taq',]
    repeat_0 = re.compile(r'(^.\s+){1,}') # 特殊符号 + 一个或多个空格
    repeat_1 = re.compile(r'^\d+.*$') # 数字开头
    repeat_2 = re.compile(r'^[\u0370-\u03FFA-Z]+\s+')
    repeat_3 = re.compile(r'^[\u0370-\u03FF]+\s+')#希腊字母
    repeat_4 = re.compile(r'.*[\£\$\€]+.*')
    repeat_5 = re.compile(r'^[A-Z]{1}\s+[A-Za-z]+$')
    # 程序中断重启
    skip_files = check_output_files(output_dir, obj)
    
    for file_path in pdf_paths:
        Search = False
        
        if file_path in skip_files:
            continue
            
        if file_path.endswith('.pdf'):
            file_size = os.path.getsize(file_path) / 1024  # KB unit
            is_valid, page_count, text_length = check_pdf(file_path)
            Search = True
        
        if not is_valid:
            with open(f'{output_dir}/{obj}_destory.txt', 'a', encoding='utf-8') as df:
                df.write(file_path + '\n')

        elif file_size < 20 or page_count < 3:
            with open(f'{output_dir}/{obj}_drop.txt', 'a', encoding='utf-8') as fd:
                fd.write(file_path + '\n')

        elif text_length == 0:
            with open(f'{output_dir}/{obj}_zero.txt', 'a', encoding='utf-8') as z:
                z.write(file_path + '\n')
                
        elif Search:
            Doi, Type = extract_Doi(file_path)
            # print(Doi, Type)
            microbe_name = 'None'
            filtered_texts = extract_italic(file_path,output_dir,obj)

            if filtered_texts:
                filtered_texts = [text for text in filtered_texts if
                                  (text.strip() != '' and len(text) > 1 and
                                   not repeat_0.search(text) and
                                   not repeat_1.search(text) and
                                   not repeat_2.search(text) and
                                   not repeat_3.search(text) and
                                   not repeat_4.search(text) and
                                   not any(char in ex_char for char in text) and
                                   not any(word in text for word in ex_word) or
                                   repeat_5.search(text))
                                  ]

                if len(filtered_texts) > 4:
                    microbe_name = filtered_texts[0:5]
                elif len(filtered_texts) > 2:
                    microbe_name = filtered_texts[0:2]
                elif len(filtered_texts) > 0:
                    microbe_name = filtered_texts[0]
                    
                # microbe_name = ' '.join(microbe)
                data = extract_primers(file_path, microbe_name, Doi, Type)
            else:
                data = extract_primers(file_path, microbe_name, Doi, Type)

            if data:
                with open(f'{output_dir}/{obj}_primer_file.txt', 'a', encoding='utf-8') as pf:
                    pf.write(file_path + '\n')
                df = pd.DataFrame(data)
                all_data = pd.concat([all_data, df], ignore_index=True)
            else:
                with open(f'{output_dir}/{obj}_useless.txt', 'a', encoding='utf-8') as uf:
                    uf.write(file_path + '\n')
        else:
            with open(f'{output_dir}/{obj}_non_pdf.txt', 'a', encoding='utf-8') as npf:
                npf.write(file_path + '\n')

    if not all_data.empty:
        all_data.to_csv(f"{output_dir}/{obj}_summary.tsv", sep='\t', index=False)
    else:
        print('No data extracted.')

        return all_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='./data/root_pdf_list.txt')
    parser.add_argument('--obj', default='root')
    args = parser.parse_args()

    print(time.strftime("%H:%M:%S", time.localtime()))
    # suf = time.strftime("%m%d_%H%M", time.localtime()) 
    suf = '0322_1117'
    object = args.obj
    files_list = args.input
    pdf_paths = read_pdf_list(files_list)
    # out_dir = os.path.join(os.getcwd(),'output',suf)
    out_dir = os.path.join(os.getcwd(),'output',object,suf)
    os.makedirs(out_dir, exist_ok=True)
    
    resoult_data = process_pdf_files(pdf_paths, out_dir,object)
    