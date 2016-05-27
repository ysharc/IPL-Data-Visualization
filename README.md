# IPL-Data-Visualization
Interactive web map for IPL match data from 04/18/2008 to 05/20/2016. The interactive map can be found at http://rpubs.com/ysharc/184185

## Quick Usage
  1. Download IPL match data from http://cricsheet.org/downloads/ipl_csv.zip
  2. Extract it in any folder of your choice and run collect.py from the same folder (if running from a different location change the path of the files in collect.py)
  3. Now for plotting the data run plot.R in RStudio to view the map instantly (if running in the R console, execute the next command to export it to a html file)
    1. library(htmlwidgets)
    2. saveWidget(map, file="map.html")  

##Quick Look
  1. Map starts with an overview of all IPL matches played until now.
     ![](http://i.imgur.com/VvZKdpQ.png)
  2. Select a subgroup to view their respective cluster. (For example kolkatta_wins in the following image)
     ![](http://i.imgur.com/SjNf6Uq.png)
  3. Hover mouse over a cluster point to see the area it covers
     ![](http://i.imgur.com/JnZuRla.png)
  4. zoom in to see the spread of the group
     ![](http://i.imgur.com/O0O6xKZ.png)   
  5. At the final zoom level click the cluster to display a spiderweb of all the matches that took place in it.
     ![](http://i.imgur.com/T7atVeM.png)
  6. The starting point of the spiral contains early day matches, where as the last point contains the latest match
     ![](http://i.imgur.com/eQycYSx.png)
     ![](http://i.imgur.com/8MpGfcU.png)

## Process
  The interactive map creation can be summarized by the collection and plot parts. The overview of the processes and code are explained below

######Data Collection
  Download the Total IPL match data from http://cricsheet.org/downloads/ipl_csv.zip . The archive contains a csv file for every match of the event. Each file typically contains the following structure

version	| 1			| ''
------- | --------------------- | ------------------------------------------------
info	| team			| Delhi Daredevils
info	| team			| Sunrisers Hyderabad
info	| gender		| male
info	| season		| 2016
info	| date			| 5/20/2016
info	| competition		| Indian Premier League
info	| match_number		| 52
info	| venue			| Shaheed Veer Narayan Singh International Stadium
info	| city			| Raipur
info	| toss_winner		| Delhi Daredevils
info	| toss_decision	   	| field
info	| player_of_match	| KK Nair
info	| umpire		| A Nand Kishore
info	| umpire		| BNJ Oxenford
info	| reserve_umpire	| YC Barde
info	| tv_umpire		| VK Sharma
info	| match_referee		| S Chaturvedi
info	| winner		| Delhi Daredevils
info	| winner_wickets	| 6

The remaining lines contain ball to ball info of the two innings, but the columns are inconsistent. For example a normal ball contains 8 columns where as a wicket contains 11 columns. Using `glob` library extract all the names of the csv files to access 
```
   file_names = glob.glob('*.csv')
``` 

Next using the `csv` library open an input file, create a writer object and create the header
```
with open('input_data.csv','wb') as input_file:
   writer = csv.writer(input_file,quoting=csv.QUOTE_ALL)
   writer.writerow(['Match','Season','date','venue','city','lat','lon','Winner','sf'])
```

With the `input_file` open iterate over every file name  in the list `file_names` and extract info using the `pandas` library. For example extract the date of each match as shown below
```
for filename in file_names:

        df = pd.read_csv(filename, warn_bad_lines=False, error_bad_lines=False)

        date = df.loc[df['version']=='date'].iloc[0,1]
```

Extract whatever features you want to plot on the map, here in this example the match,date and winner are plotted. The next important step is to collect co-ordinates of the location using any geocoding API or webscraping. Here in this example the nominatim search is used to query for co-ordinates(more info on parameters at http://wiki.openstreetmap.org/wiki/Nominatim#Parameters).

Using the `requests` and `beautifulsoup` libraries collect and scrape the data you need. 
```
            response = session.get('http://nominatim.openstreetmap.org/search.php?q='+venue.replace(' ','+')+'&polygon=1&viewbox=')

            soup = bs4.BeautifulSoup(response.text,'html.parser')

            required_element = str(soup.select('script'))

            phrase = re.compile('nominatim_results(.*?)\[(.*?)\]')

            ans = phrase.search(required_element)

            lat_lon_str = ans.group()

            lat_pattern = re.compile(ur'lat": "(.*?)"')

            lat = lat_pattern.search(lat_lon_str)

            lon_pattern = re.compile(ur'lon": "(.*?)"')

            lon = lon_pattern.search(lat_lon_str)

```

Now that you have collected all the data needed, update our input file with the info gathered
```
            writer.writerow([match,season,date,venue,city,venue_lat_lon[(venue,city)][0],venue_lat_lon[(venue,city)][1],winner,sf])
```

Finally you have the input_data.csv file created with all the info you wanted, now moving on to the plot process.

###### Plotting
  In this process we create interactive web maps using `leaflet` and `htmltools` packages of `R`. The first step is to read in the data we created in the previous process
```
IPL = read.csv("input_data.csv")
``` 

  Create subsets of the dataframe for analyzing the win locations of each team. For example
```
chennai_wins <- IPL[which(IPL$Winner =='Chennai Super Kings'),]
```

  Next create icons for each team to display on the map 
```
teamIcons <- iconList(
  csk = makeIcon("csk.png", iconWidth=36,iconHeight=36),
  dc = makeIcon("dc.png", iconWidth=36,iconHeight=36),
  dd = makeIcon("dd.png", iconWidth=36,iconHeight=36),
  gl = makeIcon("gl.png", iconWidth=36,iconHeight=36),
  kxp = makeIcon("kxp.png", iconWidth=36,iconHeight=36),
  ktk = makeIcon("ktk.png", iconWidth=36,iconHeight=36),
  kkr = makeIcon("kkr.png", iconWidth=36,iconHeight=36),
  mi = makeIcon("mi.png", iconWidth=36,iconHeight=36),
  pw = makeIcon("pw.png", iconWidth=36,iconHeight=36),
  rr = makeIcon("rr.png", iconWidth=36,iconHeight=36),
  rps = makeIcon("rps.png", iconWidth=36,iconHeight=36),
  rcb = makeIcon("rcb.png", iconWidth=36,iconHeight=36),
  sh = makeIcon("srh.png", iconWidth=36,iconHeight=36),
  t = makeIcon("draw.png", iconWidth=36,iconHeight=36)
)
```

  Now initialize the map and set the basemaps.
```
map <- leaflet(IPL) %>% 
  
  #overlay groups
  addTiles(group = "OSM (default)") %>%
  addProviderTiles("Esri.WorldGrayCanvas", group = "Esri.WorldGrayCanvas") %>%

```

  Next add markers and cluster options to the data and finally add overlay Controls.
```
addMarkers(data=IPL,icon=~teamIcons[IPL$sf], group = "IPL",popup = ~htmlEscape(paste(Match,"***",date,"***","Winner: ",Winner)),clusterOptions = markerClusterOptions()) %>%
  addMarkers(data=Matches_that_tied,icon=~teamIcons[Matches_that_tied$sf], group = "Matches_that_tied",popup = ~htmlEscape(paste(Match,"***",date,"***","Winner: ",Winner)),clusterOptions = markerClusterOptions()) %>%
  
  # Layers control
  addLayersControl(
    overlayGroups = c("OSM (default)", "Esri.WorldGrayCanvas"),
    baseGroups = c("IPL","Matches_that_tied"),
    options = layersControlOptions(collapsed = FALSE)
  )
```

#References
  1. http://nominatim.openstreetmap.org/search
  2. http://rstudio.github.io/leaflet/
