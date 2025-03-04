import csv
import os
import time
from pathlib import Path

# 读取匹配的DOI列表
match_doi_set = {line.strip() for line in Path('doi_pub.tsv').read_text().splitlines()}
suf = time.strftime("%m%d_%H%M", time.localtime())
# 创建输出文件
output_dir = Path('output',suf)
os.makedirs(output_dir, exist_ok=True)

matched_csv = output_dir / '0312_1501_matched2.csv'
matched_ids = output_dir / 'matched_ids2.txt'

# 读取输入CSV文件并筛选匹配的行
with Path('./output/0312_1501_data.csv').open('r', newline='') as input_csv_file, \
        matched_csv.open('w', newline='') as output_csv_file, \
        matched_ids.open('w') as id_txt_file:
    reader = csv.DictReader(input_csv_file)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(output_csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        doi, doi2 = row['DOI'], row['DOI2']
        if doi in match_doi_set or doi2 in match_doi_set:
            writer.writerow(row)
            id_txt_file.write(row['ID'] + '\n')

print("Matching and writing complete.")

# 格式化ID并按范围分组到ZIP文件名
ids = sorted(int(line.strip()) for line in matched_ids.read_text().splitlines())
formatted_ids = (f'{id:08d}' for id in ids)
formatted_ids_file = output_dir / 'formatted_ids.txt'
formatted_ids_file.write_text('\n'.join(formatted_ids))

zip_ranges = set()
start_range = end_range = 0

for id in ids:
    while id >= end_range:
        start_range += 1000
        end_range += 1000
    zip_ranges.add(f'libgen.scimag{start_range:08d}-{end_range - 1:08d}.zip')

zip_names_file = output_dir / 'ZipName.txt'
zip_names_file.write_text('\n'.join(sorted(zip_ranges)))

print("Processing complete.")