import sys
import random
import json
import requests
import native_plant_scraper
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from tqdm import  tqdm

#there are false positives for chained assignments
#comment this next line out to see warnings
pd.options.mode.chained_assignment = None

#makes a clean dataframe in the style of the plant dataframes
def template_dataframe():
    return pd.DataFrame(columns=['Plant Name', 'Other Names', 'Plant Type', 'Plant Size', 
                                'Growing Zones', 'Will grow in zone', 'Rainfall', 'Summer Rainfall', 
                                'Sun', 'Moisture', 'Soil', 'Coldest Month', 'Hottest Month', 'Cold Tolerance', 
                                'Humidity', 'Elevation', 'Uses', 'Flower Color','Ease of Care','Sightings', 
                                'Image', 'Calscape url'])

#get all zipcodes from LA
def get_zip_df():
    new_zip_df= pd.DataFrame(columns=["zipcode", 'local'])

    zip_url = requests.get("http://www.laalmanac.com/communications/cm02a90001-90899.php", timeout=10)
    zip_text = zip_url.text
    zipsoup = BeautifulSoup(zip_text, "html.parser")
    list_tags=zipsoup.find_all('tr')
    list_tags.pop(0)
    for i in range(len(list_tags)):
        new_zip_df.loc[i]=[list_tags[i].find_all('td')[0].text,list_tags[i].find_all('td')[1].text]
    
    return new_zip_df


#picks a random LA zipcode where the growing zone is known
def get_usuable_zip(df):
    plant_zip_df_list=[]
    zip_nums=""
    zip_loc=""
    found_a_zip=False
    zone_json={}

    while found_a_zip == False:
        zip_num = df.loc[random.sample(range(0, len(df)), 1)[0]]['zipcode']
        zone_url = requests.get("https://phzmapi.org/"+str(zip_num)+".json", timeout=10)
        zone_text = zone_url.text
        if "The specified key does not exist." not in zone_text:
            zip_nums=zip_num
            zip_loc=zip_num = df.loc[random.sample(range(0, len(df)), 1)[0]]['local']
            zone_json=zone_url.json()
            found_a_zip=True
    
    return zip_loc, zip_nums, zone_json

#uses the scraper to get a dataframe for a specific zipcode
def get_local_df(zip_nums):
  page_num = native_plant_scraper.get_pages(zip_nums)
  plant_urls = native_plant_scraper.get_urls(page_num, True, zip_nums)
  plant_df = native_plant_scraper.get_df(plant_urls)

  return plant_df

#loads local csv files as dataframes
def open_local_df():
    boyle_heights_df=pd.read_csv("../data/boyle_heights.csv")
    malibu_df=pd.read_csv("../data/malibu.csv")
    larchmont_df=pd.read_csv("../data/larchmont.csv")
    boyle_heights_df = boyle_heights_df.replace({np.nan: None})
    malibu_df = malibu_df.replace({np.nan: None})
    larchmont_df = larchmont_df.replace({np.nan: None})
    return boyle_heights_df , malibu_df , larchmont_df

#opens local json files
def open_local_jsons():
    boyle=open("../data/boyle.json")
    boyle_json=json.load(boyle)
    boyle.close()

    mal=open("../data/malibu.json")
    malibu_json=json.load(mal)
    mal.close()

    larch=open("../data/larch.json")
    larchmont_json=json.load(larch)
    larch.close()


    return boyle_json, malibu_json, larchmont_json


# identifies if plant is a succulent then checks that it will grow in zipcode based on growing zone, cold tolerance or temperture if available
def find_succulents(loc_df,zone_json, local=True):
    succulent_df= template_dataframe()
    count=0
    if local==False:
        num= len(loc_df)+1
    else:
        num= len(loc_df)
    
    for i in tqdm(range(1, num)):
        if loc_df.loc[i]['Plant Type'] != None :
            if ('Succulent' in loc_df.loc[i]['Plant Type']):
                if loc_df.loc[i]['Growing Zones'] != None and zone_json['zone'] in loc_df.loc[i]['Growing Zones']:
                    succulent_df.loc[count]=loc_df.loc[i]
                    succulent_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Coldest Month'] != None and zone_json["temperature_range"].split(' ')[0] >= loc_df.loc[i]['Coldest Month'].replace('"', '').split(' ')[1]:
                    succulent_df.loc[count]=loc_df.loc[i]
                    succulent_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Cold Tolerance'] != None and float(zone_json["temperature_range"].split(' ')[0]) >= float(loc_df.loc[i]['Cold Tolerance'].replace('°', '').split(' ')[3]):
                    succulent_df.loc[count]=loc_df.loc[i]
                    succulent_df.loc[count]['Will grow in zone']=True
      
        count+=1
    return succulent_df

