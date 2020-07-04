import json

if __name__ == '__main__':

    with open('item.json') as f:
        item = json.load(f)

    print(json.dumps(item, indent=4, sort_keys=True))
    print(item['data']['1001'])
    ids = item['data']
    print(ids.keys())
    item_list = open('Item List.txt', 'w')
    for key in item['data'].keys():
        item_list.write(key + ': ' + item['data'][key]['name']+'\n')