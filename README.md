# HomieAI
HomieAI is built to make the process of finding budget-friendly shared housing easier and more organized. Right now, most people rely on scattered WhatsApp groups and Facebook Marketplace, which can be messy and time-consuming. This project aims to bring everything into one place for a smoother and more efficient experience.

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

## 📊 Architecture

![Architecture Diagram](assets/architecture.png)

**Key Components:**
- **Data Scraping:** Marketplace, Craigslist, WhatsApp chat exports
- **ETL Pipelines:** Airflow orchestrates PySpark transformations and Snowflake loads
- **Database:** Listings stored in Snowflake
- **API Backend:** FastAPI serves room listing APIs
- **Frontend:** React-based application for user interaction
- **Analytics:** Neo4j for relationship graphs, Tableau for visual insights
- **Deployment:** Dockerized services deployed on AWS

## 🔹 Codelab

Coming soon!

## 🔠 Project Structure

```
# Placeholder - to be added
```

---

Built with passion to simplify room hunting! 🏡💜

