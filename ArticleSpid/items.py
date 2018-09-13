# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

class ArticlespidItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
#只是 另一种添加字段并且获取的方法
# def add_jobbole(value):
#     return value + "pengliang"
#
#
# def date_convert(value):
#     try :
#         create_date = datetime.datetime.strptime(value,"%Y/%m/%d").date()
#     except Exception as e:
#         create_date = datetime.datetime.now().date()
#     return create_date
# class JoBoleArticleItem(scrapy.Item):
#     title = scrapy.Field(
#         input_processor = MapCompose(lambda x:x+"-jobbole")
#     )
#     create_date = scrapy.Field(
#         input_processor = MapCompose(date_convert),
#         output_processor = TakeFirst()
#     )
# 在items 中定义一个类 对于字段的获取 和存储作用
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comments_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()









