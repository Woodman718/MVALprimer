#!/bin/bash
#

#read -p "Input the files path: " paths
paths="$@"

total=0
echo "==$paths=="
for i in  `ls $paths`
do
        printf "\033[33m${i}:\033[0m \t"
        num=`ls ${paths}/$i | wc -l`
        echo "$num"
        let total=($num+$total)
done
echo "total:$total"