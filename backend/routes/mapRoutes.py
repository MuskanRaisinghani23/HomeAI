import requests
from fastapi import HTTPException, APIRouter
import configparser
from neo4j_client import Neo4jClient

config = configparser.ConfigParser()
config.read('configuration.properties')

api_key = config["GOOGLE-CLOUD"]["api_key"]
neo4j_client = Neo4jClient("bolt://76.152.120.193:7687", "neo4j", "neo4jtest")

router = APIRouter()

PLACE_TYPES = ["restaurant", "cafe", "park", "gym", "supermarket"]

def geocode_address(location):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address": location,
        "key": api_key
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            # Extract latitude and longitude
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            return lat, lng
        else:
            raise HTTPException(status_code=404, detail=f"Geocoding API request failed with status: {data['status']}")
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Geocoding API request failed with status code: {response.status_code}")

@router.get("/{location}")
def get_nearby_places(location: str):
    radius = 5000  
    latitude, longitude = geocode_address(location)

    all_places = []  

    for place_type in PLACE_TYPES:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": api_key,
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": place_type,
        }

        response = requests.get(url, params=params)
        print(f"Trying type: {place_type}")
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Google API returned status: {data.get('status')}")
            places_data = data.get("results", [])
            print(f"Found {len(places_data)} places for type {place_type}")
            for place in places_data:
                place["place_type"] = place_type
            all_places.extend(places_data)
        else:
            raise HTTPException(status_code=response.status_code, detail="API Error")

    neo4j_client.create_listing_with_places(latitude, longitude, all_places)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "places_count": len(all_places),
        "place_types": PLACE_TYPES
    }
   
@router.get("/nearby/{location}")
def get_nearby_places_for_listing(location:str):
    latitude, longitude = geocode_address(location)
    with neo4j_client.driver.session() as session:
        result = session.run("""
            MATCH (l:Listing {latitude: $lat, longitude: $lng})-[:NEARBY]->(p:Place)
            RETURN p.name AS name, p.address AS address, p.type AS type, p.rating AS rating
        """, lat=latitude, lng=longitude)

        places_by_type = {
            "restaurant": [],
            "cafe": [],
            "park": [],
            "gym": [],
            "supermarket": []
        }

        # Group places by type
        for record in result:
            place_type = record["type"]
            place_info = {
                "name": record["name"],
                "address": record["address"],
                "rating": record["rating"]
            }
            if place_type in places_by_type:
                places_by_type[place_type].append(place_info)

        for type_name, places in places_by_type.items():
            places.sort(key=lambda x: x["rating"] if x["rating"] is not None else 0, reverse=True)
            places_by_type[type_name] = places[:10]

    return {"nearby_places": places_by_type}
