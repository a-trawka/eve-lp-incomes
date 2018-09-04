from operator import itemgetter

from lxml import html
from requests import get, post

EVEPRAISAL_URL = 'http://evepraisal.com'
FUZZWORK_URL = 'httl://fuzzwork.co.uk/'


def concord_items():
    items = []
    for i in (1, 2):
        with open(f'resources/CONCORD_forge_sell_{i}.html', 'r') as items_html:
            tree = html.fromstring(items_html.read())
            tbody = tree.xpath('//*[@id="lp"]/tbody')[0]
            for row in tbody.xpath('tr'):
                item_column = row.xpath('td')[3]
                item = item_column.xpath('a')[0].text
                items.append(item)
    return items


def query_evepraisal(items_list, market):
    """
    :param items_list: list of item names (ex. Zainou 'Gypsy' Sensor Linking SL-902)
    :param market: ex. jita
    :return: item regional appraisal response
    """
    items_text = '\n'.join(items_list)
    f = {
        'persist': (None, 'yes'),
        'price_percentage': (None, 100),
        'uploadappraisal': '',
        'raw_textarea': (None, items_text),
        'market': (None, market),
    }
    return post(url=f'{EVEPRAISAL_URL}/appraisal', files=f)


def appraisal(appraisal_id):
    return get(f'{EVEPRAISAL_URL}/a/{appraisal_id}')


def extract_prices(prices_response_content):
    """
    :param prices_response_content: response content in bytes (ex. Response.content)
    :return: tuple of prices
    """
    all_items_prices = []
    tree = html.fromstring(prices_response_content)
    tbody = tree.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody')[0]
    for row in tbody.xpath('tr'):
        # TODO: take ISK and LP cost into consideration too
        item_name = row.xpath('td[2]')[0].xpath("a[@class='text-light']/strong")[0].text.strip()
        raw_prices_text = row.xpath('td[4]')[0].text_content().strip()
        raw_prices = raw_prices_text.replace(' ', '').split('\n')
        prices = map(
            lambda p: int(p.split('.')[0].replace(',', '')),
            raw_prices
        )
        all_items_prices.append([item_name, next(prices)])  # only buy price for now
    return all_items_prices


def most_protifable_items(prices, n=5):
    # TODO: take ISK and LP cost into consideration too
    return sorted(prices, key=itemgetter(1), reverse=True)[:n]


if __name__ == '__main__':
    items = concord_items()
    post_response = query_evepraisal(items, 'jita')
    appraisal_id = post_response.headers['X-Appraisal-Id']
    appraisal_response = appraisal(appraisal_id)
    prices = extract_prices(appraisal_response.content)
    print(most_protifable_items(prices))
