# HomieAI
HomieAI is built to make the process of finding budget-friendly shared housing easier and more organized. Right now, most people rely on scattered WhatsApp groups and Facebook Marketplace, which can be messy and time-consuming. This project aims to bring everything into one place for a smoother and more efficient experience.

[![Codelab Documentation](https://img.shields.io/badge/codelabs-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=12itBNmCPvDPGoQZRLQj9TXRsB-O6feUUO2VdW6u5b6E#0)

## Live application link

[![Demo](https://img.shields.io/badge/Demo_Link-808080?style=for-the-badge&logoColor=white)](http://76.152.120.193:4173/)

## Technologies Used
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=for-the-badge&logo=Snowflake&logoColor=white)](https://www.snowflake.com/)
[![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)](https://airflow.apache.org/)
[![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=Apache%20Spark&logoColor=white)](https://spark.apache.org/docs/latest/api/python/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white)](https://www.docker.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=for-the-badge&logo=Neo4j&logoColor=white)](https://neo4j.com/)
[![Tableau](https://img.shields.io/badge/Tableau-E97627?style=for-the-badge&logo=Tableau&logoColor=white)](https://www.tableau.com/)
[![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)

**Challenge:**
Searching for a room today means bouncing between WhatsApp chats, Facebook Marketplace posts, and inconsistent Craigslist listings. Messages are often outdated, unstructured, and impossible to filter by what matters most—budget, room type, or location. This chaotic and inefficient system causes frustration and missed opportunities for users.

**Solution:**
HomeAI transforms this disorganized process into a centralized, smart platform. By scraping data from major sources, structuring it into a clean database, and enabling intelligent search and filters, HomeAI saves users time, energy, and uncertainty. Early career professionals, interns, and those seeking short-term housing can now find the perfect room, faster and easier.

## Architecture

![Architecture Diagram](screenshots/architecture.jpg)

**Key Components:**
- **Data Scraping:** Marketplace, Craigslist, WhatsApp chat exports
- **ETL Pipelines:** Airflow orchestrates PySpark transformations and Snowflake loads
- **Database:** Listings stored in Snowflake
- **API Backend:** FastAPI serves room listing APIs
- **Frontend:** React-based application for user interaction
- **Analytics & Graphs:** Neo4j for relationship graphs, Tableau for visual insights
- **Deployment:** Dockerized services deployed on AWS


## Features

- Smart search based on location, budget, room type, and amenities
- Personalized room recommendations based on user preferences
- Relationship graph between listings, locations, and nearby amenities (Neo4j)
- Real-time listing updates with scraping pipelines
- Interactive data analytics dashboards for insights (Tableau)
- Secure user authentication (FastAPI + Snowflake)
- Responsive, mobile-friendly UI (React)

## Project Tree

```
📦 
├─ .gitignore
├─ README.md
├─ airflow
│  ├─ .env.example
│  ├─ .gitignore
│  ├─ .gitkeeper
│  ├─ airflowimage
│  │  └─ Dockerfile
│  ├─ dags
│  │  ├─ craigslist_data_dag.py
│  │  ├─ email_notification_dag.py
│  │  ├─ facebook_metadata_dag.py
│  │  ├─ helper
│  │  │  └─ snowflake_helper.py
│  │  ├─ scripts
│  │  │  ├─ craigslist
│  │  │  │  ├─ load_listings.py
│  │  │  │  └─ transform_listings.py
│  │  │  ├─ email
│  │  │  │  └─ sendemail.py
│  │  │  ├─ facebook
│  │  │  │  ├─ load_data.py
│  │  │  │  └─ transform_data.py
│  │  │  └─ whatsapp
│  │  │     └─ load_data.py
│  │  ├─ spark
│  │  │  ├─ craigslist
│  │  │  │  └─ extract_listing.py
│  │  │  ├─ facebook
│  │  │  │  ├─ extract_listing.py
│  │  │  │  ├─ extract_metadata.py
│  │  │  │  └─ transform_listing.py
│  │  │  └─ whatsapp
│  │  │     ├─ extract_listing.py
│  │  │     └─ transform_listing.py
│  │  └─ whatsapp_data_dag.py
│  ├─ docker-compose.yaml
│  ├─ requirements.txt
│  └─ sparkimage
│     └─ Dockerfile
├─ backend
│  ├─ Dockerfile
│  ├─ connections.py
│  ├─ docker-compose.yml
│  ├─ main.py
│  ├─ neo4j_client.py
│  ├─ requirements.txt
│  └─ routes
│     ├─ authRoutes.py
│     ├─ listingRoutes.py
│     ├─ mapRoutes.py
│     └─ preferenceRoute.py
├─ homeAI-app
│  ├─ .gitignore
│  ├─ Dockerfile
│  ├─ README.md
│  ├─ docker-compose.yml
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  ├─ logo.jpg
│  │  └─ vite.svg
│  ├─ src
│  │  ├─ App.css
│  │  ├─ App.jsx
│  │  ├─ STATE_CITY_MAP.jsx
│  │  ├─ assets
│  │  │  ├─ background.jpg
│  │  │  ├─ logo.jpg
│  │  │  └─ react.svg
│  │  ├─ components
│  │  │  ├─ ListingCard.jsx
│  │  │  ├─ LoginSIgnup.jsx
│  │  │  ├─ Navbar.jsx
│  │  │  ├─ NearbyPlaces.jsx
│  │  │  ├─ PreferenceListingsChat.css
│  │  │  ├─ PreferenceListingsChat.jsx
│  │  │  ├─ PreferencesWizard.css
│  │  │  ├─ PreferencesWizard.jsx
│  │  │  └─ styles.css
│  │  ├─ index.css
│  │  └─ main.jsx
│  └─ vite.config.js
├─ requirements.txt
├─ screenshots
│  ├─ architecture.jpg
│  └─ dashboard.png
├─ snowflake_setup
│  ├─ procedure_setup.sql
│  ├─ stages_setup.sql
│  ├─ tables_setup.sql
│  └─ tasks_setup.sql
└─ web_driver
   └─ docker-compose.yaml
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)

## Application UI

**Filter and Select - Get Listings or Find Nearby Hotspots**  

![Alt text](screenshots/FilterAndSelect.png)

**Get matched listings based on your preferences**  

![Alt text](/screenshots/Listings.png)

**Find Restaurants, Cafes, Gym, Supermarkets and Park for your preferred location**  

![Alt text](/screenshots/NearbyPlaces.png)

## Relationship Graph with Neo4j

HomeAI uses Neo4j to map listings to nearby places like parks, cafes, gyms, and restaurants. This enables users to search not just for rooms, but for neighborhoods that match their lifestyle preferences.

![Alt text](/screenshots/Graph.png)

Listings (:Listing nodes) are connected to nearby amenities (:Place nodes) using :NEARBY relationships. Each Place node stores structured properties like name, address, rating, and type, enabling graph-based contextual search and filtering.

![Alt text](/screenshots/Graph2.png)

## 📊 Analytics 

![Tableau](screenshots/dashboard.png)

## Future Enhancements
- Allow user-contributed reviews
- Implement advanced filters (pet-friendly, furnished, lease duration)
- Geo-search for nearby attractions and commute times

## 👥 Authors

- **Monil Shah** 
- **Muskan Deepak Raisinghani** 
- **Rachana Keshav** 


Built with passion to simplify room hunting! 🏡💜


