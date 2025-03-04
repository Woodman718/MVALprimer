#!/usr/bin/env python
# coding: utf-8

import os,time
import re

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
    #"%": "%25",
}

def escape_doi(doi):
    pattern = re.escape(''.join(escape_dict.keys()))
    regex = re.compile(r'([' + pattern + r'])')
    # 使用re.sub替换匹配到的字符
    return regex.sub(lambda match: escape_dict[match.group()], doi)

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
        pre_doi = parts[0]
        suf_doi = '/'.join(parts[1:])
        return suf_doi
    else:
        print(f'{doi} is not a valid format.')
        
    return doi        


def read_doi_set(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return set(transform_doi(doi) for doi in file.read().splitlines())


def process_doi(match_doi_file, qunhui_file_path, root_dir,output_dir):

    doi_list = read_doi_set(match_doi_file)
    paths_list = read_doi_set(qunhui_file_path)
    
    # paths_map = read_doi_to_path_map(qunhui_file_path)
    # paths_list = set(paths_map.keys())
    # 找出既在doi_list又在paths_list中的DOI
    doi_match = paths_list.intersection(doi_list)
    # 找出在doi_list中但不在paths_list中的DOI
    doi_non_match = doi_list - paths_list

    # 构造完整的PDF路径
    # pdf_paths = [paths_map[doi] for doi in doi_match]
    # 构造完整的PDF路径
    pdf_paths = [os.path.join(root_dir, doi) + '.pdf' for doi in doi_match]
    # 写入到文件
    with open(os.path.join(output_dir, 'pdf_list.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(pdf_paths))

    with open(os.path.join(output_dir, 'wait2handle.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(doi_non_match))

    print("处理完成，并已写入到输出文件中。")


if __name__ == '__main__':
    suf = time.strftime("%m%d_%H%M", time.localtime())
    out_dir = f'./output/{suf}'
    os.makedirs(out_dir, exist_ok=True)

    root_dir = '/s1/SHARE/sci_hub/pub_med/root'
    match_doi_file = './data/wait2handle.txt'
    qunhui_file_path = './data/root_file_path.txt'


    process_doi(match_doi_file, qunhui_file_path,root_dir, out_dir)

    # get_ipython().system(' wc -l {out_dir}/*')