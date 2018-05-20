# -*- coding: utf-8 -*-
import scrapy
from zhihuusers.items import UsersItem
import json

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    users_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    users_query = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topic'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def start_requests(self):
        yield scrapy.Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20), callback=self.parse_index)
        yield scrapy.Request(self.users_url.format(user=self.start_user, include=self.users_query), callback=self.parse_detail)
        yield scrapy.Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20), callback=self.parse_index)

    def parse_index(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.users_url.format(user=result.get('url_token'), include=self.users_query), callback=self.parse_detail)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page, callback=self.parse_index)

    def parse_index2(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield scrapy.Request(self.users_url.format(user=result.get('url_token'), include=self.users_query),callback=self.parse_detail)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield scrapy.Request(next_page, callback=self.parse_index2)

    def parse_detail(self, response):
        result = json.loads(response.text)
        item = UsersItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield scrapy.Request(self.follows_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20), callback=self.parse_index)
        yield scrapy.Request(self.followers_url.format(user=result.get('url_token'), include=self.followers_query, offset=0, limit=20), callback=self.parse_index2)





