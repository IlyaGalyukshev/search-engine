import urllib.request
import urllib.parse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
import os


class Parser:
    def __init__(self):
        self.links = []

    def search_ttk(self, ttk_name: str) -> list:
        downloaded_links = []
        cnt = 0
        queries = self.generate_queries(ttk_name)
        search_engines = [
            "https://www.google.com/search?q=",
            "https://www.bing.com/search?q=",
            "https://search.yahoo.com/search?p=",
            "https://duckduckgo.com/?q=",
            "https://yandex.com/search/?text=",
        ]
        for query in queries:
            for engine in search_engines:
                encoded_query = urllib.parse.quote(query)
                url = f"{engine}{encoded_query}"
                user_agent = UserAgent()
                headers = {"User-Agent": user_agent.random}
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    data = response.read()
                if response.getcode() == 200:
                    soup = BeautifulSoup(data.decode("utf-8"), "html.parser")
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        extension = href.split(".")[-1]
                        if extension in ["pdf", "docx", "doc", "rtf"]:
                            if href not in downloaded_links:
                                file_name = f"data/{self.convert_to_file_name(ttk_name)}_{cnt}.{extension}"
                                if self.save_file(href, file_name):
                                    cnt += 1
                                    self.links.append(href)
                                    downloaded_links.append(href)
                                    print(f"{href} was downloaded as {file_name}")
        return self.links

    @staticmethod
    def convert_to_file_name(string: str) -> str:
        return string.lower().replace(" ", "_")

    @staticmethod
    def generate_queries(ttk_name: str) -> list:
        main_queries = [
            f"типовая технологическая карта {ttk_name}",
            f"ТТК {ttk_name}",
            f"{ttk_name} типовая технологическая карта",
            f"{ttk_name} ТТК",
        ]
        extensions = ["pdf", "docx", "doc", "rtf"]
        queries = []
        for query in main_queries:
            for filetype in extensions:
                queries.append(f"{query} filetype:{filetype}")
            queries.append(
                f"{query} filetype:pdf OR filetype:docx OR filetype:doc OR filetype:rtf"
            )
        return queries

    @staticmethod
    def save_file(url: str, path: str) -> bool:
        try:
            user_agent = UserAgent()
            headers = {"User-Agent": user_agent.random}
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request)
            file_size = int(response.headers.get("Content-Length", 0))
            if file_size > 2 * 1024 * 1024:
                return False
            data = response.read()
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(path, "wb") as f:
                f.write(data)
            return True
        except Exception as e:
            print(f"Download failed | {e} | ({path}): {url}")
            return False


data = pd.read_csv("smeta1_bad_works.csv")
ttks = data["Activity Name"]
parser = Parser()
for ttk in ttks[:3]:
    files = parser.search_ttk(ttk)
