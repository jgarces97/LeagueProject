import json

if __name__ == '__main__':

    with open('runesReforged.json') as f:
        runes = json.load(f)

    # runes = json.dumps(item, indent=4, sort_keys=True)
    with open('../rune_ids.json', 'w') as json_file:
        doot = {'8008': 80009}
        json.dump(doot, json_file)
    rune_list = open('Rune List.txt', 'w')
    for keystone in runes:
        rune_list.write(str(keystone['id']) + ': ' + keystone['key'] + '\n--------\n')
        for slot in keystone['slots']:
            for rune in slot['runes']:
                rune_list.write(str(rune['id']) + ': ' + rune['key'] + '\n')
        rune_list.write('\n\n')