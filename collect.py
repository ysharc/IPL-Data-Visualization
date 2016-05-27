'''
This program is to clean and gather data for the input_file.csv of the

IPL match Visualization project
'''
import pandas as pd

import csv

import glob

import requests,bs4,re

#Start Session

session = requests.Session()
session.trust_env = False #incase you use a proxy server comment out this line


#get all the names of csv files in folder
file_names = glob.glob('*.csv')

venue_lat_lon = {}

short_form = lambda x:x[0].lower()

# Initiate input_file creation and add headers
with open('input_data.csv','wb') as input_file:
    writer = csv.writer(input_file,quoting=csv.QUOTE_ALL)

    #Writing header
    writer.writerow(['Match','Season','date','venue','city','lat','lon','Winner','sf'])

    #Adding data rows
    for filename in file_names:

        df = pd.read_csv(filename, warn_bad_lines=False, error_bad_lines=False)

        match = df.iloc[0,1]+' VS '+df.iloc[1,1]
        season = df.loc[df['version']=='season'].iloc[0,1]
        date = df.loc[df['version']=='date'].iloc[0,1]
        venue = df.loc[df['version']=='venue'].iloc[0,1]
        city = df.loc[df['version']=='city'].iloc[0,1]
        
        try:
            winner = df.loc[df['version']=='winner'].iloc[0,1]
        except:
            winner = "TIE"
        sf = ''.join(map(short_form,winner.split(' ')))
        
        if type(city)==float:
            city = 'NA'
        
        if (venue,city) in venue_lat_lon:
            
            writer.writerow([match,season,date,venue,city,venue_lat_lon[(venue,city)][0],venue_lat_lon[(venue,city)][1],winner,sf])

        else:

            response = session.get('http://nominatim.openstreetmap.org/search.php?q='+venue.replace(' ','+')+'&polygon=1&viewbox=')

            soup = bs4.BeautifulSoup(response.text,'html.parser')

            required_element = str(soup.select('script'))

            phrase = re.compile('nominatim_results(.*?)\[(.*?)\]')

            ans = phrase.search(required_element)

            lat_lon_str = ans.group()

            if lat_lon_str=='nominatim_results = [\\n\\n]':

                if city=="NA":
                    print 'found a record with no address. venue:'+ str(venue) + 'city: Not Available'
                else:
                    try:
                        
                        response = session.get('http://nominatim.openstreetmap.org/search.php?q='+city.replace(' ','+')+'&polygon=1&viewbox=')

                        soup = bs4.BeautifulSoup(response.text,'html.parser')

                        required_element = str(soup.select('script'))

                        phrase = re.compile('nominatim_results(.*?)\[(.*?)\]')

                        ans = phrase.search(required_element)

                        lat_lon_str = ans.group()    

                    except:

                        print 'found a venue,city without address'+ str(venue)                
                
            lat_pattern = re.compile(ur'lat": "(.*?)"')

            lat = lat_pattern.search(lat_lon_str)

            lon_pattern = re.compile(ur'lon": "(.*?)"')

            lon = lon_pattern.search(lat_lon_str)

            try:
                lat = lat.group()
                lon = lon.group()
                lat = float(lat[7:-1])
                lon = float(lon[7:-1])
                print 'address retreival success. Venue:'+str(venue)+' lat:'+str(lat)+' lon:'+str(lon)
            except:
                lat = 'Not Available'
                lon = 'Not Available'
                print 'found a venue without address'+ str(venue) +'\n'

                decision = raw_input('Do you want to manually enter the coordinates for' + str(venue) + '? Y|N')

                if decision == 'Y'or'y':
                    try:
                        lat = float(raw_input('please enter latitude in degrees :'))
                    except:
                        print 'invalid latitude co-ordinates'

                    try:
                        lon = float(raw_input('please enter longitude in degrees :'))
                    except:
                        print 'invalid longitude co-ordinates'

                elif decision == 'N' or 'n':
                    print 'setting lat and lon values to NA'
                else:
                    print ' invalid decision, setting lat and lon values to NA'

            venue_lat_lon[(venue,city)] = (lat,lon)

            writer.writerow([match,season,date,venue,city,venue_lat_lon[(venue,city)][0],venue_lat_lon[(venue,city)][1],winner,sf])
        
