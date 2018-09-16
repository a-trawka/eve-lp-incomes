from csv import DictWriter

from lxml import html


"""In order to work, this script needs to use local html"""


def concord_items():
    items = []
    for i in (1, 2):
        with open(f'resources/CONCORD_forge_sell_{i}.html', 'r') as items_html:
            tree = html.fromstring(items_html.read())
            tbody = tree.xpath('//*[@id="lp"]/tbody')[0]
            for row in tbody.xpath('tr'):
                tds = row.xpath('td')
                item = {
                    'item': tds[3].xpath('a')[0].text.strip(),
                    'lp': tds[1].text.strip().replace(',', ''),
                    'isk': tds[2].text.strip().replace(',', '')
                }
                items.append(item)
    return items


if __name__ == '__main__':
    with open('resources/concord_items.csv', 'w') as csvfile:
        items = concord_items()
        itemwriter = DictWriter(csvfile, items[0].keys())
        itemwriter.writeheader()
        for item in items:
            itemwriter.writerow(item)
