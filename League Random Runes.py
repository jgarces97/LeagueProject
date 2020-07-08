import random
from lcu_driver import Connector
import json
from random import sample
import os

connector = Connector()
API_KEY = 'RGAPI-8275b631-142e-415c-b7b1-3afa55cd7709'


async def random_items(champ):

    starter_items = [{"id": "1055", "count": 1}, {"id": "2003", "count": 1}, {"id": "3340", "count": 1},
                    {"id": "3364", "count": 1}, {"id": "2263", "count": 1}, {"id": "2055", "count": 1}]

    final_items = [{"id": "3078", "count": 1}, {"id": "3047", "count": 1}, {"id": "3074", "count": 1},
                    {"id": "3812", "count": 1}, {"id": "3053", "count": 1}, {"id": "3026", "count": 1}]


    random_build = {
     "title": "Jank Build     ",
     "type": "custom",
     "map": "any",
     "mode": "any",
     "priority": True,
     "sortrank": 0,
     "blocks": [{
            "recMath": False,
            "minSummonerLevel": -1,
            "maxSummonerLevel": -1,
            "showIfSummonerSpell": "",
            "hideIfSummonerSpell": "",
            "type": "Jank Starting Items & Trinkets",
            "items": starter_items
        },
         {
             "recMath": False,
             "minSummonerLevel": -1,
             "maxSummonerLevel": -1,
             "showIfSummonerSpell": "",
             "hideIfSummonerSpell": "",
             "type": "Jank Final Build",
             "items": final_items
         }],
     "championKey": champ
    }
    return random_build


def random_runes():

    rune_list = []
    with open('rune_ids.json') as f:
        runes = json.load(f)

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
        rune_list.extend(
            sample(runes['keystones'][str(keystones[1])][key], 1))

    for key in runes['little_runes'].keys():
        rune_list.extend(sample(runes['little_runes'][key], 1))

    rune_page = {"autoModifiedSelections": [],
                 "current": False,
                 "isActive": False,
                 "isDeletable": True,
                 "isEditable": True,
                 "isValid": True,
                 "name": "Jank Page",
                 "order": 1,
                 "primaryStyleId": keystones[0],
                 "selectedPerkIds": rune_list,
                 "subStyleId": keystones[1],
                 'api_key': API_KEY}

    return rune_page

def random_sums():

    with open('summoner_spell_ids.json') as f:
        sums = json.load(f)
    rand_sums = sample(sums['Spells'],2)

    selections = {"selectedSkinId": 0,
                   "spell1Id": rand_sums[0],
                   "spell2Id": rand_sums[1],
                   "wardSkinId": 0
                    }
    return selections

async def set_sums(connection):
    set_sums_request = await connection.request('patch', '/lol-champ-select/v1/session/my-selection', data = random_sums())

async def lockin(connection):

    champs_owned = await connection.request('get', '/lol-champ-select/v1/pickable-champion-ids', data={
        'api_key': API_KEY})
    champs_owned = list(await champs_owned.json())
    champ = random.choice(champs_owned)
    lock = await connection.request('patch', '/lol-champ-select/v1/session/actions/1',
                                    data={"actorCellId": 0, "championId": champ, "completed": True, "id": 0,
                                          "isAllyAction": True, "type": "string", 'api_key': API_KEY})
    return champ


async def set_rune_page(connection):

    inv_size_req = await connection.request('get', '/lol-perks/v1/inventory', data={'api_key': API_KEY})
    inv_size_json = await inv_size_req.json()
    inv_size = inv_size_json['ownedPageCount']

    all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
    all_pages_json = await all_pages_req.json()

    for page in all_pages_json:
        if page['name'] == 'Jank Page':
            del_id = page['id']
            await connection.request('delete', '/lol-perks/v1/pages/' + str(del_id), data={'api_key': API_KEY})

    all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
    all_pages_json = await all_pages_req.json()
    num_pages = len(all_pages_json) - 5

    if num_pages < inv_size:
        all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
        all_pages_json = await all_pages_req.json()

        for page in all_pages_json:
            if page['name'] == 'Jank Page':
                curr_id = page['id']
                await connection.request('delete', '/lol-perks/v1/currentpage', data={'id': curr_id, 'api_key': API_KEY})

        put_page_req = await connection.request('post', '/lol-perks/v1/pages', data=random_runes())


async def set_item_page(champ_id):

    with open('champ_id.json') as f:
        champs = json.load(f)

    random_build = await random_items(champs[str(champ_id)])
    if not os.path.exists('C:\\Riot Games\\League of Legends\\Config\\Champions\\'+ champs[str(champ_id)]
                          + '\\Recommended'):
        os.makedirs('C:\\Riot Games\\League of Legends\\Config\\Champions\\'+ champs[str(champ_id)]
                    + '\\Recommended')

    with open('C:\\Riot Games\\League of Legends\\Config\\Champions\\'+ champs[str(champ_id)]
              + '\\Recommended\\JankBuild.json', 'w') as fp:
        json.dump(random_build, fp)


@connector.ready
async def connect(connection):

    # check if the user is already logged into his account
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner', data={'api_key': API_KEY})
    if summoner.status != 200:
        print('Please login into your account')
    else:
        print('Client Connected')
        print('Locking in Random Champ')
        champ = await lockin(connection)
        bad_req = await connection.request('get', '/data-store/v1/install-dir', data={'api_key': API_KEY})
        print(await bad_req.json())
        print('Setting up a random rune page')
        await set_rune_page(connection)
        bad_req = await connection.request('get', '/data-store/v1/install-dir', data={'api_key': API_KEY})
        print(await bad_req.json())
        print('Setting random summoner Spells')
        await set_sums(connection)
        bad_req = await connection.request('get', '/data-store/v1/install-dir', data={'api_key': API_KEY})
        print(bad_req)
        print('Importing Random Item Page')
        await set_item_page(champ)
        bad_req = await connection.request('get', '/data-store/v1/install-dir', data={'api_key': API_KEY})
        print(await bad_req.json())


connector.start()
