import argparse
import csv
import logging
import re
import time
from typing import List
from unicodedata import normalize

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class Normalizer:
    @staticmethod
    def remove_spaces(txt: str):
        return re.sub(r"\s", "", txt)


class Crawler:
    def __init__(self, root: str, init_page: str, num_of_cols: int = 13):
        self.logger = logging.getLogger(__name__)
        self.root = root
        self.page = init_page
        self.num_of_cols = num_of_cols
        self.logger.info(f"GET {self.root}{self.page}")
        url = requests.get(self.root + self.page)
        self.soup = BeautifulSoup(url.content, "html.parser")

    @classmethod
    def _remove_spaces(cls, header: str) -> str:
        return header.strip().replace("　", "")

    @classmethod
    def _get_string(cls, elm: Tag) -> str:
        elm_str = elm.string
        if elm_str:
            return cls._remove_spaces(elm_str)
        else:
            return ""

    def get_header(self) -> List[str]:
        ret = []
        for div in self.soup.find("thead").find_all("div"):
            ret.append(Crawler._get_string(div))
        return ret

    @classmethod
    def _normalize(cls, text: str) -> str:
        return normalize("NFKC", text)

    def get_records(self) -> List[List[str]]:
        ret = []
        for tr in self.soup.find("tbody").find_all("tr"):
            r = []
            for div in tr.find_all("div"):
                div_str = Crawler._get_string(div)
                if div_str:
                    div_str = Crawler._normalize(div_str)
                    r.append(div_str)
            if len(r) != self.num_of_cols:
                self.logger.warning(f"Wrong record: {len(r)} != {self.num_of_cols}")
                continue
            ret.append(r)
        return ret

    def crawl_next(self):
        next_page_button = self.soup.find("img", alt="次のページ")
        if not next_page_button:
            self.page = None
            return
        next_page_a = next_page_button.parent
        self.page = next_page_a["href"]

        self.logger.info(f"GET {self.root}{self.page}")
        url = requests.get(self.root + self.page)
        self.soup = BeautifulSoup(url.content, "html.parser")


def set_logger(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="path to the generated csv")
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=10,
        help="crawl interval [secs] (Default: 10) ",
    )
    args = parser.parse_args()

    root = "https://renrakuda.mlit.go.jp/renrakuda/"
    init_page = "opn.search.html?selCarTp=1&lstCarNo=&txtFrDat=0000-00-00&txtToDat=9999-99-31&txtNamNm=&txtMdlNm=&txtEgmNm=&chkDevCd=&contentSummary=&contentSummaryCondition=STRINC&asv=false"  # noqa: E501
    csv_path = args.csv_path
    set_logger(__name__)
    logger = logging.getLogger(__name__)
    with open(csv_path, "w", encoding="UTF-8") as f:
        writer = csv.writer(f)
        crawler = Crawler(root, init_page)

        header = crawler.get_header()
        if len(header) != crawler.num_of_cols:
            logger.error(
                f"Length of table header is different from expected: {len(header)} != 13"
            )
            return
        writer.writerow(header)
        while crawler.page:
            writer.writerows(crawler.get_records())
            time.sleep(args.interval)
            crawler.crawl_next()


if __name__ == "__main__":
    main()
