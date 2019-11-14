import json
import requests

with open("config.json") as cnf:
    TOKEN = json.load(cnf)["token"]

user = "leshark"  # set user here

repos = requests.get(f"https://api.github.com/users/{user}/repos", headers={'Authorization': f'token {TOKEN}'}).json()

for repo in repos:
    print(f'{repo["name"]}: {repo["description"] if repo["description"] else "нет описания"}')
