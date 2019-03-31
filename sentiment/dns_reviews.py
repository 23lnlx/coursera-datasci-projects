import requests
import bs4
from multiprocessing import Pool
import codecs
from functools import reduce
import pickle

DNS_WEBPAGE = 'https://www.dns-shop.ru'

def get_all_products(url):
    print('>>> Parsing page '+url)
    text = requests.get(url).text
    parser = bs4.BeautifulSoup(text, 'lxml')
    
    product_links = parser.findAll('div', attrs='title')
    return [DNS_WEBPAGE+product.a['href'] for product in product_links]

PAGES_LIST = [DNS_WEBPAGE + '/catalog/17a8a01d16404e77/smartfony/?p={}'.format(num) for num in range(1,51)]

def get_opinions(product_url):
    print('\t>>> Parsing product '+product_url)
    text = requests.get(product_url+'opinion/').text
    parser = bs4.BeautifulSoup(text, 'lxml')
    
    opinions = parser.findAll('div', attrs='opinion-item')
    
    opnions_w_raiting = []
    for opinion_parser in opinions:
#         print(opinion_parser.prettify())
        rating = opinion_parser.find('div', attrs='product-item-rating rating')['data-rating']
        descriptions = opinion_parser.findAll('span', attrs='description-text')
        opinion_text = ' '.join([descr.text for descr in descriptions])
        opnions_w_raiting.append((opinion_text, int(rating)))
        
    return opnions_w_raiting


if __name__ == '__main__':
    p = Pool(100)

    map_products = p.map(get_all_products, PAGES_LIST)
    reduce_products = reduce(lambda x,y: x + y, map_products)
    
    map_reviews = p.map(get_opinions, reduce_products)
    reduce_reviews = reduce(lambda x,y: x + y, map_reviews)
    
    with open('all_dns.txt', 'wb') as output_file:
        pickle.dump(reduce_reviews, output_file)