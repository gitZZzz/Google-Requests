from urllib.parse import urlparse
import re
import base64
from lxml import etree
from selenium.webdriver.firefox.options import Options as FOptions
# from selenium测试.webdriver.chrome.options import Options as FOptions
from selenium import webdriver
import time
import pymysql
import random
import os
import pypyodbc
import pandas as pd

from elasticsearch import Elasticsearch

"""
通过google搜索采购商主页url
1.从es数据库的hs_compy_contact索引内遍历查询每条数据
2.根据每条数据的hs_compy_id去hs_buyer索引查询该hs_compy_id的name值
3.通过谷歌搜索该name的主页url
4.把主页url更新到hs_compy_contact索引的website字段
"""


class Google(object):
    """
    selenium谷歌获取采购方主页链接
    """

    def __init__(self):
        # self.url = 'https://www.baidu.com/s?&wd={}&rqlang=en'
        # self.headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        # }
        # self.dns = 'https://www.baidu.com'
        BASE_DIR = os.path.dirname(__file__)  # 获取当前文件夹的绝对路径
        self.file_path = os.path.join(BASE_DIR, 'addresses.mdb')
        # self.conn = pypyodbc.connect("Driver={Microsoft Access Driver (*.mdb,*.accdb)};DBQ=" + self.file_path)
        # self.conn = pypyodbc.win_connect_mdb("Driver={Microsoft Access Driver (*.mdb,*.accdb)};DBQ=" + r'D:\zp\project\SEO\addresses.mdb')
        # self.cur = self.conn.cursor()

        # self.options = webdriver.FirefoxOptions()
        # self.browser = webdriver.Firefox(firefox_options=self.options)  # 火狐浏览器

        self.options = webdriver.ChromeOptions()
        # self.options.add_argument("-headless")  # 无头模式
        # self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=self.options)  # 谷歌浏览器

    def read_excel(self):
        """
        读取关键字excel表格
        :return: 关键字列表
        """
        try:
            df = pd.read_excel('keyword.xlsx')
            data = df.values  # 读取excel表内所有行数据
            keyword_lt = []
            for i in data:
                keyword_lt.append(i[0])
            return keyword_lt

        except Exception as e:
            print('读取excel表时出错,以下是错误信息')
            print(e)

    def get_one(self, wd):
        """
        获取谷歌搜索第一页的页面源码
        :param wd:
        :return:
        """
        time.sleep(random.uniform(3, 5))  # 每一页请求休眠时间

        self.browser.get('https://www.google.com.hk/search?q={}&oq={}'.format(wd, wd))
        if '异常流量' in self.browser.page_source:
            print('谷歌搜索出现验证码,请手动打开谷歌首页破解验证码或等待一段时间再进行爬取')
            return None

        return self.browser.page_source

    def get_page_list(self, page_source, pages):
        """
        获取搜索结果第2页到指定页数的url
        :param page_source: 第一页的页面源码
        :param page: 搜索的最后一页页码数
        :return: 第2页到指定最后一页的url地址列表
        """
        html = etree.HTML(page_source)

        page_lt = []  # 第2页到第n页搜索结果的url,::     /s?wd=abc&pn=10&oq=abc&ie=utf-8&rsv_idx=1&rsv_pq=91736694000be881&rsv_t=e6b28%2B1Hyp4RUkim%2FuDxElWoPVhmb3AVWn1Xy5%2F16Ss4Qc%2B95PLE3Dmt8tA&sl_lang=en&rsv_srlang=en
        try:
            for i in range(2, pages + 1):
                page_url = 'https://www.google.com' + html.xpath('//a[@aria-label="Page {}"]/@href'.format(i))[0]
                # print('page_url::::', page_url)
                page_lt.append(page_url)
        except:
            pass

        return page_lt

    def analysis_source(self, url):
        """
        解析页面源码
        :param url: url地址
        :return: 页面源码
        """
        time.sleep(random.uniform(3, 5))  # 每一页请求休眠时间
        self.browser.get(url)
        if '异常流量' in self.browser.page_source:
            print('谷歌搜索出现验证码,请手动打开谷歌首页破解验证码或等待一段时间再进行爬取')
            return None
        return self.browser.page_source

    def get_data(self, page_source):
        """
        解析页面中搜索结果的标题和摘要
        :param page_source:每一页的页面源码
        :return: 返回当前页标题列表和摘要列表
        """
        rst = []  # 存储标题和摘要 [['标题1','摘要1'],['标题2','摘要2'],['标题3','摘要3'],......]
        html = etree.HTML(page_source)
        node = html.xpath('//div[@class="srg"]/div[@class="g"]')  # 每一条搜索结果的元素列表
        for j in node:
            j_test = []
            j_html_test = str(etree.tostring(j), encoding="utf-8")
            j_html = etree.HTML(j_html_test)

            try:
                j_title = j_html.xpath('//h3')[0].xpath('string(.)').strip()  # 标题
                j_text = j_html.xpath('//div[@class="s"]//span')[0].xpath('string(.)').strip()  # 摘要
                print('j_title::', j_title)
                print('j_text::', j_text)
            except Exception as e:

                print('异常', e)
                continue

            j_test.append(j_title)
            j_test.append(j_text)
            rst.append(j_test)

        df_title = []
        df_text = []
        for q in rst:
            df_title.append(q[0])
            df_text.append(q[1])
        # for w in rst:
        #     print(w)
        return df_title, df_text, rst

    # =============================================================

    def run(self):
        # 清空原有的数据
        # 获取用户输入搜索关键字和页数
        pages = int(input('请输入查询的前几页的页数:'))
        keyword_lt = self.read_excel()  # 关键字列表 keyword_lt=['key1','key2',....]

        # 循环关键字列表获取采集内容
        for k in keyword_lt:
            print('{} 当前爬取关键字::{}-{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), keyword_lt.index(k),
                                             k))

            # 当前关键字所有搜索结果字典
            pd_dict = {
                '标题': [],
                '摘要': []
            }
            writer = pd.ExcelWriter('excel/{}.xlsx'.format(k))  # 创建excel表
            page_source_lt = []  # 1~指定页页面源码

            page_source = self.get_one(k)  # 获取第一页源码
            if page_source == None:
                return
            page_source_lt.append(page_source)  # 把页面源码添加到 page_source_lt 列表
            page_lt = self.get_page_list(page_source, pages)  # 第2页~指定页的url列表
            # 循环获取每一页页面源码并添加到page_source_lt列表内
            for i in page_lt:
                rst_text = self.analysis_source(i)
                page_source_lt.append(rst_text)
            for y in page_source_lt:  # 循环获取每一页的所有标题和摘要
                df_title, df_text, rst = self.get_data(y)  # rst: 最终数据
                pd_dict['标题'] += df_title
                pd_dict['摘要'] += df_text
            # 把搜索结果写入excel表
            df = pd.DataFrame(pd_dict)
            df.to_excel(writer, 'Sheet1')
            writer.save()
            print('保存到excel')

        print('所有关键字已爬取完毕,共计 {} 个'.format(len(keyword_lt)))
        self.browser.quit()


if __name__ == '__main__':
    google = Google()
    google.run()
