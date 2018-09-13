# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from scrapy.http import Request
from ArticleSpid.items import JobBoleArticleItem
from ArticleSpid.utils.common import get_md5
from w3lib.html import remove_tags
import datetime
from scrapy.loader import ItemLoader
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
    def parse(self, response):
        """
        1.获取文章列表页中的文章URL并交给scrapy下载后并进行解析
        2.获取下一页的URL并交给scrapy进行下载，下载完成后交给parse

        """
        #解析列表页中所有文章URL
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta={"front_image_url":image_url},callback=self.parse_detail)   # 域名连接作用
            #提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse)
    def parse_detail(self,response):
        #提取具体字段
        # re_selector_l = response.xpath('//*[@id="post-114214"]/div[3]/p[1]')
        # re_selector = response.xpath('//*[@id="post-114214"]/div[1]/h1/text()')
        # re_selector_2=response.xpath('//*[@id="post-114214"]/div[2]/p')
        # creat_data=response.xpath('//*[@id="post-114214"]/div[2]/p/text()').extract()[0].strip().replace("·", "").strip()
        # praise_nums = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0])
        # fav_nums = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]
        # r=re.match(r".*?(\d+).*",fav_nums)
        # if r:
        #     fav_nums = int(r.group(1))
        # else:
        #     fav_nums = 0
        # comments_nums = response.xpath("//a[@href='#article-comment']/span").extract()[0]
        # r1 = re.match(r".*?(\d+).*",comments_nums)
        # if r1:
        #     comments_nums = int(r1.group(1))
        # else:
        #     comments_nums = 0

        #通过css选择器提取字段
        article_item = JobBoleArticleItem() #然后对他进行填充
        front_image_url = response.meta.get("front_image_url","")
        title = response.css(".entry-header h1::text").extract_first("")
        title1 = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip()
        create_date = response.xpath('//*[@id="post-114214"]/div[2]/p/text()').extract_first("").strip().replace("·","").strip()
        praise_nums = response.css(".vote-post-up h10::text").extract_first("")
        r3=re.match(r".*?(\d+).*",praise_nums)
        if r3:
            praise_nums = int(r3.group(1))
        else:
            praise_nums = 0
        fav_nums = response.css("span.bookmark-btn::text").extract()[0]
        r=re.match(r".*?(\d+).*",fav_nums)
        if r:
            fav_nums = int(r.group(1))
        else:
            fav_nums = 0
        comments_nums = response.css("span.hide-on-480::text").extract()[0]
        r2 = re.match(r".*?(\d+).*",comments_nums)
        if r2:
            comments_nums = int(r2.group(1))
        else:
            comments_nums = 0
        # content = response.xpath('//div[@class="entry"]') # xpath 用外面用单引号 ，class里面用双引号
        # content = content.xpath('string(.)').extract()[0].replace(' ', '').replace('\r\n', '').replace('\t', '').replace('\n','')
        # print(content)
        content = response.css("div.entry").extract()[0].replace('\n','').replace('\r','').replace(' ','').replace('\t','').replace('\xa0','') ###去除HTML标签方法 记住后面必须带[0]
        content = remove_tags(content)
        print(content)
        tags=response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tagdata=response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip()
        tags=",".join(tagdata)
        #字段的填充
        article_item["title"] = title
        article_item["url"] = response.url
        try:
             create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
             create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comments_nums"] = comments_nums
        article_item["tags"] = tags
        article_item["content"] = content
        article_item["url_object_id"]=get_md5(response.url)
        #通过item loader 加载item
        # item_loader = ItemLoader(item = JobBoleArticleItem(),response = response) # 定义一个itemloader 进行实列
        # item_loader.add_css("title",".entry-header h1::text")
        # item_loader.add_value("front_image_url",[front_image_url])
        # item_loader.add_xpath("create_date",'//*[@id="post-114214"]/div[2]/p/text()')
        # item_loader.add_css("praise_nums",".vote-post-up h10::text")
        # item_loader.add_css("comments_nums","span.hide-on-480::text")
        # item_loader.add_css("fav_nums","span.bookmark-btn::text")
        # item_loader.add_value("url",response.url)  # 因为url是直接获取的 所以直接value 值来匹配
        # item_loader.add_value("url_object_id",get_md5(response.url))
        # item_loader.add_css("tags","p.entry-meta-hide-on-mobile::text")
        # item_loader.add_css("content","div.entry")
        # article_item = item_loader.load_item()  # 响应函数
        yield article_item
