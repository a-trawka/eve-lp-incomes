from bs4 import BeautifulSoup
from lxml import html
from requests import get, post

EVEPRAISAL_URL = 'http://evepraisal.com'
FUZZWORK_URL = 'httl://fuzzwork.co.uk/'


def top_store_items():
    pass


def request_evepraisal_data(item_name, market='jita'):
    f = {
        'persist': (None, 'yes'),
        'price_percentage': (None, 100),
        'uploadappraisal': '',
        'raw_textarea': (None, item_name),
        'market': (None, market),
    }
    return post(url=f'{EVEPRAISAL_URL}/appraisal', files=f)


def get_prices(appraisal_id):
    return get(f'{EVEPRAISAL_URL}/a/{appraisal_id}')


def extract_prices(prices_response_content):
    tree = html.fromstring(prices_response_content)
    raw_prices_text = tree.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody/tr/td[4]')[0].text_content().strip()
    raw_prices = raw_prices_text.replace(' ', '').split('\n')
    prices = map(lambda p: int(p.split('.')[0].replace(',', '')), raw_prices)
    return tuple(prices)


if __name__ == '__main__':
    response = request_evepraisal_data("Zainou 'Snapshot' Torpedoes TD-606", 'jita')
    appraisal = response.headers['X-Appraisal-Id']
    prices_response = get_prices(appraisal)
    print(extract_prices(prices_response.content))
