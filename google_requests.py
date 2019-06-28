import requests, time, os, pypyodbc
from lxml import etree
import pandas as pd


class GoogleRequests(object):
    """
    requests爬取谷歌关键字结果
    """
    def __init__(self):
        """
        # 创建google.mdb数据库和游标
        if os.path.exists(r'google.mdb') == False:  # 检查是否存在数据库文件
            pypyodbc.win_create_mdb('google.mdb')  # 创建access数据库
        self.BASE_DIR = os.path.dirname(__file__)  # 获取当前文件夹的绝对路径
        self.file_path = os.path.join(self.BASE_DIR, 'google.mdb')
        self.conn = pypyodbc.connect("Driver={Microsoft Access Driver (*.mdb)};DBQ=" + self.file_path)
        self.cur = self.conn.cursor()
        """

    def read_excel(self):
        """
        读取关键字excel表格
        :return: 关键字列表
        """
        try:
            df = pd.read_excel('../keyword.xlsx')
            data = df.values
            keyword_lt = []
            for i in data:
                keyword_lt.append(i[0])
            return keyword_lt

        except Exception as e:
            print('读取excel表时出错,以下是错误信息')
            print(e)

    def access(self):
        """
        创建access数据库表
        :return:
        """
        try:
            self.cur.execute(
                '''CREATE TABLE Content (ID int,已采 VARCHAR(50),已发 VARCHAR(50), 标题 VARCHAR,内容 Text);''')
            self.cur.commit()
        except:
            pass
        try:
            self.cur.execute(
                '''CREATE TABLE Update (ID int,old_str VARCHAR(50),new_str VARCHAR(50));''')
            self.cur.commit()
        except:
            pass

    def run(self):
        # 1.读取excel关键字表
        keyword_lt = self.read_excel()

        # 2.输入爬取页数
        pages = int(input('请输入查询的前几页的页数:'))

        # 3.创建mdb数据库和表,并清空表数据
        # self.access()
        # self.cur.execute("delete from Content")
        # self.cur.commit()

        # 4.遍历搜索关键字列表
        for k in keyword_lt:
            print('{} 当前爬取关键字::{}-{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), keyword_lt.index(k)+1 ,k))
            # 当前关键字所有搜索结果字典
            pd_dict = {
                '标题': [],
                '摘要': []
            }

if __name__ == '__main__':
    google = GoogleRequests()
    google.run()
