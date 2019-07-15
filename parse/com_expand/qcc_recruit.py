#! /usr/bin/env python3
# -*- coding:utf-8 -*-
"""
企查查-招聘 信息采集
"""
import time
import random
import requests

from lxml import etree

from support.others import DealKey as dk
from support.use_mysql import ConnMysql as db
from support.others import TimeInfo as tm
from support.headers import GeneralHeaders as gh
from parse.com_common.common import GeneralMethod as gm

class RecruitInfo():
    def __init__(self):
        self.dk = dk()
        self.db = db()
        self.tm = tm()
        self.gh = gh()
        self.gm = gm()
        self.index_url = 'https://www.qichacha.com/'

    def sql(self): #输出需要的sql查询结果
        sel = """
        SELECT com_id,com_name FROM `com_info`
        WHERE origin IS NOT NULL
        AND chain = '微电子产业'
        AND status_recruit IS NULL
        AND LENGTH(com_id) > 8
        ORDER BY RAND() LIMIT 1;
        """
        # sel = """
        # SELECT com_id,com_name FROM com_info
        # WHERE area ='广东省'
        # AND origin is not null
        # AND chain ='虚拟现实'
        # AND status_recruit is null
        # ORDER BY RAND() LIMIT 1;
        # """
        # sel = """
        # SELECT com_id,com_name FROM com_info
        # WHERE status_recruit is null
        # AND com_id IN(
        # '09a2b97c0596a84cf14404a4bd2c37d5',
        # '18ff2c7ad1d11bfe40e0bec84f6d04d3',
        # '1b16bbdae1540c6a72cd81d918b7c1f6',
        # '30c09ef2def97bd3dc8d021fc2233b05',
        # '424b1559bdac92d298cf9751979eb26b',
        # '47967ccec9d2e681d6f478e0dd16e0b9',
        # '48431ef3f2c62cc60e1f4c22a178ee50',
        # '4c468b205f73f703274e9db7f769a03f',
        # '5602135acdc60cd54daf58cffbc24367',
        # '61b780963a4bc4df5707fe376e41fb6f',
        # '652177a5d80be3d70d7460a09018f599',
        # '722e57a557a857c16121d5c03bd06d42',
        # '7bb7f10fbffbdb6af869af34e8697ecc',
        # '89d337c3d33410e68ca65d7933bd7d05',
        # '8ad8b2d2c15fb92f9ce14107489e83cd',
        # 'a484e7a0b3167f6b257beb51dd93b241',
        # 'a58533710987ecf98159545b61505a74',
        # 'a5a0ba522ce994fb2a8de3a7625534e1',
        # 'a9aa7de83d5d7b4c5008310395b1f403',
        # 'ad797adc3b0a3fe293a0d7238c671b72',
        # 'af8ef0be6adcc6cc6c5b5d1c217b487c',
        # 'b45f3cc43a98aa52f5b3409cef1d6cd9',
        # 'dbe7a5624002aec7b0f26445c94f60cc',
        # 'e06f5af040745430aec2faf8684ae3c7',
        # 'f11933e8723fd03d325529bd2adc19a6',
        # 'fa078a468930c63c92f7909b5a1c5788',
        # 'ff0e1ff937b7aaa29b8953a54c978fe8')
        # ORDER BY RAND() LIMIT 1;
        # """
        # sel = """
        # SELECT com_id,com_name FROM `com_info`
        # WHERE com_id = 'bfcd4f4c8b4dd119556e518c9167b8fd'
        # """
        return sel

    def get_column(self,sql): #接收sql语句，返回结果
        result = RecruitInfo().db.selsts(sql)[0]
        return result #返回元祖数据

    def count_rc_judge( self,com_id): #根据公司首页招聘字段判断招聘数量，模糊判断，需做二次判断
        if com_id == None:
            count_rc = 0
        else:
            com_url = f'https://www.qichacha.com/firm_{com_id}.html'
            hds = gh().header()
            time.sleep(random.randint(3, 5))
            res = requests.get(com_url, headers=hds).text
            tree = self.gm.verify(res)
            try:
                count_rc = tree.xpath('//div[@class="company-nav-items"]/span[contains(text(),"招聘")]/span/text()|//div[@class="company-nav-items"]/a[@data-pos="joblist"]/span/text()')[0]
                if count_rc == '999+':
                    count_rc = 999
                count_rc = int(count_rc)
            except:
                count_rc = 0
        return count_rc

    def get_count_rc(self,count_rc,key,count,com_id): #根据模糊判断，到招聘详情页判断出精确的招聘数量
        if count_rc > 0:
            info_url = f'https://www.qichacha.com/company_getinfos?unique={com_id}&companyname={key}&tab=run'
            hds = self.gh.header()
            hds.update({'Referer':f'https://www.qichacha.com/firm_{com_id}.html'})
            time.sleep(random.randint(3, 5))
            res = requests.get(info_url, headers=hds).text
            tree = self.gm.verify(res)
            count_rc = tree.xpath('//a[contains(@onclick,"#joblist")]/text()')[0].split('招聘')[1].strip()
            count_rc = int(count_rc)
            localtime = tm().get_localtime()  # 当前时间
            print(localtime)
            print(f'计数器：{count}\n公司ID:{com_id}\n招聘岗位数：{count_rc}')
        else:
            count_rc = 0
            res = 0
        status_column = 'status_recruit'  # 表字段名
        count_column = 'count_recruit'  # 表字段名
        self.gm.upd_status(com_id, status_column, count_column, count_rc)
        return count_rc,res

    def rc_judge(self): #返回精确的招聘数
        # global com_id,com_name,res
        count_rc = 0
        com_id = 1
        count = 0
        while count_rc == 0 and com_id != None:
            count += 1
            sql = RecruitInfo().sql()
            result = RecruitInfo().get_column(sql)
            com_id = result[0]
            com_name = result[1]
            key = dk().search_key(com_name)
            count_rc = RecruitInfo().count_rc_judge(com_id)
            info = RecruitInfo().get_count_rc(count_rc,key,count,com_id)
            count_rc = info[0]
            res = info[1]
        else:
            com_name = com_name
            res = res
        real_count_rc = count_rc
        result = [real_count_rc,com_id,com_name,res]
        return result

    def rc_page_judge(self): #判断页码                                                           #判断是否是最近一或两年的招聘数据
        result = RecruitInfo().rc_judge()
        real_count_rc = result[0]
        com_id = result[1]
        com_name = result[2]
        res = result[3]
        if res == 0 or com_id == None:
            rc_page_count = 0
        else:
            if real_count_rc % 10 == 0:
                rc_page_count = real_count_rc // 10
            else:
                rc_page_count = real_count_rc // 10 + 1
        return rc_page_count,com_id,com_name,res,real_count_rc

    def rc_detail_para(self,com_id,com_name,page): #详情页链接参数
        para = {
            'unique': f'{com_id}',
            'companyname': f'{com_name}',
            'p': page,
            'tab': 'run',
            'box': 'job'
        }
        return para

    def get_info(self,rc_info_li,com_id,page): #解析详情页面代码，获取所需字段
        count = (page-1)*10
        for nbr, info in enumerate(rc_info_li, 1):
            count += 1
            job_id = info.xpath('td[3]/a/@href')[0].split('jobdetail_')[1].strip()
            rc_num = info.xpath('td[1]/text()')[0].strip()
            pub_date = info.xpath('td[2]/text()')[0].strip()
            rc_job = info.xpath('td[3]/a/text()')[0].strip()
            salary = info.xpath('td[4]/text()')[0].strip()
            education = info.xpath('td[5]/text()')[0].strip()
            we = info.xpath('td[6]/text()')[0].strip()
            city = info.xpath('td[7]/text()')[0].strip()
            # print('\n{0}--总第{1}条----{2}/{3}页--{0}\n'.format('-' * 9, count, page, count_page))
            print('\n{0}--总第{1}条----第{2}页----{0}\n'.format('-' * 9,count,page))
            localtime = self.tm.get_localtime()  # 当前时间
            create_time = localtime
            print(f'当前时间：{create_time}')
            print(f'公司ID：{com_id}\n序号:{rc_num}\n岗位ID:{job_id}\n岗位名称:{rc_job}\n发布时间:{pub_date}\n'
                  f'薪资:{salary}\n学历:{education}\n工作经历:{we}\n城市:{city}\n')
            ins = f"""
            INSERT INTO com_recruit 
            (com_id,job_id,rc_num,pub_date,rc_job,
            salary,education,we,city,create_time)
            VALUES 
            ("{com_id}","{job_id}","{rc_num}","{pub_date}","{rc_job}",
            "{salary}","{education}","{we}","{city}","{create_time}");
            """
            self.db.inssts(ins)
        return count

    def rc_info(self): #主循环程序
        rc = RecruitInfo()
        count_cond = rc.verify_cond()
        count = 0
        print('\n{2}\n{1}剩余{0}家企业招聘数据待采集！{1}\n{2}\n'.format(count_cond, '*' * 20, '*' * 63))
        while count_cond > 0:
            print('Loading......\n')
            time.sleep(5)
            print('开始新一轮采集')
            result = rc.rc_page_judge()
            rc_page_count = result[0]
            com_id = result[1]
            com_name = result[2]
            res = result[3]
            real_count_rc = result[4]
            real_count = real_count_rc - 1
            value = True
            while value == True and real_count < real_count_rc:
                for page in range(1,rc_page_count+1):
                    count += 1
                    url = f'{rc.index_url}company_getinfos?'
                    para = rc.rc_detail_para(com_id,com_name,page)
                    hds = self.gh.header()
                    hds.update({'Referer': f'{rc.index_url}firm_{com_id}.html'})
                    time.sleep(random.randint(1, 2))
                    res = requests.get(url,params=para,headers=hds).text
                    tree = self.gm.verify(res)
                    pub_date_li = tree.xpath('//tbody/tr[position()>1]/td[2]/text()')
                    value = rc.verify_year(pub_date_li)
                    if value == False:
                        break
                    rc_info_li = tree.xpath('//tbody/tr[position()>1]')
                    real_count_rc = rc.get_info(rc_info_li,com_id,page)
                real_count = real_count_rc
                value = value
            else:
                print('该企业招聘信息采集结束！')
                time.sleep(3)
            count_cond = rc.verify_cond()
            print('\n{2}\n{1}剩余{0}家企业招聘数据待采集！{1}\n{2}\n'.format(count_cond,'*'*20,'*'*63))
        print('\n数据采集完成！')

    def verify_cond(self):#验证是否符合继续采集的条件
        rc = RecruitInfo()
        sel = """
        SELECT COUNT(*) FROM `com_info`
        WHERE origin IS NOT NULL
        AND chain = '微电子产业'
        AND status_recruit IS NULL
        AND LENGTH(com_id) > 8;
        """
        # sel = """
        # SELECT count(*) FROM `com_info`
        # WHERE origin IS NOT NULL
        # AND status_recruit IS NULL
        # AND LENGTH(com_id) > 8
        # AND com_id IN(
        # '09a2b97c0596a84cf14404a4bd2c37d5',
        # '18ff2c7ad1d11bfe40e0bec84f6d04d3',
        # '1b16bbdae1540c6a72cd81d918b7c1f6',
        # '30c09ef2def97bd3dc8d021fc2233b05',
        # '424b1559bdac92d298cf9751979eb26b',
        # '47967ccec9d2e681d6f478e0dd16e0b9',
        # '48431ef3f2c62cc60e1f4c22a178ee50',
        # '4c468b205f73f703274e9db7f769a03f',
        # '5602135acdc60cd54daf58cffbc24367',
        # '61b780963a4bc4df5707fe376e41fb6f',
        # '652177a5d80be3d70d7460a09018f599',
        # '722e57a557a857c16121d5c03bd06d42',
        # '7bb7f10fbffbdb6af869af34e8697ecc',
        # '89d337c3d33410e68ca65d7933bd7d05',
        # '8ad8b2d2c15fb92f9ce14107489e83cd',
        # 'a484e7a0b3167f6b257beb51dd93b241',
        # 'a58533710987ecf98159545b61505a74',
        # 'a5a0ba522ce994fb2a8de3a7625534e1',
        # 'a9aa7de83d5d7b4c5008310395b1f403',
        # 'ad797adc3b0a3fe293a0d7238c671b72',
        # 'af8ef0be6adcc6cc6c5b5d1c217b487c',
        # 'b45f3cc43a98aa52f5b3409cef1d6cd9',
        # 'dbe7a5624002aec7b0f26445c94f60cc',
        # 'e06f5af040745430aec2faf8684ae3c7',
        # 'f11933e8723fd03d325529bd2adc19a6',
        # 'fa078a468930c63c92f7909b5a1c5788',
        # 'ff0e1ff937b7aaa29b8953a54c978fe8');
        # """
        result = rc.get_column(sel)[0]
        return result


    def verify_year(self,date):
        a = [0,1]
        date_today_stamp = round(time.time())
        if type(date) == type(a):
            value = []
            for dt in date:
                dt = dt.strip()
                if dt == '-':
                    et = 366
                    print('字符串非法！')
                else:
                    date_stamp = time.mktime(time.strptime(dt,'%Y-%m-%d'))
                    date_stamp = round(date_stamp)
                    et = int((date_today_stamp - date_stamp) // (60*60*24))  # 计算时间差,天
                if et >= 366:
                    et = 366
                value.append(et)
            if 366 in value:
                print('招聘发布时间已超过一年,终止采集！')
                return False
            else:
                return True
        else:
            date_stamp = time.mktime(time.strptime(date, '%Y-%m-%d'))
            date_stamp = round(date_stamp)
            print(date_today_stamp,date_stamp)
            et = int((date_today_stamp - date_stamp) // (60 * 60 * 24))  # 计算时间差,天
            print(et)
            if et >= 366:
                print('招聘发布时间已超过一年,终止采集!')
                return False
            else:
                return True

if __name__ == '__main__':
    rc = RecruitInfo()
    # rc.verify_year('2019-05-09')
    # sql = rc.sql()
    # result = rc.get_column(sql)
    rc.rc_info()
    # rc.verify_cond()