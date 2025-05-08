### 本脚本优势
1. 使用简单点，不用先去hosts配置一遍了。一个txt写所有域名，一行一个，然后执行python脚本。
2. 加了国内gitee的v2.2.5版本压缩包，也会自动请求github获取最新版
3. 对各个域名加了检测，不是cf节点的不会配置到hosts
4. 对优选出来的节点进行二次tcp联通行测试，确保能通
5. 可以同时更改docker中hosts，不用重启docker。
6. 脚本每一行代码都透明安全，都写在下边了

### 步骤
1. 从教程下载脚本保存为 cloudflare_speed_test.py 放到nas上某个文件夹下
2. 同文件夹下新建cloudflare_speed_test.txt 文件，写你要优选的站点的域名，一行一个，# 号开头的行会忽略。
3. 执行python /volume3/develop/PythonScript/CloudflareST/cloudflare_speed_test.py 就会更新 /etc/hosts文件了，如果想同时修改docker的，把docker 容器名称加到脚本DOCKERS 列表字段中。可以配置为定时任务

注意：本脚本只支持linux x86-64/arm-64，其他系统可以基于这个改改
<img width="432" alt="image" src="https://github.com/user-attachments/assets/8f60607e-48e0-49dc-b02b-c4dedcf26dcf" />
<img width="308" alt="image" src="https://github.com/user-attachments/assets/5c473b02-8fb1-48e5-bcbc-7f03a33be5ed" />
<img width="583" alt="image" src="https://github.com/user-attachments/assets/ccb173d0-d7f3-47d3-818c-07e1eefc32cf" />
<img width="716" alt="image" src="https://github.com/user-attachments/assets/e416f648-db1f-4407-bbe8-cc4aeebf335c" />

欢迎大家提意见
