import re
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from requests.exceptions import HTTPError
from user_agent import generate_user_agent


def format_data(name, link, salary, site):
    min_max = False
    if "—" in salary:
        min_s, max_s = salary.split("—")
        min_s = float("".join(re.findall(r"\d+", min_s)))
        min_max = True
    elif "-" in salary:
        min_s, max_s = salary.split("-")
        min_s = float("".join(re.findall(r"\d+", min_s)))
        min_max = True
    elif "от" in salary.lower():
        min_s = re.search(r"от\s*(\d+[^до]*)(до|руб|kzt|₽|USD)", salary.lower())
        min_s = float("".join(re.findall(r"\d+", min_s.group(1)))) if min_s else salary
        max_s = "-"
        min_max = True
    else:
        return {"name": name, "link": link, "salary": salary, "site": site}

    if min_max:
        return {"name": name, "link": link, "min_salary": min_s, "max_salary": max_s, "site": site}


def make_request(url, params):
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": generate_user_agent()})
        resp.raise_for_status()
        return resp.text
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} while parsing hh.ru (maybe number of pages was too big)')


def parse_hh(vacancy, pages, collection, mode="unique"):
    search_url = "https://hh.ru/search/vacancy"

    for page in range(pages):

        time.sleep(1)

        params = {"text": f"{vacancy}", "page": f"{page}"}

        html = make_request(search_url, params=params)

        if html is None:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        job_list = soup.find_all("div", class_="vacancy-serp-item")
        for job in job_list:
            link = job.find('a').get('href', 'no link')
            name = job.find('a').get_text()
            salary_div = job.find("div", class_="vacancy-serp-item__compensation")
            salary = "З/П не указана"
            if salary_div:
                salary = salary_div.get_text()

            if mode == "unique":
                if not collection.find_one({"link": link}):
                    collection.insert_one(format_data(name, link, salary, "hh.ru"))
            else:
                collection.insert_one(format_data(name, link, salary, "hh.ru"))


def parse_superjob(vacancy, pages, collection, mode="unique"):
    base_url = "https://www.superjob.ru"
    search_url = "https://www.superjob.ru/vacancy/search"

    for page in range(1, pages + 1):

        time.sleep(1)

        params = {"keywords": f"{vacancy}", "page": f"{page}", "geo[c][0]": "1"}

        html = make_request(search_url, params=params)

        if html is None:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        for job in soup.find_all("div", class_="f-test-vacancy-item"):
            links = job.find_all("a")
            vac_link = "No link"
            for link in links:
                if not (link.get("href", "No link").startswith("/clients")):
                    vac_link = link.get("href")
                    break

            job_html = make_request(base_url + vac_link, params={})
            job_soup = BeautifulSoup(job_html, 'html.parser')
            job_info = job_soup.find("div", class_="_3MVeX")

            name = job_info.find("h1").get_text()
            salary = job_info.find("span", class_="_3mfro _2Wp8I ZON4b PlM3e _2JVkc").get_text()

            if mode == "unique":
                if not collection.find_one({"link": base_url + vac_link}):
                    collection.insert_one(format_data(name, base_url + vac_link, salary, "superjob.ru"))
            else:
                collection.insert_one(format_data(name, base_url + vac_link, salary, "superjob.ru"))


def search_job(salary, collection):
    for job in collection.find({"min_salary": {"$gt": salary}}):
        print(
            "-" * 79 + f"\n{job['name']} ({job['link']})\nMin salary: {job['min_salary']}\nMax salary: {job['max_salary']}\nSite: {job['site']}")


def main():
    action = input(
        "Что вы хотите сделать? Нажмите 1 чтобы сохранить вакансии, 2 чтобы сохранить вакансии без повторений, "
        "3 чтобы вывести вакансии с З/П больше указанной: ")

    client = MongoClient('localhost', 27017)
    db = client.jobs_database
    collection = db.jobs

    if action == "1":
        position = input("Введите должность: ")  # python
        page_num = int(input("Введите кол-во страниц: "))  # 2
        parse_hh(position, page_num, collection, mode="all")
        parse_superjob(position, page_num, collection, mode="all")
    elif action == "2":
        position = input("Введите должность: ")  # python
        page_num = int(input("Введите кол-во страниц: "))  # 2
        parse_hh(position, page_num, collection, mode="unique")
        parse_superjob(position, page_num, collection, mode="unique")
    elif action == "3":
        salary = float(input("Введите зарплату(в рублях): "))  # допустим
        search_job(salary, collection)


if __name__ == "__main__":
    main()
