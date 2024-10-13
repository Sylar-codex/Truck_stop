import pandas as pd

import requests
import os
from django.conf import settings
from opencage.geocoder import OpenCageGeocode
from functools import reduce




def normalize_city_name(city_name):
    abbreviation_mapping = {
    "St.": "Saint",
    "Mt.": "Mount",
    "Pk." :"Park",
    "Ft." : "Fort"
}
    city_name = city_name
    # Replace abbreviations with full names
    for abbr, full_name in abbreviation_mapping.items():
        city_name = city_name.replace(abbr, full_name)
    return city_name


class TruckStops :
    key = settings.OPENCAGE_API_KEY
    loc_key = settings.LOCATION_ACCESS
    
    # ensure they ar within the US
    bounds = ("-180.00000","-14.76084","180.00000","71.58895")

    geocoder = OpenCageGeocode(key)

    def get_routes(self, start, finish) :        
        start_cord = self.geocoder.geocode(start, bounds=self.bounds)

        finish_cord= self.geocoder.geocode(finish,bounds=self.bounds)

        start_lat,start_lng = start_cord[0]['geometry']['lat'], start_cord[0]['geometry']['lng']
        finish_lat, finish_lng = finish_cord[0]['geometry']['lat'], finish_cord[0]['geometry']['lng']


        # lng and lat
        req_url = f'https://us1.locationiq.com/v1/directions/driving/{start_lng},{start_lat};{finish_lng},{finish_lat}?key={self.loc_key}&geometries=geojson'
        headers = {"accept": "application/json"}
        res  = requests.get(req_url, headers=headers)
        data = res.json()
        print(data['routes'][0]['duration'])
        coordinates= [cord for cord in data['routes'][0]['geometry']['coordinates']]
        return {"city_routes":self.get_cities(coordinates),
                "distance":data['routes'][0]['distance'],
                "duration":data['routes'][0]['duration']
                }

    def get_cities(self,coordinates) :
        cities = []
        for coordinate in coordinates :
            components = self.geocoder.reverse_geocode(coordinate[1],coordinate[0])
            try :
                 cities.append(components[0]['components']['_normalized_city'])
            except KeyError:
                pass
        return self.get_fuel_stops(cities)         

    def get_fuel_stops(self,cities) :
        file_path = os.path.join(settings.BASE_DIR, 'fuelstops', 'fuel-prices-for-be-assessment.csv')
        fuel_prices_df = pd.read_csv(file_path)
        stops = []
        for city in cities :
            city_stations = fuel_prices_df[fuel_prices_df['City'] == normalize_city_name(city)]
            city_routes = {}
            if not city_stations.empty :
                # find station with least price
                cheapest_station = city_stations.sort_values(by="Retail Price").iloc[0]
                city_routes['name'] = city
                city_routes['station'] = cheapest_station
                stops.append(city_routes)
        return stops



def get_total_amount(stops) :

    # max range of 500 miles, 10 miles per gallon will 50 gallons for the trip
    total_amount = reduce(lambda prev, current : prev + current['station']['Retail Price'],stops,0)
    return total_amount * 50