#identifies flowering shrubs that like full sun, low water, and are easy to grow    
def find_easy_full_sun_shrubs(loc_df,zone_json, local=True):
    if local==False:
        num= len(loc_df)+1
    else:
        num= len(loc_df)

    sun_df=template_dataframe()
    count=0

    for i in tqdm(range(1, num)):
        if loc_df.loc[i]['Sun'] != None :
            if ('Full Sun' in loc_df.loc[i]['Sun']) and (loc_df.loc[i]['Moisture'] != None) and ('Very Low' in loc_df.loc[i]['Moisture']) and ('Shrub' in loc_df.loc[i]['Plant Type']) and (loc_df.loc[i]['Flower Color'] != None) and (loc_df.loc[i]['Ease of Care'] != None) and ('Very Easy' in loc_df.loc[i]['Ease of Care']):
                if loc_df.loc[i]['Growing Zones'] != None and zone_json['zone'] in loc_df.loc[i]['Growing Zones']:
                    sun_df.loc[count]=loc_df.loc[i]
                    sun_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Coldest Month'] != None and zone_json["temperature_range"].split(' ')[0] >= loc_df.loc[i]['Coldest Month'].replace('"', '').split(' ')[1]:
                    sun_df.loc[count]=loc_df.loc[i]
                    sun_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Cold Tolerance'] != None and float(zone_json["temperature_range"].split(' ')[0]) >= float(loc_df.loc[i]['Cold Tolerance'].replace('°', '').split(' ')[3]):
                    sun_df.loc[count]=loc_df.loc[i]
                    sun_df.loc[count]['Will grow in zone']=True
        count+=1
    
    return sun_df

#finds plants for a butterfly garden
def find_rare_butterfly_garden_plants(loc_df, zone_json, local=True):
    butterfly_df=template_dataframe()
    count=0
    if local==False:
        num= len(loc_df)+1
    else:
        num= len(loc_df)

    for i in tqdm(range(1, num)):
        if loc_df.loc[i]['Uses'] != None :
            if ('Butterfly' in loc_df.loc[i]['Uses']):
                if loc_df.loc[i]['Growing Zones'] != None and zone_json['zone'] in loc_df.loc[i]['Growing Zones']:
                    butterfly_df.loc[count]=loc_df.loc[i]
                    butterfly_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Coldest Month'] != None and zone_json["temperature_range"].split(' ')[0] >= loc_df.loc[i]['Coldest Month'].replace('"', '').split(' ')[1]:
                    butterfly_df.loc[count]=loc_df.loc[i]
                    butterfly_df.loc[count]['Will grow in zone']=True
                elif loc_df.loc[i]['Cold Tolerance'] != None and float(zone_json["temperature_range"].split(' ')[0]) >= float(loc_df.loc[i]['Cold Tolerance'].replace('°', '').split(' ')[3]):
                    butterfly_df.loc[count]=loc_df.loc[i]
                    butterfly_df.loc[count]['Will grow in zone']=True
      
        count+=1
    
    return butterfly_df

# makes sun figure
def make_sun_figure(loc_df, zip_loc):
    loc_df.to_csv('fullsunshrubs.csv')
    if len(loc_df) < 10:
        sun_df = loc_df.sort_values(by=['Sightings'], ascending=False)
        sun_range=range(1,len(loc_df)+1)
    else:
        sun_df = loc_df.sort_values(by=['Sightings'], ascending=False).head(10)
        sun_range=range(1,10+1)
    plt.hlines(y=sun_range, xmin=0, xmax=sun_df['Sightings'], color='green')
    plt.scatter(sun_df['Sightings'], sun_range, s=40, alpha=1, color='coral')
    plt.yticks(sun_range, sun_df['Plant Name'])
    plt.xlabel('Number of Sightings')
    plt.title("Full Sun shrubs in "+zip_loc+ " with flowers that are very easy to grow (ordered by sightings)")
    plt.savefig('sun.png',bbox_inches="tight")
    plt.clf()

