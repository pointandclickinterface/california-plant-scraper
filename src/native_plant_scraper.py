import sys
import os
import requests
import math
import pandas as pd         
from bs4 import BeautifulSoup
from tqdm import tqdm

# gets number of pages of plants
def get_pages(zipcode=None):
    if zipcode == None:
        calurl = requests.get("https://calscape.org/loc-California/cat-All-Plants", timeout=5)
        calhtmltext = calurl.text
        scapesoup = BeautifulSoup(calhtmltext, "html.parser")
        total_pages = math.ceil(int(scapesoup.find(class_='counter_text').find('b').text.split(' ')[0])/100)
        return total_pages
    else:
        try:
            stringbuilder='https://calscape.org/loc-'+str(zipcode)+'/cat-All-Plants/.html'
            calurl = requests.get(stringbuilder, timeout=5)
            calhtmltext = calurl.text
            scapesoup = BeautifulSoup(calhtmltext, "html.parser")
            total_pages = math.ceil(int(scapesoup.find(class_='counter_text').find('b').text.split(' ')[0])/100)
            return total_pages
        except Exception as e:
            print(e)

# gets urls of plants
def get_urls(pages, switch, zipcode = None):
    calscapeurls=[]
    print("Getting lists of plants...")
    if switch == True and zipcode == None:
        for i in tqdm(range(1,(pages+1))):
            href='https://calscape.org/loc-California/cat-All-Plants//page-'+str(i)+'.html'
            cal_page_url = requests.get(href, timeout=5)
            cal_page_text = cal_page_url.text
            cal_page_soup = BeautifulSoup(cal_page_text, "html.parser")
            for link in cal_page_soup.find_all(class_="pad"):
                calscapeurls.append(link.find('a').get('onclick').strip('javascript:showPageLoading({});').split(', ')[3][7:][:-1])
        return calscapeurls
    elif switch == True:
        for i in tqdm(range(1,(pages+1))):
            href='https://calscape.org/loc-'+str(zipcode)+'/cat-All-Plants//page-'+str(i)+'.html'
            cal_page_url = requests.get(href, timeout=5)
            cal_page_text = cal_page_url.text
            cal_page_soup = BeautifulSoup(cal_page_text, "html.parser")
            for link in cal_page_soup.find_all(class_="pad"):
                calscapeurls.append(link.find('a').get('onclick').strip('javascript:showPageLoading({});').split(', ')[3][7:][:-1])
        return calscapeurls
    elif switch == False and zipcode == None:
        href='https://calscape.org/loc-California/cat-All-Plants//page-1.html'
        cal_page_url = requests.get(href, timeout=5)
        cal_page_text = cal_page_url.text
        cal_page_soup = BeautifulSoup(cal_page_text, "html.parser")
        for link in cal_page_soup.find_all(class_="pad")[:5]:
            calscapeurls.append(link.find('a').get('onclick').strip('javascript:showPageLoading({});').split(', ')[3][7:][:-1])
        return calscapeurls
    else:
        href='https://calscape.org/loc-'+str(zipcode)+'/cat-All-Plants//page-1.html'
        cal_page_url = requests.get(href, timeout=5)
        cal_page_text = cal_page_url.text
        cal_page_soup = BeautifulSoup(cal_page_text, "html.parser")
        for link in cal_page_soup.find_all(class_="pad")[:5]:
            calscapeurls.append(link.find('a').get('onclick').strip('javascript:showPageLoading({});').split(', ')[3][7:][:-1])
        return calscapeurls

