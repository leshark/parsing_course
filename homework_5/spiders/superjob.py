# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.http import HtmlResponse

from homework_5.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo[c][0]=1']

    def parse(self, response: HtmlResponse):
        next_page = response.css("a[rel='next']::attr(href)").extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancy_items = response.css(
            "a[href*='vakansii']::attr(href)").extract()
        for link in vacancy_items:
            yield response.follow("https://www.superjob.ru" + link, callback=self.vacancy_parse)

    def format_salary(self, s1, s2):
        if "от" in s1:
            return {"min_s": "".join(re.findall(r"\d+", "".join(s2))), "max_s": "не указано"}
        elif not s2:
            return "По договорённости"
        else:
            s2 = "".join(s2).replace(u'\xa0', ' ').split("—")
            return {"min_s": s2[0], "max_s": s2[1]}

    def vacancy_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath('//h1/text()').extract_first()
        salary1 = response.xpath("//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']/text()").extract()
        salary2 = response.xpath("//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']/span/text()").extract()
        salary = self.format_salary(salary1, salary2)
        print(link, name, salary)
        yield JobparserItem(name=name, salary=salary, link=link, site="superjob.ru")
