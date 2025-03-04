import os,time
import shutil
import zipfile
import argparse
parser = argparse.ArgumentParser(description="Process PDF files in a specified directory.")
parser.add_argument('--ex_dir', type=str, default='./sb/', help='The results directory path.')
parser.add_argument('--sou', type=str, default='./sb/', help='The source directory path.')
parser.add_argument('--des', type=str, default='./sb/', help='The destination directory path.')
parser.add_argument('--zip_name_file', type=str, default='./output/ZipName.txt', help='The file containing ZIP file names to process.')
# args = parser.parse_args(args=[])
def process_zip_files(args):
    source_dir = args.sou
    destination_dir = args.des
    extract_dir = args.ex_dir
    zip_name_file = args.zip_name_file
    
    suf = time.strftime("%m%d_%H%M", time.localtime())
    output_dir = f'./output/{suf}'
    os.makedirs(output_dir, exist_ok=True)
    processed_file_path = f'{output_dir}/processed_files.txt'
    updated_zip_names_path = f'./output/ZipName_{suf}.txt'
    print(suf)
    # 读取待处理的 ZIP 文件名称列表
    with open(zip_name_file, 'r') as file:
        zip_names = set(file.read().splitlines())#去除行尾的\n 和 防止重复元素

    match_files = []  # 存储已处理的文件名称
    # try:
    #     with open(processed_file_path, 'r') as file:
    #         processed_files = set(file.read().splitlines())
    # except FileNotFoundError:
    #     processed_files = set()

    # 遍历源目录下的子目录
    for subdir in os.listdir(source_dir):
        subdir_path = os.path.join(source_dir, subdir)
        if os.path.isdir(subdir_path):
            # 遍历子目录下的 ZIP 文件
            for zip_file in os.listdir(subdir_path):
                if zip_file.endswith('.zip') and zip_file in zip_names:
                    zip_file_path = os.path.join(subdir_path, zip_file)

                    # 创建目标子目录
                    target_subdir = os.path.join(destination_dir, subdir)
                    os.makedirs(target_subdir, exist_ok=True)

                    # 移动 ZIP 文件到目标子目录
                    shutil.move(zip_file_path, target_subdir)
                    print(f"Moved {zip_file} to {target_subdir}")

                    # # 解压缩 ZIP 文件
                    # with zipfile.ZipFile(os.path.join(target_subdir, zip_file), 'r') as zip_ref:
                    #     print(f"Processing {zip_file}")
                    #     zip_ref.extractall(extract_dir)
                    #     print(f"Extracted {zip_file} to {extract_dir}")
                        
                    # 更新已处理文件列表
                    match_files.append(zip_file)
                    with open(processed_file_path, 'w') as file:
                        file.write('\n'.join(zip_file))

    # 更新待处理的 ZIP 文件名称列表
    updated_zip_names = zip_names - set(match_files)
    match_zip = len(match_files)
    # 保存更新后的 ZIP 文件名称列表到文件
    with open(updated_zip_names_path, 'w') as file:
        file.write('\n'.join(updated_zip_names))

    print(f"Complete. Matched {match_zip} zip files.")
if __name__ == '__main__':
    args = parser.parse_args(args=[])#jupyter
    # args = parser.parse_args()#python
    # args.des = '/s1/SHARE/sci_hub/med_data/root/'
    # args.ex_dir = '/s1/SHARE/sci_hub/pub_med/root/'
    # args.sou = '/s1/SHARE/sci_hub/Liuyang/root/'
    args.sou = '/s1/SHARE/sci_hub/gao/Mingqi/'
    args.des = '/s1/SHARE/sci_hub/med_data/Mingqi/'
    args.ex_dir = '/s1/SHARE/sci_hub/pub_med/hub1/'
    
    args.zip_name_file= './output/ZipName0322.txt'
    # 调用函数处理 ZIP 文件
    process_zip_files(args)