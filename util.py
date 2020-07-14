import json
from random import sample, choice
from os import listdir, chdir, path, remove, getcwd

API_KEY = 'RGAPI-ede632c0-c81f-4621-bd05-05468bfaaa23'


def random_runes(champ):
    # The list of runes to run
    rune_list = []

    with open('rune_ids.json') as f:
        runes = json.load(f)

    with open('champ_id.json') as f:
        champions = json.load(f)

    # Picks to random trees
    keystones = sample(runes['keystones'].keys(), 2)

    # Gets the main key stone and all secondaries for first tree
    for key in runes['keystones'][str(keystones[0])].keys():
        rune_list.extend(sample(runes['keystones'][str(keystones[0])][key], 1))

    # Pick the 2 lines for secondary tree
    sec_runes = list(runes['keystones'][str(keystones[1])].keys())
    sec_runes.remove('main')
    sec_runes = sample(sec_runes, 2)

    # Adds 2 random
    for key in sec_runes:
        rune_list.append(choice(runes['keystones'][str(keystones[1])][key]))

    # Picks random little runes
    for key in runes['little_runes'].keys():
        rune_list.extend(sample(runes['little_runes'][key], 1))

    rune_page = {"autoModifiedSelections": [],
                 "current": False,
                 "isActive": False,
                 "isDeletable": True,
                 "isEditable": True,
                 "isValid": True,
                 "name": "Jank Page: " + champions[str(champ)],
                 "order": 1,
                 "primaryStyleId": keystones[0],
                 "selectedPerkIds": rune_list,
                 "subStyleId": keystones[1],
                 'api_key': API_KEY}

    return rune_page


def random_sums(role):

    with open('summoner_spells_id.json') as f:
        sums = json.load(f)

    if role == 'jungle':
        selections = {"selectedSkinId": 0,
                      "spell1Id": 11,
                      "spell2Id": choice(sums['Spells']),
                      "wardSkinId": 0
                      }
    else:
        rand_sums = sample(sums['Spells'], 2)
        selections = {"selectedSkinId": 0,
                      "spell1Id": rand_sums[0],
                      "spell2Id": rand_sums[1],
                      "wardSkinId": 0
                      }

    return selections


def delete_old_builds():

    for folder in listdir('C:\\Riot Games\\League of Legends\\Config\\Champions\\'):

        files = listdir('C:\\Riot Games\\League of Legends\\Config\\Champions\\' + folder
                        + '\\Recommended')
        if files.__contains__('JankBuild.json'):
            chdir('C:\\Riot Games\\League of Legends\\Config\\Champions\\' + folder
                  + '\\Recommended')
            remove('JankBuild.json')

    chdir(path.dirname(path.realpath(__file__)))


def get_api_key():
    return API_KEY
