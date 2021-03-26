import scrapy
from ..items import UnionbaItem
import re
from scrapy.loader import ItemLoader

from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class UnionbaSpider(scrapy.Spider):
	name = 'unionba'
	start_urls = ['https://www.unionbank.com/about-us/newsroom']

	def parse(self, response):
		articles_count = len(response.xpath('//div[@class="text-block__body"]//a[not (ancestor::section[@componentindex="8"] or ancestor::section[@componentindex="0"])]'))
		for index in range(articles_count):
			date = response.xpath(f'(//div[@class="text-block__body"]/p[contains(text(),"-")][not (ancestor::section[@componentindex="8"])])[{index+1}]/text()').get().split(' - ')[0]
			post_links = response.xpath(f'(//div[@class="text-block__body"]//a[not (ancestor::section[@componentindex="8"] or ancestor::section[@componentindex="0"])])[{index+1}]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):

		title = response.xpath('//div[@class="page-hero-simple__headline"]//text()').get()
		content = response.xpath('//div[@class="text-block__body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=UnionbaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
