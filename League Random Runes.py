from random import sample, choice
from lcu_driver import Connector
import json
from os import path, makedirs
from re import search
from util import random_runes, random_sums, delete_old_builds, get_api_key

connector = Connector()
API_KEY = get_api_key()


async def random_items(champ):

    starter_items = [{"id": "1054", "count": 1}, {"id": "1055", "count": 1}, {"id": "1056", "count": 1},
                    {"id": "1082", "count": 1}, {"id": "1039", "count": 1}, {"id": "1041", "count": 1}]

    all_items = ['3001', '3003', '3004', '3022', '3025', '3026', '3027', '3028', '3030', '3031', '3033', '3036',
                   '3046', '3046', '3050', '3053', '3065', '3068', '3071', '3072', '3074', '3075', '3078', '3083',
                   '3085', '3087', '3089', '3091', '3094', '3095', '3100', '3102', '3107', '3109', '3110', '3115',
                   '3116', '3124', '3135', '3139', '3142', '3143', '3146', '3151', '3152', '3153', '3156', '3157',
                   '3165', '3174', '3181', '3190', '3194', '3222', '3285', '3742', '3748', '3800', '3812', '3814',
                   '3905', '3907']

    jungle_items = ['1400', '1401', '1402', '1412', '1413', '1414', '1416', '1419']

    support_items = ['3850', '3854', '3858', '3862']

    boots = ['3006', '3047', '3020', '3111', '3117', '3158', '3009']

    items = sample(all_items, 5)
    boot = choice(boots)

    final_items = [{"id": boot, "count": 1}, {"id": items[0], "count": 1}, {"id": items[1], "count": 1},
                    {"id": items[2], "count": 1}, {"id": items[3], "count": 1}, {"id": items[4], "count": 1}]


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


async def set_sums(connection):

    set_sums_request = await connection.request('patch', '/lol-champ-select/v1/session/my-selection',
                                                data=random_sums('top'))


async def lock_in_champ(connection, turn_id, player_id):

    champs_owned = await connection.request('get', '/lol-champ-select/v1/pickable-champion-ids', data={
        'api_key': API_KEY})
    champs_owned = list(await champs_owned.json())
    champ = choice(champs_owned)
    lock = await connection.request('patch', '/lol-champ-select/v1/session/actions/' + str(turn_id),
                                    data={"actorCellId": int(player_id), "championId": champ, "completed": True, "id": 0,
                                          "isAllyAction": True, "type": "string", 'api_key': API_KEY})
    lock_in_json = await lock.json()
    return champ, lock_in_json


async def set_rune_page(connection, champ):

    # Gets the max number of rune pages you own
    inv_size_req = await connection.request('get', '/lol-perks/v1/inventory', data={'api_key': API_KEY})
    inv_size_json = await inv_size_req.json()
    inv_size = inv_size_json['ownedPageCount']

    # Gets all your rune pages
    all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
    all_pages_json = await all_pages_req.json()

    # Deletes any old Jank rune page
    for page in all_pages_json:
        if search('\AJank Page:', page['name']):
            del_id = page['id']
            await connection.request('delete', '/lol-perks/v1/pages/' + str(del_id), data={'api_key': API_KEY})

    # Checks for the number of rune pages you currently have equipped
    all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
    all_pages_json = await all_pages_req.json()
    num_pages = len(all_pages_json) - 5

    # If open rune page adds the Jank rune page
    if num_pages < inv_size:
        # Gets all rune pages
        all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
        all_pages_json = await all_pages_req.json()

        # Adds the Jank rune page
        put_page_req = await connection.request('post', '/lol-perks/v1/pages', data=random_runes(champ))

        # Looks for a Jank rune page and sets it to the current rune page
        for page in all_pages_json:
            if search('\AJank Page:', page['name']):
                curr_id = page['id']
                await connection.request('patch', '/lol-perks/v1/currentpage', data={'id': curr_id, 'api_key': API_KEY})

    else:
        print('NOT ENOUGH RUNE PAGES')


async def set_item_page(champ_id):

    with open('champ_id.json') as f:
        champs = json.load(f)

    random_build = await random_items(champs[str(champ_id)])
    if not path.exists('C:\\Riot Games\\League of Legends\\Config\\Champions\\'+ champs[str(champ_id)]
                          + '\\Recommended'):
        makedirs('C:\\Riot Games\\League of Legends\\Config\\Champions\\'+ champs[str(champ_id)]
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
        delete_old_builds()


@connector.close
async def disconnect(_):
    print('The client have been closed!')
    delete_old_builds()
    await connect.stop()


@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def champ_select_listener(connection, event):

    player_id = event.data['localPlayerCellId']
    actions = [item for sublist in event.data['actions'] for item in sublist]
    is_pick_turn = False
    is_pick_complete = False
    champion_picked_id = 0
    champ_picked_name = ''
    turn_id = -1

    for act in actions:
        # Finds if its the users turn to pick
        if act['actorCellId'] == player_id and act['isInProgress'] is True and act['type'] == 'pick':
            is_pick_turn = True
            turn_id = act['id']
        # Finds if the user already picked a champ
        elif act['actorCellId'] == player_id and act['completed'] is True and act['type'] == 'pick':
            is_pick_complete = True
            champion_picked_id = act['championId']
            with open('champ_id.json') as f:
                champions = json.load(f)
            champ_picked_name = champions[str(champion_picked_id)]

    # Gets all your rune pages
    all_pages_req = await connection.request('get', '/lol-perks/v1/pages', data={'api_key': API_KEY})
    all_pages_json = await all_pages_req.json()

    # Finds the name of the champ on a Jank page if there
    rune_page_champ = ''
    for page in all_pages_json:
        if search('\AJank Page:', page['name']):
            rune_page_champ = page['name'][11:]

    if is_pick_turn:
        await lock_in_champ(connection, turn_id, player_id)

    elif is_pick_complete and champ_picked_name != rune_page_champ:
        await set_rune_page(connection, champion_picked_id)
        await set_item_page(champion_picked_id)
        await set_sums(connection)


connector.start()
