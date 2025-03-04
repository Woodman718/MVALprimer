#!/bin/bash

# 检查参数
if [ -z "$1" ]; then
  echo "Usage: $0 directory_path"
  exit 1
fi

# 设置工作目录和日志文件路径
work_dir="$1"
out_dir="$2"
log_file="${out_dir}$(date +%F-%H%M%S)"

# 过滤文件
find "$work_dir" -type f -name '*.xltd' -exec rm -f {} +
find "$work_dir" -type f -name '*(*' -exec rm -f {} +
find "$work_dir" -type f -size -100k -exec rm -f {} +

# 统计每个子目录文件数
info=$(find "$work_dir" -mindepth 1 -type d -exec sh -c 'echo -n "{}: " && find "{}" -maxdepth 1 -type f | wc -l' \;)

# 过滤文件数为0的目录
file_count_zero=$(echo "$info" | awk -F': ' '$2 == 0 {print $1}')

# 过滤文件数小于100大于0的目录 
less_100_greater_0=$(echo "$info" | awk -F': ' '($2 < 100) && ($2 > 0) {print $1}')

# 创建目录
mkdir -p "${out_dir}zero" "${out_dir}residue"

# 移动目录
echo "$file_count_zero" | xargs -I{} mv {} "${out_dir}zero/" &>> "$log_file_zero.log"
echo "$less_100_greater_0" | xargs -I{} mv {} "${out_dir}residue/"  &>> "$log_file.log"

# 输出日志
echo "Log file is ${log_file}"