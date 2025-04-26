from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_listing_with_places(self, latitude, longitude, places: list):
        with self.driver.session() as session:
            # Create or match the Listing node
            session.run("""
                MERGE (l:Listing {latitude: $lat, longitude: $lng})
            """, lat=latitude, lng=longitude)

            # Link each Place to the Listing
            for place in places:
                session.run("""
                    MERGE (p:Place {name: $name})
                    SET p.address = $address, p.type = $type, p.rating = $rating
                    WITH p
                    MATCH (l:Listing {latitude: $lat, longitude: $lng})
                    MERGE (l)-[:NEARBY]->(p)
                """,
                name=place["name"],
                address=place.get("vicinity", "Unknown"),
                type=place.get("place_type", "unknown"),
                rating=place.get("rating", 0),
                lat=latitude,
                lng=longitude)

