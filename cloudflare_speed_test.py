#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 本脚本只支持linux x86-64/arm-64
# 同时更新hosts 的docker镜像列表
DOCKERS = ['qbittorrent', 'transmission', 'moviepilot']
import json
import os
import socket
import time
from datetime import datetime
import requests


def execute(cmd: str) -> str:
    try:
        with os.popen(cmd) as p:
            return p.readline().strip()
    except Exception as err:
        print(str(err))
        return ""


def __os_install(download_url, release_version):
    # 删除 .gz
    if os.path.exists(gz_file_path):
        os.remove(gz_file_path)
    # os.system(f'wget -P {_cf_path} https://ghproxy.com/{download_url}')
    # os.system(f'curl {download_url} -O {gz_file_path}')
    try:
        # 发送 HTTP GET 请求
        response = requests.get(download_url, stream=True)
        # 检查响应状态码
        response.raise_for_status()

        # 以二进制写入模式打开文件
        with open(gz_file_path, 'wb') as file0:
            # 分块写入文件
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file0.write(chunk)
        print(f"{gz_file_path} 下载压缩包成功")
    except requests.exceptions.RequestException as e:
        print(f"下载过程中出现错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

    # 判断是否下载好安装包
    if os.path.exists(gz_file_path):
        if os.path.exists(binary_file_path):
            os.remove(binary_file_path)
        # 解压
        os.system(f'{unzip_command}')
        # 删除压缩包
        os.remove(gz_file_path)
    # 是否有命令行文件
    if os.path.exists(binary_file_path):
        print(f"{_binary_name}更新成功，当前版本：{release_version}")
        with open(cur_version_file_path, 'w') as file1:
            file1.write(release_version)
    else:
        print(f"CloudflareSpeedTest安装失败，请检查")
        exit(-10)


def check_tcp_connection(index, ip, timeout=5):
    if not ip:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result80 = sock.connect_ex((ip, 80))
    result443 = sock.connect_ex((ip, 443))
    if result80 == 0 and result443 == 0:
        print(f"    index={index} {ip} 80,443 的TCP连接均正常")
        sock.close()
        return True
    sock.close()
    if result80 != 0:
        print(f"    index={index} {ip} 80 的TCP连接失败")
    elif result443 != 0:
        print(f"    index={index} {ip} 443 的TCP连接失败")
    return False


def get_new_version_by_github():
    try:
        response = requests.request("get",
                                    "https://api.github.com/repos/XIU2/CloudflareSpeedTest/releases/latest")
        new_version = f"{response.json()['tag_name']}".strip()
        return new_version
    except Exception as err:
        print(f'获取github 最新版本出错:{err}')
    return None


# 写入系统host信息
def append_host_file(append_content: str) -> str:
    hostFile = HOST_PATH
    # 拆分路径和文件名
    directory = os.path.dirname(hostFile)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # 如果目录不存在，创建目录
    if not os.path.exists(hostFile):
        # 创建空文件
        try:
            open(hostFile, 'w').close()
            print(f"成功创建文件：{hostFile}")
        except Exception as e:
            print(f"创建文件时出错：{e}")

    new_hosts_content = ""
    with open(hostFile, "r", encoding="utf-8") as f:
        # 之前是否已经写过dns信息
        flag = False
        for eachLine in f.readlines():
            if r"# Cloudflare IP Start" in eachLine:
                flag = True
            elif r"# Cloudflare IP End" in eachLine:
                flag = False
            else:
                if not flag:
                    new_hosts_content = new_hosts_content + eachLine
        # 写入新的host记录
        new_hosts_content = new_hosts_content.strip()
        new_hosts_content = new_hosts_content + '\n' + append_content
    with open(hostFile, "w", encoding="utf-8") as f:
        f.write(new_hosts_content)
    print(f'---CloudFlare IP已写入系统{HOST_PATH}:')
    print(new_hosts_content)
    return new_hosts_content


def is_cloudflare_domain(domain, retry=3):
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror as e:
        print(f"错误: 无法解析域名 {domain}，错误信息: {e},retry={4 - retry}")
        ip = None
    if ip:
        try:
            response = requests.get(url=f'https://ip.zxinc.org/api.php?type=json&ip={ip}',
                                    timeout=10)
            local = json.loads(response.text)['data']['local']
            if local and 'CloudFlare节点' in local:
                return True
        except Exception as e:
            print(f"错误: 无法获取{domain} {ip}，local信息: {e},retry={4 - retry}")
    if retry > 0:
        return is_cloudflare_domain(domain, retry - 1)
    return False


def get_best_id_and_check_tcp(index):
    ip = execute(f"sed -n '{index},1p' " + _result_file + " | awk -F, '{print $1}'")
    if check_tcp_connection(index, ip):
        return ip
    else:
        return None


HOSTS_TEMPLATE = """# Cloudflare IP Start Update time: {update_time}{content}
# Cloudflare IP End"""
HOST_PATH = '/etc/hosts'
# HOST_PATH = '/volume3/develop/PythonScript/CloudflareST/test_hosts.txt'  # 模拟/etc/hosts
if __name__ == '__main__':
    # 官网 https://github.com/XIU2/CloudflareSpeedTest
    # 1.定义工作目录
    # 获取脚本所在的文件夹绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TO_CHECK_DOMAINS = f'{script_dir}/cloudflare_speed_test.txt'
    _cf_path = f'{script_dir}/CloudflareSpeedTest'
    _additional_args = ''
    _download_prefix = 'https://github.com/XIU2/CloudflareSpeedTest/releases/download'
    _binary_name = 'CloudflareST'
    _cf_ipv4 = os.path.join(_cf_path, "ipv4.txt")
    _cf_ipv6 = os.path.join(_cf_path, "ipv6.txt")
    # _result_file = "result_hosts.txt"
    _result_file = os.path.join(_cf_path, "result_hosts.txt")
    uname = execute('uname -m')
    arch = 'amd64' if uname == 'x86_64' else 'arm64'
    cf_file_name = f'CloudflareST_linux_{arch}.tar.gz'
    gz_file_path = os.path.join(_cf_path, cf_file_name)
    binary_file_path = os.path.join(_cf_path, _binary_name)
    cur_version_file_path = os.path.join(_cf_path, 'cache_cur_version.txt')

    unzip_command = f"tar -zxf {_cf_path}/{cf_file_name} -C {_cf_path}"

    # 2.检查脚本更新
    now = time.time()
    datetime0 = datetime.fromtimestamp(now).strftime("%Y-%m-%d_%H:%M:%S")
    # 创建目录
    if not os.path.exists(_cf_path):
        os.mkdir(_cf_path)
    # 首次运行,先从国内gitee下载一份v2.2.5
    # 是否有命令行文件
    if not os.path.exists(binary_file_path):
        print("---首次运行,先从国内gitee下载一份 v2.2.5")
        lanzouyun_download_url = 'https://gitee.com/abcdef789/cloudflare_speed_test/raw/master/CloudflareST_linux_amd64.tar.gz' if uname == 'x86_64' else 'https://gitee.com/abcdef789/cloudflare_speed_test/raw/master/CloudflareST_linux_arm64.tar.gz'
        __os_install(lanzouyun_download_url, 'v2.2.5')
    # 获取github CloudflareSpeedTest最新版本,如果有就更新
    new_version = get_new_version_by_github()
    cur_version = None
    if os.path.exists(cur_version_file_path):
        with open(cur_version_file_path, 'r') as file:
            cur_version = file.readline().strip()
    if new_version and new_version != cur_version:
        download_url = f'{_download_prefix}/{new_version}/{cf_file_name}'
        __os_install(download_url, new_version)

    # 3.运行CloudflareST,找出最快 IP
    if os.path.exists(binary_file_path):
        print(f"---开始进行CLoudflare IP优选 {datetime0} ")
        if not os.path.exists(_result_file):
            with open(_result_file, 'w') as file:
                pass  # 这里使用 pass 语句，因为我们只是想创建一个空文件，不需要写入任何内容
        cf_command = f'cd {_cf_path} && chmod a+x {_binary_name} && ./{_binary_name} {_additional_args} -o {_result_file} >/dev/null 2>&1'
        os.system(cf_command)
        time.sleep(1)
    best_ip = None
    if os.path.exists(_result_file):
        for i in range(2, 12):
            result_ip = get_best_id_and_check_tcp(i)
            if result_ip:
                best_ip = result_ip
                break
    # todo
    # best_ip = '104.25.244.89'
    # 4.读取待替换域名列表,检查是否为优选ip,批量替换
    if best_ip:
        print(f"---获取到最优ip {best_ip},开始筛选CloudFlare 域名")
        # 开始替换
        to_check_domains_content = f'#---以下域名已替换为CF 优选IP[{best_ip}] {datetime0}'  # 待写入.txt的内容
        cf_domains_set = set()
        not_cf_domains_set = set()

        with open(TO_CHECK_DOMAINS, "r", encoding="utf-8") as f:
            for eachLine in f.readlines():
                domain = eachLine.strip()
                if not domain:
                    pass
                elif domain.startswith('#---'):
                    pass
                elif domain.startswith('#'):  # 注释行,添加到最前
                    to_check_domains_content = f"{domain}\n{to_check_domains_content}"
                else:  # 正常domain
                    if is_cloudflare_domain(domain):
                        cf_domains_set.add(domain)
                    else:
                        not_cf_domains_set.add(domain)
        if cf_domains_set:
            hosts_content = ""  # 待写入 host 文件的cf优选部分内容
            for domain in cf_domains_set:
                hosts_content += f"\n{best_ip}	{domain}"
                to_check_domains_content += f"\n{domain}"
            hosts_content = HOSTS_TEMPLATE.format(content=hosts_content, update_time=datetime0)
            new_hosts_content = append_host_file(hosts_content)
            if new_hosts_content and DOCKERS:
                for docker in DOCKERS:
                    cmd = f"docker exec {docker} bash -c 'echo \"{new_hosts_content}\" > /etc/hosts'"
                    result = execute(cmd)
                    print(f'---CloudFlare IP已写入 docker({docker}) {result}')

        if not_cf_domains_set:
            to_check_domains_content += f'\n#---以下域名不是CloudFlare IP,跳过配置到hosts {datetime0}'  # 待写入.txt的内容
            print(f'---以下域名不是CloudFlare IP,跳过配置到hosts:')
            for domain in not_cf_domains_set:
                to_check_domains_content += f"\n{domain}"
                print(domain)
        # 更新TO_CHECK_DOMAINS
        with open(TO_CHECK_DOMAINS, "w", encoding="utf-8") as f:
            f.write(to_check_domains_content)

        print(f'\nSUCCESS End script, 共耗时:{int(time.time() - now)}s')
