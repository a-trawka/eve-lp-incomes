from csv import DictReader
from operator import itemgetter

from lxml import html
from requests import get, post

EVEPRAISAL_URL = 'http://evepraisal.com'


def query_evepraisal(item_dicts, market):
    """
    :param item_dicts: list of item dicts
    :param market: ex. jita
    :return: item regional appraisal response
    """
    items_text = '\n'.join(i['item'] for i in item_dicts)
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


def evepraisal_prices(prices_response_content, item_dicts):
    """
    :param prices_response_content: response content in bytes (ex. Response.content)
    :param item_dicts: list of item dicts
    :return: tuple of prices
    """
    all_items_prices = []
    tree = html.fromstring(prices_response_content)
    tbody = tree.xpath('/html/body/div[1]/div[3]/div[2]/table/tbody')[0]  # table tbody containing prices
    for row in tbody.xpath('tr'):
        item_name = row.xpath('td[2]')[0].xpath("a[@class='text-light']/strong")[0].text.strip()
        matching_item = next(  # find the matching item by name and then isk required to purchase the item
            filter(
                lambda item: item['item'] == item_name,
                item_dicts
            )
        )
        isk_cost = int(matching_item['isk'])
        lp_cost = int(matching_item['lp'])
        raw_prices_text = row.xpath('td[4]')[0].text_content().strip()
        raw_prices = raw_prices_text.replace(' ', '').split('\n')
        prices = map(  # both buy and sell prices
            lambda p: int(p.split('.')[0].replace(',', '')),
            raw_prices
        )
        all_items_prices.append([item_name, next(prices) - isk_cost, lp_cost])  # [item, price-isk cost=income, lp cost]
    return all_items_prices


def most_protifable_items(prices, n=5):
    return sorted(prices, key=itemgetter(1), reverse=True)[:n]


def items():
    with open('resources/concord_items.csv') as csvfile:
        return list(DictReader(csvfile))


def prettify_results(results):
    def commafy(n):
        r = []
        for i, c in enumerate(reversed(str(n))):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)

    return ((commafy(r[1]), commafy(r[2]), r[0]) for r in results)


if __name__ == '__main__':
    # TODO: add current amount of LPs
    item_dicts = items()  # list of item dicts

    post_response = query_evepraisal(item_dicts, 'jita')
    appraisal_id = post_response.headers['X-Appraisal-Id']
    appraisal_response = appraisal(appraisal_id)

    prices = evepraisal_prices(appraisal_response.content, item_dicts)
    results = most_protifable_items(prices)
    for result in prettify_results(results):
        print(result)
