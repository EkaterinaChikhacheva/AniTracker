# Helper functions are stored here

import requests



TOKEN = '9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee'
RED_LIST_URL = 'http://apiv3.iucnredlist.org'



def how_many_pages_RL():
    """Returns a num of pages needed to get all the data from RL API"""
    page = 0
    res = requests.get(f'{RED_LIST_URL}/api/v3/species/page/{page}?token={TOKEN}')

    # add a page if res in not null
    while res:

        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print(res)
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

        page += 1
        return page


how_many_pages_RL()