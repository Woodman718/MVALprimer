# 打印开始时间
# ex_zip5.sh

start_time=$(date '+%Y-%m-%d %H:%M:%S')
echo "Start time: $start_time"

# 定义输出目录路径变量
# extract_dir="/s1/SHARE/sci_hub/pub_med/Mingqi/"
extract_dir="$1"

# 文件路径,包含所有需要处理的压缩文件路径
zip_files_file="$2"


# 检查参数

if [ -z "$zip_files_file" ]; then
echo "Usage: $0 <zip_files_file>"
exit 1
fi

# 确保输出目录存在

mkdir -p "$extract_dir"

# 日志文件

log_file="unzip_$(date '+%Y%m%d_%H%M%S').log"

export extract_dir
export log_file

# 从文件中读取每个压缩文件路径并解压

cat "$zip_files_file" | parallel -j 4 --bar 'if [ -f "{}" ]; then
echo "Extracting {}" | tee -a "$log_file"
unzip -oqd "$extract_dir" "{}" 2>&1 | tee -a "$log_file"
else
echo "File {} does not exist" | tee -a "$log_file"
fi'

# 打印结束时间

end_time=$(date '+%Y-%m-%d %H:%M:%S')
echo "End time: $end_time" | tee -a "$log_file"
echo "All files processed." | tee -a "$log_file"