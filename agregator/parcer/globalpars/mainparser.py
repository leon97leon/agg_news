import re
from datetime import datetime as dt
from time import sleep
from langdetect import detect
import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
from tqdm import tqdm
import pycld2 as cld
from urllib.parse import urlparse

from ._config import Ya
from ._history import history
from ._textparser import TextParser
from ._utils import Utils


class MainParser:
    __session = None
    __keys = None
    __df = pd.DataFrame()

    @classmethod
    def main(
            cls,
            first_date: dt,
            second_date: dt,
            keys_df: pd.DataFrame,
    ):
        cls.__session = Utils.create_session()
        cls.__keys = Utils.read_keys(keys_df)
        dates_list = Utils.get_list_of_dates(first_date, second_date)

        MainParser.get_articles(dates_list)

        cls.__df.drop_duplicates(['Ссылка'], inplace=True, ignore_index=True)
        history_df = history(cls.__df)
        sleep(0.1)  # для корректного вывода tqdm в консоли PyCharm

        cls.__df.drop(MainParser.__titles_check(), inplace=True)
        cls.__df = TextParser.parser(cls.__df)
        if not cls.__df.empty:
            df_ending, to_drop = MainParser.__replace_rows()
            cls.__df.drop(to_drop, inplace=True)
            MainParser.__drop_rows()
            #cls.__df = pd.concat([cls.__df, df_ending], ignore_index=True)

            return cls.__df, df_ending
        else:
            return cls.__df, pd.DataFrame()

    @classmethod
    def get_articles(cls, dates_list):
        keys_for_table, links, titles = [], [], []
        search_links = []

        for date in dates_list:
            qs = Ya.query_start
            qe = f'+date%3A{date.strftime("%Y%m%d")}..{date.strftime("%Y%m%d")}&flat=1&sortby=date&filter_date={int(date.timestamp() * 1000)}%2C{int(date.timestamp() * 1000)}'
            art_cls = Ya.article_class
            for key in tqdm(
                    cls.__keys,
                    desc=f'Выгрузка ссылок из {Ya.name} за {date.date()}'
            ):
                query = qs + key.replace(' ','+') + qe
                k, l, t = MainParser.__links_and_titles(key, query, art_cls)
                keys_for_table += k
                links += l
                titles += t
                search_links += [query for _ in range(len(k))]

        cls.__session.close()

        cls.__df = pd.DataFrame({
            'Ключевое слово': keys_for_table,
            'Заголовок': titles,
            'Ссылка': links,
            'Поисковой url': search_links
        })

    @classmethod
    def __links_and_titles(
            cls, key: str, q: str, art_cls: str
    ):
        """Return lists of keys, links and titles for search query.

        :param key: keyword for search
        :type key: str
        :param q: search link
        :type q: str
        :param art_cls: html class with title and link
        :type art_cls: str

        :rtype: tuple[list[str], list[str], list[str]]
        :return: 3 lists with keys, links and titles for search query
        """
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        try:
            response = cls.__session.get(q, timeout=10, headers=headers)

        except IOError as http_err:
            print(f'Запрос "{key}" не выполнен! '
                  'Проблемы с интернет подключением:\n'
                  f'{http_err}\nПовторная попытка подключения...')
            # Utils.check_connection(cls.__session)
            return MainParser.__links_and_titles(key, q, art_cls)

        # TODO: сделать ограничение по количеству попыток повтора
        except Exception as err:
            print(f'Запрос "{key}" не выполнен! Ошибка:\n'
                  f'{err}\nПовторная попытка подключения...')
            # Utils.check_connection(cls.__session)
            return MainParser.__links_and_titles(key, q, art_cls)

        else:
            keys_for_table, links, titles = [], [], []
            soup = BeautifulSoup(response.text, 'lxml')
            for el in soup.findAll({'a': True}, class_=art_cls):
                link, title = Ya.get_article(el)
                keys_for_table.append(key)
                links.append(link)
                titles.append(title)
        return keys_for_table, links, titles

    @classmethod
    def __titles_check(cls):
        """Return set of rows, provided that their titles
         is similar to at least one of other titles.

        :rtype: set[int]
        :return: set of rows to drop them from df
        """
        to_drop = set()
        cls.__df.reset_index(inplace=True, drop=True)
        normal_titles = [Utils.normal_str(t) for t
                         in cls.__df['Заголовок'].values]
        for ind_one, title_one in enumerate(normal_titles):
            for ind_two, title_two in enumerate(normal_titles):
                if ind_two not in to_drop and ind_two != ind_one:
                    if fuzz.token_sort_ratio(title_one, title_two) >= 60:
                        to_drop.add(ind_one)
                        break

        return to_drop

    @classmethod
    def __replace_rows(cls):
        """Return pd.Dataframe with articles to add it to the end of
        result df and set of ints to drop them from result df.

        :rtype: tuple[pd.Dataframe, set[int]]
        :return: pd.Dataframe with articles and set of ints-indexes
        """
        df_ending = pd.DataFrame()

        to_end = set()
        for row, text in zip(cls.__df.index, cls.__df['Текст'].values):
            if (text == 'В тексте отсутствуют русские символы!' or
                    re.search(r'Не удалось выгрузить данные!!!', text)):
                to_end.add(row)
        df_ending = pd.concat([df_ending, cls.__df.loc[list(to_end)]],
                              ignore_index=True)

        return df_ending, to_end

    @classmethod
    def __drop_rows(cls):
        """Drop articles from result df:
        with "schroders" in url;
        without keyword in text;
        with non-russian text.
        """
        to_drop = set()
        for row, link in zip(cls.__df.index, cls.__df['Ссылка'].values):
            if re.search('schroders', link) or re.search('kz',urlparse(link).netloc):
                to_drop.add(row)
        cls.__df.drop(to_drop, inplace=True)

        to_drop = set()
        for row, text, title, key in zip(
                cls.__df.index,
                cls.__df['Текст'].values,
                cls.__df['Заголовок'].values,
                cls.__df['Ключевое слово'].values
        ):
            if not len(key.split(' ')) > 1:
                if pd.notna(text):
                    key_clear = re.sub(r'"', '', key)
                    if (not re.search(rf'\b{key_clear}\b', text.lower()) and
                            not re.search(rf'\b{key_clear}\b', title.lower())):
                        to_drop.add(row)
                else:
                    to_drop.add(row)
        cls.__df.drop(to_drop, inplace=True)

        to_drop = set()
        for row, text in zip(cls.__df.index, cls.__df['Текст'].values):
            try:
                if cld.detect(text)[2][0][0] != 'RUSSIAN':
                    to_drop.add(row)
            except cld.error:
                to_drop.add(row)
        cls.__df.drop(to_drop, inplace=True)