# makes succulent figure
def make_succulent_figure(loc_df, zip_loc):
    loc_df.to_csv('succulents.csv')
    if len(loc_df) < 10:
        succulent_df = loc_df.sort_values(by=['Sightings'], ascending=False)
        suc_range=range(1,len(loc_df)+1)
    else:
        succulent_df = loc_df.sort_values(by=['Sightings'], ascending=False).head(10)
        suc_range=range(1,10+1)
    plt.hlines(y=suc_range, xmin=0, xmax=succulent_df['Sightings'], color='green')
    plt.scatter(succulent_df['Sightings'], suc_range, s=40, alpha=1, color='deeppink',)
    plt.yticks(suc_range, succulent_df['Plant Name'])
    plt.xlabel('Number of Sightings')
    plt.title("Succulent plants to survive a wildfire in "+zip_loc+" (ordered by sightings)")
    plt.savefig('succulent.png', bbox_inches="tight")
    plt.clf()

# makes butterfly garden figure
def make_butterfly_figure(loc_df, zip_loc):
    loc_df.to_csv('butterflygarden.csv')
    if len(loc_df) < 10:
        butterfly_df = loc_df.sort_values(by=['Sightings'], ascending=True)
        butterfly_range=range(1,len(loc_df)+1)
    else:
        butterfly_df = loc_df.sort_values(by=['Sightings'], ascending=True).head(10)
        butterfly_range=range(1,10+1)
    plt.hlines(y=butterfly_range, xmin=0, xmax=butterfly_df['Sightings'], color='green')
    plt.scatter(butterfly_df['Sightings'], butterfly_range, s=40, alpha=1, color='deeppink',)
    plt.yticks(butterfly_range, butterfly_df['Plant Name'])
    plt.xlabel('Number of Sightings')
    plt.title("Plants for a butterfly garden in "+zip_loc+" with fewest sightings (ordered by sightings)")
    plt.savefig('butterfly.png', bbox_inches="tight")
    plt.clf()



#static mode functions
def static_mode():
    boyle_heights_df, malibu_df, larchmont_df =open_local_df()
    boyle_zip=90033
    malibu_zip=90263
    larchmont_zip=90004
    boyle_name="Boyle Heights"
    malibu_name="Malibu"
    larchmont_name="Larchmont"

    boyle_json, malibu_json, larchmont_json = open_local_jsons()
    print('Building filtered dataframes...')
    succulent_df = find_succulents(malibu_df, malibu_json)
    sun_df = find_easy_full_sun_shrubs(boyle_heights_df, boyle_json)
    butterfly_df = find_rare_butterfly_garden_plants(larchmont_df, larchmont_json)
    print('Creating Figures...')
    make_succulent_figure(succulent_df, malibu_name)
    make_sun_figure(sun_df, boyle_name)
    make_butterfly_figure(butterfly_df, larchmont_name)
    print('Done!')
    

#defaul mode functions
def default_mode():
    local=False
    zip_df = get_zip_df()
    zip_loc, zip_num, zone_json = get_usuable_zip(zip_df)
    plant_df = get_local_df(zip_num)
    print('Building filtered dataframes...')
    succulent_df = find_succulents(plant_df, zone_json, local)
    sun_df = find_easy_full_sun_shrubs(plant_df, zone_json, local)
    butterfly_df = find_rare_butterfly_garden_plants(plant_df, zone_json, local)
    print('Creating Figures...')
    make_succulent_figure(plant_df, zip_loc)
    make_sun_figure(plant_df, zip_loc)
    make_butterfly_figure(plant_df, zip_loc)
    print('Done!')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        default_mode()
    elif sys.argv[1] == '--static':
        static_mode()

