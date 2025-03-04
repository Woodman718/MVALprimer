#!/usr/bin/env python
# coding: utf-8


import csv
from prettytable import PrettyTable


def read_doi_set(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return set(line.strip() for line in file if line.strip())


# 读取sci_hub_dois->0312_1501_matched2.csv
sci_hub_dois = set()
with open('./0312_1501_matched2.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # 跳过表头
    for row in csv_reader:
        doi = row[1]  # 假设DOI在每行的第二列
        sci_hub_dois.add(doi)


doi_pub_set = read_doi_set("doi_pub.tsv")


total_dois = len(doi_pub_set)
# 初始化总计数器
total_match_dois_count = 0
total_non_match_dois_count = 0
data_match = []
data_non_match = []

table = PrettyTable()
table.field_names = ["Name", "Number", "Percent"]


# 比对
doi_match = sci_hub_dois.intersection(doi_pub_set)
doi_non_match = doi_pub_set - sci_hub_dois

# 保存匹配和不匹配的 DOI
with open(f'doi_pub_match.tsv', 'w') as match_file:
    match_file.write('\n'.join(doi_match))
with open(f'doi_pub_non.tsv', 'w') as non_match_file:
    non_match_file.write('\n'.join(doi_non_match))


# 遍历所有 DOI 列表文件
for i in range(1, 13):
    doi_list_path = f'/home/caisongbo/s1/Doi/doi_list/doi_list_{i}.tsv'
    doi_list = read_doi_set(doi_list_path)

    # 比对
    doi_match = sci_hub_dois.intersection(doi_list)
    doi_non_match = doi_list - sci_hub_dois #difference

    # 保存匹配和不匹配的 DOI
    with open(f'./tmp/doi_match_{i:02}.tsv', 'w') as match_file:
        match_file.write('\n'.join(doi_match))
    with open(f'./tmp/doi_non_{i:02}.tsv', 'w') as non_match_file:
        non_match_file.write('\n'.join(doi_non_match))


for i in range(1, 13):
    match_set = read_doi_set(f"tmp/doi_match_{i:02}.tsv")
    non_match_set = read_doi_set(f"tmp/doi_non_{i:02}.tsv")
    
    # 检查交集
    overlap = match_set.intersection(non_match_set)
    assert len(overlap) == 0, f"Overlap found between match and non-match files for index {i}"

    # 更新总计数器
    match_count = len(match_set)
    non_match_count = len(non_match_set)
    total_match_dois_count += match_count
    total_non_match_dois_count += non_match_count
    
    data_match.append((f"Match {i}", match_count, f"{(match_count / total_dois) * 100:.2f}%"))
    data_non_match.append((f"Non-Match {i}", non_match_count, f"{(non_match_count / total_dois) * 100:.2f}%"))


# 计算占比
total_match_percentage = (total_match_dois_count / total_dois) * 100
total_non_match_percentage = (total_non_match_dois_count / total_dois) * 100

print(f"Total match DOIs percentage: {total_match_percentage:.2f}%")
print(f"Total non-match DOIs percentage: {total_non_match_percentage:.2f}%")
data = data_match + [
    ("Total Match", total_match_dois_count, f"{total_match_percentage:.2f}%")
    ] + data_non_match + [
    ("Total Non-Match", total_non_match_dois_count, f"{total_non_match_percentage:.2f}%")
    ]
for row in data:
    table.add_row(row)

print(table)