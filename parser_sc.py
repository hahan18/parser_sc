from os.path import isdir

import bs4
import requests

from dotenv import load_dotenv
import os

from sqlalchemy import Column, String, DECIMAL, Text, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database, URLType


class Parser:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1'
    }

    def parse(self):
        session = requests.Session()
        parsed = [field for field in self.__parse_info(session=session)]
        session.close()
        return parsed

    def __parse_info(self, session):
        url_response = self.__make_urls(session=session)
        for url_page in url_response:
            response = session.get(url=url_page, headers=self.headers)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            data = soup.find('div', class_='card mt-4 my-4')

            title = data.find('h3', class_='card-title').text
            price = float(data.find('h4').text.replace('$', ''))
            descr = data.find('p', class_='card-text').text
            img = f'https://scrapingclub.com' + data.find('img', class_='card-img-top img-fluid').get('src')
            yield title, price, descr, img

    def __make_urls(self, session):
        for page in range(1, 8):
            url = f'https://scrapingclub.com/exercise/list_basic/?page={page}'
            response = session.get(url=url, headers=self.headers)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            data = soup.find_all('div', class_='col-lg-4 col-md-6 mb-4')

            for field in data:
                url_response = f'https://scrapingclub.com' + field.find('a').get('href')
                yield url_response


class ToDB:

    def __init__(self):
        load_dotenv()
        DB_CONFIG_DICT = {
            'user': os.environ.get('USER'),
            'password': os.environ.get('PASSWORD'),
            'host': os.environ.get('HOST'),
            'port': os.environ.get('PORT'),
        }
        database = 'ParserDB'
        DB_CONN_FORM = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        self.DB_CONN = (DB_CONN_FORM.format(database=database,
                                            **DB_CONFIG_DICT))

    def master(self, parsed, headers):
        engine = create_engine(self.DB_CONN)

        if self.__db_exists(engine=engine):
            with engine.connect() as conn:
                if self.__table_exists(engine=engine, conn=conn):
                    self.__save(conn=conn, _parsed=parsed)
                    self.__save_img(_parsed=parsed, headers=headers)

    @staticmethod
    def __db_exists(engine):
        if not database_exists(engine.url):
            create_database(engine.url)
            print('CREATE DB')
        return True

    @staticmethod
    def __table_exists(engine, conn):
        if not engine.dialect.has_table(connection=conn, table_name='ParsedWeb'):
            Base = declarative_base()

            class ParsedWeb(Base):
                __tablename__ = 'ParsedWeb'

                id = Column(Integer, primary_key=True)
                title = Column(String(250))
                price = Column(DECIMAL(precision=4, asdecimal=True, decimal_return_scale=2))
                descr = Column(Text)
                img_url = Column(URLType)

            Base.metadata.create_all(engine)
            print('CREATE TABLE')
        return True

    @staticmethod
    def __save(conn, _parsed):
        if not conn.execute('SELECT id FROM "ParsedWeb" WHERE id = 1').rowcount >= 1:
            for field in _parsed:
                conn.execute("""INSERT INTO "ParsedWeb" (title, price, descr, img_url) 
                                VALUES (%s, %s, %s, %s)""", field[0], field[1], field[2], field[3])

    @staticmethod
    def __save_img(_parsed, headers):
        if not isdir('./images'):
            print('CREATE DIR')
            os.mkdir('./images')
            with requests.Session() as session:
                for field in _parsed:
                    file_name = f'{field[0]}.jpg'
                    url = field[3]
                    response = session.get(url=url, headers=headers)
                    with open(f'./images/{file_name}', 'wb') as file:
                        file.write(response.content)


if __name__ == '__main__':
    parser = Parser()
    db = ToDB()

    parsed_response = parser.parse()
    db.master(parsed=parsed_response, headers=parser.headers)
