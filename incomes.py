from csv import DictReader
from operator import itemgetter

from requests import get, post

EVEPRAISAL_URL = 'http://evepraisal.com'


def query_evepraisal(store_data, market='jita'):
    """
    :param store_data: LP store data - list of dicts
    :param market: ex. jita
    :return: response containing important appraisal id in headers
    """
    items_text = '\n'.join(i['item'] for i in store_data)
    f = {
        'persist': (None, 'yes'),
        'price_percentage': (None, 100),
        'uploadappraisal': '',
        'raw_textarea': (None, items_text),
        'market': (None, market),
    }
    return post(url=f'{EVEPRAISAL_URL}/appraisal', files=f)


def appraisal_data(appraisal_id):
    return get(f'{EVEPRAISAL_URL}/a/{appraisal_id}.json')


def iter_formatted_items(data, store_data):
    """
    :param data: appraisal data dict
    :param store_data: LP store data - list of dicts
    :return: generator of item dicts containing market data
    """
    for item in data['items']:
        name = item['name']
        matching_store_item = next(filter(
            lambda store_item: store_item['item'] == name,
            store_data
        ))
        buy_scope = item['prices']['buy']
        sell_scope = item['prices']['sell']
        yield {
            'item': matching_store_item,
            'buy_price': buy_scope['min'],
            'buy_orders': buy_scope['order_count'],
            'sell_price': sell_scope['min'],
            'sell_orders': sell_scope['order_count']
        }


def lp_store_items():
    with open('resources/concord_items.csv') as csvfile:
        return list(DictReader(csvfile))


# def prettify_results(results):
#     def commafy(n):
#         r = []
#         for i, c in enumerate(reversed(str(n))):
#             if i and (not (i % 3)):
#                 r.insert(0, ',')
#             r.insert(0, c)
#         return ''.join(r)
#
#     return ((commafy(r[1]), commafy(r[2]), r[0]) for r in results)


if __name__ == '__main__':
    # TODO: add current amount of LPs
    # TODO: query more than 1 trade hubs
    lp_store_data = lp_store_items()

    post_response = query_evepraisal(lp_store_data)
    appraisal_id = post_response.headers['X-Appraisal-Id']
    appraisal_response = appraisal_data(appraisal_id)
    appraisal_data = appraisal_response.json()

    items = iter_formatted_items(appraisal_data, lp_store_data)
    filtered_zero_orders = filter(
        lambda item: item['buy_orders'] != 0 and item['sell_orders'] != 0,
        items
    )
    for i in sorted(filtered_zero_orders,
                    key=itemgetter('sell_price'),
                    reverse=True)[:10]:
        print(i)
