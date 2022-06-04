import json
from math import prod
import time
import requests
import os
from bs4 import BeautifulSoup
import random
ROOT = f'{os.path.dirname(__file__)}/'
ROOT_OF_DATABASE = f'{os.path.dirname(__file__)}/database_2.json'


database = json.load(open(ROOT_OF_DATABASE,encoding='utf8'))


class Product():
    def __init__(self,id, title, price, image, category, characteristics,description):
        self.id = id
        self.title = title
        self.price = price
        self.image = image
        self.category = category
        self.count = random.randint(1, 50)
        self.description = description
        self.characteristics = characteristics

class Parser():
    BASE_URL = "https://www.shop.kz"


    katalogi = [
        # ('/noutbuki/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Ноутбук'),
        # ('/ultrabuki/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Ультрабуки'),
    # ('/nastolnye-kompyutery/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Компьютеры'),
    # ('/monitory/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Мониторы'),
    # ('/myshi/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Мыши'),
    # ('/klaviatury/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Клавиатуры'),
    # ('/zhestkie-diski/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Жесткие диски'),
    # ('/protsessory/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Процессоры'),
    # ('/videokarty/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'Видеокарты'),
    ('/ssd-diski/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/', 'SSD диски')
        ]
    
    def get_content_of(self, url):
        headers ={
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}
        print(f"Getting content of {url}")
        return requests.get(f'{url}',headers=headers).content


    def get_link(self, soup_of_products):
        result = list()

        for soup in soup_of_products:
            try:
                result.append(soup.find('div', {'class': 'bx_catalog_item_title'}).find('a').get('href'))
            except:
                print(soup)
        return result

    def get_products(self, soup_of_products):
        return soup_of_products.find('div', {'class':'bx_catalog_list_home col1 bx_blue'}).find_all('div', {'class': 'bx_catalog_item double'})

    def download_image(self, link_to_img,id):
        response = requests.get(link_to_img)
        print(link_to_img)
        file = open(f"{ROOT}/images/{id}.jpg", "wb")
        file.write(response.content)
        file.close()
        print("Successfully downloaded")
        # with open(f"{ROOT}/images/{id}.jpg", 'wb') as handle:
        #     response = requests.get(link_to_img, stream=True, allow_redirects=True)

        #     if not response.ok:
        #         print(response)

        #     for block in response.iter_content(1024):
        #         if not block:
        #             break

        #         handle.write(block)


    def get_title(self, soup_of_product):
        return soup_of_product.find('h1',{'class': 'bx-title dbg_title'}).text

    def get_price(self, soup_of_product):
        return self.extract_digits(soup_of_product.find('div',{'class': 'item_current_price'}).text)
    
    def get_description(self, soup_of_product):
        return soup_of_product.find('div', {'class': 'bx_item_description'}).text.replace('Описание','')

    def get_image_link(self, soup_of_product):
        return soup_of_product.find("meta",{"property":"og:image"}).get('content')
    
    
    def get_id(self, soup_of_product):
        return soup_of_product.find('p',{"class":'Typography product-info__sku Typography__Caption'}).text


    def extract_digits(self, string):
        num = ""
        for c in string:
            if c.isdigit():
                num = num + c
        return int(num)

    def get_characteristic(self, soup_of_product):
        rows = soup_of_product.find('dl', {'class': 'bx_detail_chars'}).find_all('div',{'class':'bx_detail_chars_i'})
        characteristics = dict()
        # print(rows)
        for row in rows:
            characteristics[row.find('dt',{'class':'bx_detail_chars_i_title'}).text.strip()] = row.find('dd',{'class':'bx_detail_chars_i_field'}).text.strip()
        return characteristics

    def start(self):
        counter = 0
        for catalog in self.katalogi[0]:
            content = self.get_content_of(self.BASE_URL + catalog)
            self.soup = BeautifulSoup(content, 'html.parser')
            links = self.get_link(self.get_products(self.soup))
            for link in links[:10]:
                content = self.get_content_of(f'{self.BASE_URL}/{link}')
                soup_of_product = BeautifulSoup(content, 'html.parser')

                title = self.get_title(soup_of_product)
                price = self.get_price(soup_of_product)
                description = self.get_description(soup_of_product)
                characteristics = self.get_characteristic(soup_of_product)
                print(characteristics['UID товара'])
                try:
                    id = characteristics['UID товара'].replace()
                except:
                    id = random.randint(0,1000000)
                # # print(self.get_image_link(soup_of_product))
                name_of_image = self.download_image(self.get_image_link(soup_of_product),id)
                product = Product(id, title, price, f'images/{id}.jpg', self.katalogi[counter][1], characteristics,description)
                database.append(product.__dict__)
                json.dump(database,open(ROOT_OF_DATABASE,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
                time.sleep(0.1)
            counter = counter + 1
            # break


parser = Parser()
parser.start()