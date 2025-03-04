import csv,os,time
import pymysql
# 设置重试连接
pymysql.err.RECONNECT_TIMEOUT = 10
suf = time.strftime("%m%d_%H%M", time.localtime())

connection = pymysql.connect(host='localhost',
                     user='root',
                     password='password',
                     database='SCI_HUB')
cursor = connection.cursor()

with connection.cursor() as cursor:

    sql = """SELECT ID, 
                    DOI, DOI2 FROM scimag"""
    cursor.execute(sql)
    
    results = cursor.fetchall()
  
with open(f'./output/{suf}_data.tsv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, escapechar='\\', quoting=csv.QUOTE_ALL)  
    writer.writerow(['ID','DOI', 'DOI2']) 
    writer.writerows(results)