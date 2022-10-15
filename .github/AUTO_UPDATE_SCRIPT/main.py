import json
import re
import requests
from datetime import timedelta, datetime

result_list = []
api_status = True
max_count = 100
continue_mark = '<!--cont.-->'


def get_start_line(file):
    for index, per_line in enumerate(file):
        if get_short_url(per_line) != -1 and len(per_line) - len(per_line.replace(continue_mark, '')) != 0:
            i = index
            f.seek(0)
            return i
    return 0

# 调整太平洋时间
def change_time(raw_time):
    raw_time = str(raw_time).replace('Z', '')
    txtfmt = raw_time[:10]+ " " + raw_time[11:19]
    dt = datetime.strptime(txtfmt,"%Y-%m-%d %H:%M:%S")
    cur_time = dt + timedelta(hours=8)
    return str(cur_time)

def get_update_time(short_urls):
    global max_count
    max_count -= 1
    request_url = 'https://api.github.com/repos/' + short_urls
    response = requests.get(request_url)
    if response.status_code == 404:
        return -1
    if response.status_code == 403:
        print('API访问达到上限')
        return 0
    if max_count < 0:
        print('API访问达到上限')
        return 0
    print('api访问成功')
    return json.loads(response.text).get('pushed_at')


def get_api_limit():
    request_url = 'https://api.github.com/rate_limit'
    response = requests.get(request_url)
    print('响应状态' + str(response.status_code))
    return json.loads(response.text).get('resources')['core']['remaining']


def get_format_message(basic_message, short_url):
    sign_mount = len(basic_message) - len(basic_message.replace('|', ''))
    global api_status
    if not api_status:
        return basic_message
    update_time = get_update_time(short_url)
    if update_time == -1:
        message = '仓库已失效'
    elif update_time == 0:
        api_status = not api_status
        lines = basic_message.split('|')
        lines[1] = lines[1] + continue_mark
        return '|'.join(lines)
    else:
        message = change_time(update_time)
    if sign_mount < 5:
        return basic_message + str(message) + '|'
    else:
        lines = basic_message.split('|')
        lines[4] = str(message)
        return '|'.join(lines)


def add_line(index, per_line):
    if index <= len(result_list) - 1:
        if api_status:
            result_list[index] = per_line
    else:
        result_list.append(per_line)


def get_short_url(per_line):
    sign_mount = len(per_line) - len(per_line.replace('|', ''))
    urls = re.findall('https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+', per_line)
    if len(urls) != 0 and sign_mount != 0:
        urls = urls[0].replace(')', '').split('/')
        return urls[3] + '/' + urls[4]
    return -1


def read_file(file, start_line):
    pointer = start_line
    for index, per_line in enumerate(file):
        per_line = per_line.replace('\n', '')
        if pointer > -1 and start_line != 0:
            if pointer == 0:
                per_line = per_line.replace(continue_mark, '')
                per_line = get_format_message(per_line, get_short_url(per_line))
            pointer -= 1
            add_line(index, per_line)
            continue
        clean_url = get_short_url(per_line)
        if clean_url != -1:
            if api_status:
                message = get_format_message(per_line, clean_url)
                add_line(index, message)
                continue
        add_line(index, per_line)


if __name__ == '__main__':
    path = 'README.md'
    with open(path, 'r') as f:
        print(get_start_line(f))
        read_file(f, get_start_line(f))
        while api_status:
            f.seek(0)
            read_file(f, 0)
        # for line in result_list:
        #     print(line)
    with open(path, 'w') as f:
        f.write('\n'.join(result_list))
        f.close()
