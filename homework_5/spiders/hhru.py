# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse

from homework_5.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://izhevsk.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=python&showClusters=true']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacansy_items = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()
        for link in vacansy_items:
            yield response.follow(link, callback=self.vacancy_parse)

    def format_salary(self, salary):
        res = "з/п не указана"
        sal_f = "".join(salary)
        if "от" in sal_f and "до" in sal_f and len(salary) > 3:
            res = {"min_salary": salary[1].replace(u'\xa0', ' '), "max_salary": salary[3].replace(u'\xa0', ' ')}
        elif "от" in sal_f:
            res = {"min_salary": salary[1].replace(u'\xa0', ' '), "max_salary": "не указано"}
        elif "до" in sal_f:
            res = {"min_salary": "не указано", "max_salary": salary[1].replace(u'\xa0', ' ')}
        return res

    def vacancy_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath('//h1[@class=\'header\']//span/text()').extract_first()
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract()
        salary = self.format_salary(salary)
        print(link, name, salary)
        yield JobparserItem(name=name, salary=salary, link=link, site="hh.ru")
