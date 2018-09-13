# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi   # 将mysqldb操作变为异步化操作
import MySQLdb
import MySQLdb.cursors
class ArticlespidPipeline(object):
    def process_item(self, item, spider):
        return item
class JsonWithEncodingPipeline(object): #拦截item 保存到数据库当中
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")
    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()
class MysqlPipeline(object):
    def __init__(self):  #功能使对数据库进行连接
        self.conn = MySQLdb.connect('localhost','root','','crticle_spater',charset='utf8',use_unicode=True)  # 密码为空就为空的   但是得写空
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title,url,create_date, fav_nums,content)
            VALUES (%s, %s, %s, %s, %s)  # sql语句的占位符 
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"], item["content"]))
        self.conn.commit()
class MysqlTwistedPipleline(object): #完成mysql插入的异步化
    #使用的mysqldb的一个库
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls,settings): #第一个参数 cls就是当前类的名字
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL-PASSWORD"],
            charset = 'utf-8',
            cursorclass = MySQLdb.cursors,
            use_unicode = True,
        )#把这些参数放在dict中在这样 在 adbapi中传入参数 更加方便
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms) #第一个参数 是模块名
        return cls(dbpool) # 相当于类的实例化
    def process_item(self, item, spider):
        #使用twisted 将mysql 插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error) #处理异常
    def handle_error(self, failue):
        #处理异步插入的异常
        print(failue)
    def do_insert(self, cursor, item):
        #执行具体的插入
        insert_sql = """
                    insert into article(title,url,create_date, fav_nums,content)
                    VALUES (%s, %s, %s, %s, %s)  # sql语句的占位符 
                """
        cursor.execute(insert_sql,(item["title"], item["url"], item["create_date"], item["fav_nums"], item["content"]))

class JsonExporterPipleline(object): #提高爬虫的速度 数据的准确性
   # 调用scrapy 提供的json export 导出json文件
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding="utf-8",ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info): # 这个函数 获得文件重载下载地址
        for ok, value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path   #图片下载的路径保存
        return item
