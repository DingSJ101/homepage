import os
import time
import datetime
import argparse

import re
import yaml


class YamlHeaderGenerator:
    def __init__(self,path) -> None:
        self.path = path
        self.STATUS = {
            1:"Init",
            2:"Update",
            3:"Pass",
            4:"Skip",
            0:"Summary"
        }
        self.init_counter()
    def init_counter(self):
        self.counter = dict(zip(self.STATUS.keys(),[0]*len(self.STATUS)))
    
    def extract_yaml_parameters(self,text):
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
        
    def get_file_list(self,path,dir_to_ignore=['.']):
        file_list = []
        # ignore .git folder
        for root, dirs, files in os.walk(path):
            for dir in dir_to_ignore:
                if dir in dirs:
                    dirs.remove(dir)
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    def format_in_hugo_template(self,whether_modify=False,dir_to_ignore=['.git']):
        self.init_counter()
        for file in self.get_file_list(self.path,dir_to_ignore):
            if file.endswith('.md'):
                isfilemodify = False
                isnullheader = False
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not re.match(r'\s*---\n', content):
                    # 不存在头部信息，创建一个空字典
                    yaml_dict = {}
                    isnullheader = True
                else:
                    yaml_dict = self.extract_yaml_parameters(content)
                ori_yaml_dict = yaml_dict.copy()
                # if 'abbrlink' in yaml_dict:
                #     yaml_dict.pop('abbrlink')
                # if 'categories' in yaml_dict:
                #     yaml_dict.pop('categories')
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
                # else:
                #     yaml_dict['date'] = create_datetime
                # if 'lastmod' in yaml_dict:
                #     if yaml_dict['lastmod'].timestamp() < mod_time -1:
                #         # print('文件修改时间晚于头部时间',yaml_dict['lastmod'].timestamp(), mod_time)
                #         yaml_dict['lastmod'] = mod_datetime
                #         isfilemodify = True
                # else:
                #     # create_time 与 mod_time在同一天
                #     if create_time_local.tm_year == mod_time_local.tm_year and create_time_local.tm_yday == mod_time_local.tm_yday:
                #         pass
                #     else:
                #         yaml_dict['lastmod'] = mod_datetime
                #         isfilemodify = True
                
                if 'title' in yaml_dict:
                    pass
                else:
                    yaml_dict['title'] = os.path.basename(file).replace('.md','')

                yaml_content = yaml.dump(yaml_dict, allow_unicode=True)
                if isnullheader:
                    content = '---\n' + yaml_content + '---\n' + content
                else:
                    content = re.sub(r'---\n(.*?\n)---', '---\n' + yaml_content + '---', content, 1, re.DOTALL)
                if ori_yaml_dict != yaml_dict:
                    if  not isfilemodify:
                        self.count_file(1,file,output = True)
                    else:
                        self.count_file(2,file,output = True)
                    if whether_modify == True:
                        with open(file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        # os.utime(file, (create_time, mod_time))
                    else:
                        print('[Before]',ori_yaml_dict)
                        print('[After]',yaml_dict)
                else:
                    self.count_file(3,file,output=not whether_modify)
            else :
                self.count_file(4,file,output=not whether_modify)
        self.count_file(0,output = not whether_modify)

    def count_file(self,statu_type:int,filename="",output=True):
        """1:Init,\n2:Update,\n3:Pass,\n4:Skip,\n0:Summary"""
        self.counter[statu_type] += 1
        if output:
            self.print_log(statu_type,filename)
        

    def print_log(self,statu_type:int,content=""):
        OUTPUT = {
            1:"\033[93m[Init]\033[0m"+content,
            2:"\033[91m[Update]\033[0m"+content,
            3:"\033[92m[Pass]\033[0m"+content,
            4:"\033[94m[Skip]\033[0m"+content,
            # 0:"\033[95m[Summary]\033[0m : \n"+ \
            #        "\t\033[93m[Init]\033[0m %d files ,\n\
            #         \t\033[91m[Update]\033[0m %d files ,\n\
            #         \t\033[92m[Pass]\033[0m %d files ,\n\
            #         \t\033[94m[Skip]\033[0m %d files" % \
            #         (self.counter[1],self.counter[2],self.counter[3],self.counter[4])
                    
        }
        if statu_type:
            print(OUTPUT[statu_type])
        elif statu_type == 0:
            print("\033[95m[Summary]\033[0m : ")
            for idx in OUTPUT.keys():
                print("\t",end="")
                self.print_log(idx," %d files" % self.counter[idx])




if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--path', type=str, default='content/posts')
    argparser.add_argument('-y',action='store_true',dest='yes',default=False)
    path = os.getcwd()
    path = os.path.join(path, argparser.parse_args().path)
    generator = YamlHeaderGenerator(path)
    generator.format_in_hugo_template(False)
    if argparser.parse_args().yes:
        generator.format_in_hugo_template(True)
    else:
        ismodify = input('是否修改文件？(y/n)')
        if ismodify == 'y':
            generator.format_in_hugo_template(True)
    print('已退出')