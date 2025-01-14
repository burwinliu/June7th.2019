"""
    Will take countries data and serve into postgresql
    Will take colours spectrum data and serve into postgresql
    Will take files from scraping and link

    HERE IS MAIN FILE, try not to touch other files
"""

import re

import pycountry

from database_access import Database, NewsDatabase, OverviewDatabase
from database_access.config import test, DatabaseError, init_db, execute_command


def store_countries(db: Database) -> None:
    """
    Store country info into database

    :return:None
    """
    db.add_many_inputs(tuple(("NUMERIC", "iso3166_code", "country_name")), tuple((get_country_codes_and_names())))


def store_articles(urls: list, headlines: list, iso_codes: list):
    """
    store amount of articles, given in tuples to databases

    :param urls: tuple
    :param headlines: tuple
    :param iso_codes: tuple
    :return: None
    """
    # Variable setup
    to_exe = list()
    ndb = NewsDatabase()
    odb = OverviewDatabase()
    # Double checking your inputs are good, else we crash
    if not (len(urls) == len(headlines) == len(iso_codes)):
        raise Exception(f"Your urls, headlines and iso_codes do not have same lengths")
    for i in range(len(urls)):
        # Double checking your inputs are good, else we crash
        if type(urls[i]) != str or type(headlines[i]) != str or type(iso_codes[i]) != int:
            raise Exception(f"Input {urls[i]}, {headlines[i]} and {iso_codes[i]} are improper at position {i}")

        to_exe.append(tuple((urls[i], headlines[i], iso_codes[i])))

    param = ndb.add_many_inputs(tuple(("url", "headline", "ISO_Code")), tuple(to_exe))
    odb.add_many_inputs(tuple(("ISO_Code", "News_list")), tuple(((k, v) for k, v in param.items())))


def _init_sys_info() -> Database:
    """
    init sys info db
    :return: Database
    """
    if test() == 0:
        raise DatabaseError
    param = init_db("system", "sys_info",
                          [
                              ("schema", "TEXT"),
                              ("name", "TEXT", "UNIQUE"),
                              ("columns", "TEXT"),
                              ("types", "TEXT")
                          ],
                          sys_table=True
                          )
    res = Database(*param)
    return res


def _init_countries() -> Database:
    """
    init the countries database
    Will store countries numeric, iso and country name

    :return: database.Database object
    """
    if test() == 0:
        raise DatabaseError
    param = init_db("public", "countries",
                          [
                              ("NUMERIC", "SMALLINT", "PRIMARY KEY"),
                              ("iso3166_code", "VARCHAR(2)", "NOT NULL"),
                              ("country_name", "VARCHAR(75)", "NOT NULL")
                          ],
                          sys_table=False
                          )
    res = Database(*param)
    return res


def init_news() -> NewsDatabase:
    """
    init the news database
    Will store news article info

    :return: database.Database object
    """
    if test() == 0:
        raise DatabaseError
    init_db("public", "news",
                  [
                      ("news_number", "SERIAL", "PRIMARY KEY"),
                      ("url", "TEXT", "NOT NULL"),
                      ("headline", "TEXT", "NOT NULL"),
                      ("ISO_Code", "SMALLINT",),
                  ]
                  )
    res = NewsDatabase()
    return res


def init_news_overview() -> OverviewDatabase:
    """
    init the news overview
    Will store news overview -- number of hits, corresponding colour and other info

    :return: database.Database object
    """
    if test() == 0:
        raise DatabaseError
    res = OverviewDatabase()
    init_db("public", "news_overview",
                  [
                      ("ISO_Code", "SMALLINT", "PRIMARY KEY"),
                      ("News_list", "BIGINT[]"),
                  ]
                  )
    return res


def reset_news():
    execute_command("DELETE FROM public.news")
    execute_command("ALTER SEQUENCE public.news_news_number_seq RESTART WITH 1")


def reset_overview():
    execute_command("DELETE FROM public.news_overview")


def get_country_codes_and_names() -> list:
    """
    for retrieving all country codes and stuff

    :return: list of tuples that contain all country info
    """
    list_of_country = pycountry.countries
    res = list()
    for country in list_of_country:
        if "'" in country.name:
            to_input = re.sub(r"'", "''", country.name)
            res.append(tuple((country.numeric, country.alpha_2, to_input)))
            continue
        res.append(tuple((country.numeric, country.alpha_2, country.name)))
    return res


if __name__ == "__main__":
    # For reset of database

    '''
    reset_news()
    reset_overview()
    '''

    # For setup of databases

    '''
    _init_sys_info()
    countries = _init_countries()
    store_countries(countries)
    init_news()
    init_news_overview()
    '''


