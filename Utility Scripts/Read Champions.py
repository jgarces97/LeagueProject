import json

if __name__ == '__main__':

    with open('champion.json', 'rb') as f:
        champions = json.load(f)

    champ_dict = {}
    for champ in champions['data'].keys():
        champ_dict[champions['data'][champ]['key']] = champions['data'][champ]['id']

    with open('../champ_id.json', 'w') as fp:
        json.dump(champ_dict, fp)