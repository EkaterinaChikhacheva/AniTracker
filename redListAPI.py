import os
import requests
import json

TOKEN = '9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee'
def get_list_of_species_by_country(country):

    
    country = "AZ"
    resp = requests.get(
                # 'http://apiv3.iucnredlist.org/country/getspecies',
                # params={'country': 'AZ', 'token': f'{TOKEN}'}
                
                f'http://apiv3.iucnredlist.org/api/v3/country/getspecies/{country}?token={TOKEN}')

    return print(resp.json())



# class Red_List:
#     "Red list API"

#     def __init__(self): #what to write in init here???