def get_df(urls):
    df= pd.DataFrame(columns=[
        'Plant Name', 'Other Names', 'Plant Type', 
        'Plant Size', 'Growing Zones', 'Rainfall', 
        'Summer Rainfall', 'Sun', 'Moisture', 'Soil', 
        'Coldest Month', 'Hottest Month', 'Cold Tolerance', 
        'Humidity', 'Elevation', 'Uses', 'Flower Color',
        'Ease of Care','Sightings', 'Image', 'Calscape url'])

    print('Assembling dataframe...')
    for i in tqdm(range(len(urls))):
        count=i+1
    
        # url
        link= urls[i]
        url='https://'+link
    
        # gets the html from the plant page
        plant_page_url = requests.get(url, timeout=5)
        plant_page_text = plant_page_url.text
        calsoup = BeautifulSoup(plant_page_text, "html.parser")
    
        # name
        try:
            plantname=calsoup.find(id="plant_name").text
            sciname=plantname.split(' ')
        except:
            plantname=None
            sciname=None

        # alt names
        try:
            othernames=calsoup.find(class_="alternative_names").find(class_="info").text.strip('\t\n')
        except:
            othernames= None

        # type
        try:
            planttype=calsoup.find(class_="plant_type").find(class_="info").text.strip('\t\n')
        except:
            planttype=None
   
        # size
        try:
            plantsize=calsoup.find(class_="size").find(class_="info").text.strip('\t\n')
        except:
            plantsize= None
    
        # sun
        try:
            sun=calsoup.find(class_="sun").find(class_="info").text.strip('\t\n')
        except:
            sun= None

        # flower color
        try:
            flower=calsoup.find(class_="flower_color").find(class_="info").text.strip('\t\n')
        except:
            flower= None
  
        # ease of care
        try:
            care=calsoup.find(class_="ease_of_care").find(class_="info").text.strip('\t\n')
        except:
            care= None
  
        # uses
        try:
            uses=calsoup.find(class_="common_uses").find(class_="info").text.strip('\t\n')
        except:
            uses= None

        # moisture
        try:
            moisture = calsoup.find(class_="moisture").find(class_="info").text.strip('\t\n')
        except:
            moisture= None
  
        #soil 
        try:
            soil = calsoup.find(class_="soil_description").find(class_="info").text.strip('\t\n')
        except:
            soil= None

        # cold tolerance
        try:
            coldtol = calsoup.find(class_="cold_tolerance").find(class_="info").text.strip('\t\n')
        except:
            coldtol= None

        # climate info
        try:
            climate=calsoup.find(class_="climate").find(class_="info").text.strip('\t\n')
            climate_list=climate.split(', ')
            rainfall=climate_list[0][22:]
            sumrainfall=climate_list[1][22:]
            coldmonth=climate_list[2][14:]
            hotmonth=climate_list[3][14:]
            humid=climate_list[4][10:]
            elevation=climate_list[5][11:]
        except:
            rainfall=None
            sumrainfall=None
            coldmonth=None
            hotmonth=None
            humid=None
            elevation=None
  
        #sightings and image

        try:
            r = requests.get('https://api.inaturalist.org/v1/search?q='+sciname[0]+'%20'+sciname[1], auth=('user', 'pass'), timeout=5)
            obs = r.json()['results'][0]['record']['observations_count']
            pic = r.json()['results'][0]['record']['taxon_photos'][0]['photo']['small_url']

        except:
            obs=None
            pic=None

        #growing zone from Daves Garden  
        try:
            url2 = requests.get("https://davesgarden.com/guides/pf/latinsearch.php?search_query="+sciname[0]+"+"+sciname[1]+"&submit=Search", timeout=5)
            htmltext = url2.text
        except:
            htmltext=None

        try:
            davesoup = BeautifulSoup(htmltext, "html.parser")
            url3="https://davesgarden.com"+davesoup.find_all('tr')[1].find_all('td')[4].find('a').get('href')
            url4=requests.get(url3, timeout=5)
            htmltext2=url4.text

            davesoup2 = BeautifulSoup(htmltext2, "html.parser")

            growing_zones=[]
            for zone in davesoup2.find_all('p'):
            # print(zone.text)
                if 'USDA Zone' in zone.text:
                    growing_zones.append(zone.text)
            if len(growing_zones) > 0:
                gz=str(growing_zones)
            else: 
                gz=None
        except:
            gz=None


        # assemble the row    
        df.loc[count]=[
            plantname, othernames, planttype, 
            plantsize, gz, rainfall, sumrainfall, 
            sun, moisture, soil, coldmonth, hotmonth, 
            coldtol, humid, elevation, uses, flower, 
            care, obs, pic, url]
    return df 

#the default dataframe
#gets all plant info for all of California or a locality

def default_function(zipcode=None):
    page_num = get_pages(zipcode)
    plant_urls = get_urls(page_num, True, zipcode)
    default_df = get_df(plant_urls)
    print('\n Dataframe shape:') 
    print(default_df.shape)
    for i in range(1, len(default_df)+1)[:10]:

        print(' ')
        print(default_df.loc[i])
    return default_df

#the sample dataframe
#gets a sample of info for all of California or a locality

def scrape_function(zipcode=None):
    page_num = 1
    plant_urls = get_urls(page_num, False, zipcode)
    short_df = get_df(plant_urls)
    for i in range(1, len(short_df)+1):
        print(' ')
        print(short_df.loc[i])
    return short_df

#the static dataframe
#gets all plant info for all of California from a csv file

def static_function(path_to_static_data):
    csv_df = pd.read_csv(path_to_static_data)
    csv_df.set_index('Index')
    print('\n CSV shape:') 
    print(csv_df.shape)
    for i in range(len(csv_df))[:5]:
        print(' ')
        print(csv_df.loc[i])
    
    return csv_df

if __name__ == '__main__':
    if len(sys.argv) == 1:

#default
        default_function()
    elif sys.argv[1] == '--scrape':
        if len(sys.argv)==3:
            scrape_function(sys.argv[2])
        else:
#scrape
            scrape_function()

    elif sys.argv[1] == '--static':
        path_to_static_data = sys.argv[2]
        static_function(path_to_static_data)
#static 
    else:
        default_function(sys.argv[1])