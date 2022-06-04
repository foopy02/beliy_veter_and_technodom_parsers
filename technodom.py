import json
from math import prod
import time
import requests
import os
from bs4 import BeautifulSoup
import random
ROOT = f'{os.path.dirname(__file__)}/'
ROOT_OF_DATABASE = f'{os.path.dirname(__file__)}/database.json'


database = json.load(open(ROOT_OF_DATABASE,encoding='utf8'))


class Product():
    def __init__(self,id, title, price, image, category, characteristics):
        self.id = id
        self.title = title
        self.price = price
        self.image = image
        self.category = category
        self.count = random.randint(1, 50)
        self.characteristics = characteristics

class Parser():
    BASE_URL = "https://www.technodom.kz"


    katalogi = [
        # ('/astana/catalog/noutbuki-i-komp-jutery/noutbuki-i-aksessuary/noutbuki', 'Ноутбук'),
    # ('/astana/catalog/noutbuki-i-komp-jutery/komp-jutery-i-monitory/stacionarnye-pk', 'Компьютеры'),
    # ('/astana/catalog/noutbuki-i-komp-jutery/komp-jutery-i-monitory/monitory', 'Мониторы'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komp-juternye-aksessuary/myshi', 'Мыши'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komp-juternye-aksessuary/klaviatury', 'Клавиатуры'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komplektujuschie/zhestkie-diski', 'Жесткие диски'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komplektujuschie/processory', 'Процессоры'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komplektujuschie/videokarty', 'Видеокарты'),
    ('/astana/catalog/noutbuki-i-komp-jutery/komplektujuschie/ssd-diski', 'SSD диски')
        ]
    
    def get_content_of(self, url):
        print(f"Getting content of {url}")
        return requests.get(f'{url}').content


    def get_link(self, soup_of_products):
        result = list()

        for soup in soup_of_products:
            try:
                result.append(soup.find('a', {'class': 'category-page-list__item-link'}).get('href'))
            except:
                print(soup)
        return result

    def get_products(self, soup_of_products):
        return soup_of_products.find('ul', {'class':'category-page-list__list'}).find_all('li', {'class': 'category-page-list__item'})

    def download_image(self, link_to_img,id):
        # response = requests.get('https://www.technodom.kz/_next/image?url=https%3A%2F%2Fapi.technodom.kz%2Ff3%2Fapi%2Fv1%2Fimages%2F800%2F800%2F226869_1z.jpg')
        # print(link_to_img)
        # file = open(f"{ROOT}/images/{id}.jpg", "wb")
        # file.write(response.content)
        # file.close()
        # print("Successfully downloaded")
        with open(f"{ROOT}/images/{id}.jpg", 'wb') as handle:
            response = requests.get(link_to_img, stream=True, allow_redirects=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


    def get_title(self, soup_of_product):
        return soup_of_product.find('h1',{'class': 'Typography Typography__Title Typography__Title_Small'}).text

    def get_price(self, soup_of_product):
        return self.extract_digits(soup_of_product.find('div',{'class': 'product-actions__price product-prices'}).find('p').text)
    
    def get_description(self, soup_of_product):
        return soup_of_product.find('div', {'class': 'poDescription col-lg-12'}).text.replace('\n', '<br>')

    def get_image_link(self, soup_of_product):
        return self.BASE_URL + soup_of_product.find("link",{"as":"image"}).get('imagesrcset').split()[0]
    
    
    def get_id(self, soup_of_product):
        return soup_of_product.find('p',{"class":'Typography product-info__sku Typography__Caption'}).text


    def extract_digits(self, string):
        num = ""
        for c in string:
            if c.isdigit():
                num = num + c
        return int(num)

    def get_characteristic(self, soup_of_product):
        rows = soup_of_product.find_all('div', {'class': 'product-description__item'})
        characteristics = dict()
        for row in rows:
            inner_row = row.find_all('p')
            characteristics[inner_row[0].text] = inner_row[1].text.strip()
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
                characteristics = self.get_characteristic(soup_of_product)
                id = self.get_id(soup_of_product)
                product = Product(id, title, price, id, self.katalogi[counter][1], characteristics)
                database.append(product.__dict__)
                json.dump(database,open(ROOT_OF_DATABASE,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
                time.sleep(0.1)
            counter = counter + 1
            # break


parser = Parser()
parser.start()