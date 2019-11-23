import requests
from bs4 import BeautifulSoup
from lxml import html
from requests import HTTPError
from user_agent import generate_user_agent


def make_request(url):
    try:
        resp = requests.get(url, headers={"User-Agent": generate_user_agent()})
        resp.raise_for_status()
        return resp.text
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} while parsing hh.ru (maybe number of pages was too big)')


def format_news(url, name, link, time):
    return "-" * 79 + f"\nSite: {url}\nNews_description: {name}\nLink: {link}\nTime: {time}"


def get_lenta_news():
    url = "https://lenta.ru"

    doc = make_request(url)

    if doc is None:
        return

    root = html.fromstring(doc)
    items = root.xpath('//div[contains(@class, "item")]')
    item1_info = items[0].xpath("h2/a")[0]
    print(format_news(url, item1_info.text_content()[5:], url + item1_info.attrib["href"],
                      item1_info.xpath("time/@datetime")[0]))
    for elem in items[1:10]:
        for a_tag, time_tag in zip(elem.xpath("a"), elem.xpath("a/time/@datetime")):
            print(format_news(url, a_tag.text_content()[5:], url + a_tag.attrib["href"], time_tag))


def find_mail_news_tag(tag):
    return tag.has_attr('href') and (tag["href"] == "//auto.mail.ru/" or tag["href"] == "https://auto.mail.ru/")


def find_full_mail_news_tag(tag):
    return tag.has_attr('href') and tag["href"].startswith("https")


def get_mail_news_info(div):
    title = div.get_text()

    link = div.find(find_full_mail_news_tag)["href"]

    news_info = make_request(link)

    if news_info is None:
        news_time = "error occurred"
        return title, link, news_time

    root = html.fromstring(news_info)

    news_time = " ".join(root.xpath("//span[@datetime]/text()"))
    return title, link, news_time if news_time else "no_time_found"


def get_mail_news():
    url = "https://mail.ru"
    doc = make_request(url)

    if doc is None:
        return

    soup = BeautifulSoup(doc, 'html.parser')
    anchor = soup.find(find_mail_news_tag)
    if anchor["href"].startswith("https:"):
        news_list = list(soup.find_all("div", class_="news__list__item"))
        for div in news_list[:10]:
            title, link, news_time = get_mail_news_info(div)
            print(format_news(url, title, link, news_time))
        for div in news_list[10:13]:
            news_link = div.find(find_full_mail_news_tag)["href"]
            print(format_news(url, div.get_text(), news_link, "no_time_found"))  # time could not be retrieved here
    else:
        for div in anchor.parent.parent.parent.children:
            title, link, news_time = get_mail_news_info(div)
            print(format_news(url, title, link, news_time))


if __name__ == "__main__":
    get_mail_news()
    get_lenta_news()
