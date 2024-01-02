import os
import time
import datetime

import re
import yaml

def extract_yaml_parameters(text):
    # 定义正则表达式模式
    pattern = re.compile(r'---\n(.*?\n)---', re.DOTALL)
    # 在文本中搜索匹配的部分
    match = pattern.search(text)
    if match:
        yaml_content = match.group(1)

        # 将结果解析为字典
        yaml_dict = yaml.safe_load(yaml_content)

        return yaml_dict
    else:
        return None
    
def get_file_list(path,dir_to_ignore=['.']):
    file_list = []
    # ignore .git folder
    for root, dirs, files in os.walk(path):
        for dir in dir_to_ignore:
            if dir in dirs:
                dirs.remove(dir)
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def format_in_hugo_template(dirpath,whether_modify=False,dir_to_ignore=['.git']):
    for file in get_file_list(dirpath,dir_to_ignore):
        if file.endswith('.md'):
            # if file != "D:\\华为云盘\\Desktop\\WorkSpace\\markdown\\【Template】.md":
            #     continue
            ismodify = False
            isfilemodify = False
            isnullheader = False
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            if not re.match(r'\s*---\n', content):
                # 不存在头部信息，创建一个空字典
                yaml_dict = {}
                isnullheader = True
            else:
                yaml_dict = extract_yaml_parameters(content)
            ori_yaml_dict = yaml_dict.copy()
            # if 'abbrlink' in yaml_dict:
            #     yaml_dict.pop('abbrlink')
            #     ismodify = True
            # if 'categories' in yaml_dict:
            #     yaml_dict.pop('categories')
            # #     ismodify = True
            # create_time = os.path.getctime(file)
            # create_time_local = time.localtime(create_time)
            # create_datetime = datetime.datetime.fromtimestamp(create_time)
            # mod_time = os.path.getmtime(file)
            # mod_time_local = time.localtime(mod_time)
            # mod_datetime = datetime.datetime.fromtimestamp(mod_time)
            # if 'date' in yaml_dict:
            #     # 误差在1秒内不处理
            #     if yaml_dict['date'].timestamp() > create_time + 1:
            #         # print('文件创建时间早于头部时间',yaml_dict['date'].timestamp(), create_time)
            #         yaml_dict['date'] = create_datetime
            #         ismodify = True
            # else:
            #     yaml_dict['date'] = create_datetime
            #     ismodify = True
            # if 'lastmod' in yaml_dict:
            #     if yaml_dict['lastmod'].timestamp() < mod_time -1:
            #         # print('文件修改时间晚于头部时间',yaml_dict['lastmod'].timestamp(), mod_time)
            #         yaml_dict['lastmod'] = mod_datetime
            #         ismodify = True
            #         isfilemodify = True
            # else:
            #     # create_time 与 mod_time在同一天
            #     if create_time_local.tm_year == mod_time_local.tm_year and create_time_local.tm_yday == mod_time_local.tm_yday:
            #         pass
            #     else:
            #         yaml_dict['lastmod'] = mod_datetime
            #         ismodify = True
            #         isfilemodify = True
            
            if 'title' in yaml_dict:
                continue
            else:
                yaml_dict['title'] = os.path.basename(file).replace('.md','')
                ismodify = True

            yaml_content = yaml.dump(yaml_dict, allow_unicode=True)
            if isnullheader:
                content = '---\n' + yaml_content + '---\n' + content
            else:
                content = re.sub(r'---\n(.*?\n)---', '---\n' + yaml_content + '---', content, 1, re.DOTALL)
            if ismodify:
                if  not isfilemodify:
                    print("\033[93m[Init]\033[0m"+file)
                else:
                    print("\033[91m[Update]\033[0m"+file)
                if whether_modify == True:
                    with open(file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    # os.utime(file, (create_time, mod_time))
                else:
                    print('[Before]',ori_yaml_dict)
                    print('[After]',yaml_dict)
            else:print('\033[92m[Pass]\033[0m'+file )
        else :
            print("\033[94m[Skip]\033[0m"+file)


if __name__ == '__main__':
    path = os.getcwd()
    path = os.path.join(path,'content/posts')
    format_in_hugo_template(path,False)
    ismodify = input('是否修改文件？(y/n)')
    if ismodify == 'y':
        format_in_hugo_template(path,True)
    else:
        print('已退出')