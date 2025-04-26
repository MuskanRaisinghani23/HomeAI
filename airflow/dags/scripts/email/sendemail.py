import configparser
from helper.snowflake_helper import snowflake_connection
import warnings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

warnings.filterwarnings("ignore")

config = configparser.ConfigParser()
config.read('dags/configuration.properties')

SMTP_SERVER = config["email"]["SMTP_SERVER"]
SMTP_PORT = config["email"]["SMTP_PORT"]
SMTP_USER = config["email"]["SMTP_USER"]
SMTP_PASSWORD = config["email"]["SMTP_PASSWORD"]


query = '''
WITH matched_listings AS (
  SELECT
    up.user_email,
    rl.LISTING_URL,
    rl.LOCATION,
    rl.PRICE,
    rl.ROOM_TYPE,
    rl.PEOPLE_COUNT,
    rl.DESCRIPTION_SUMMARY
  FROM user_preference up
  JOIN ROOMS_LISTINGS rl
    ON (up.MAXPRICE IS NULL OR rl.PRICE <= up.MAXPRICE)
  AND (up.room_type IS NULL OR rl.ROOM_TYPE = up.room_type)
  AND (up.LOCATION IS NULL OR rl.LOCATION = up.LOCATION)
  AND rl.LISTING_DATE BETWEEN current_date() - 5 AND current_date()
),
ranked_listings AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY PRICE ASC) AS rank
  FROM matched_listings
)
SELECT 
  user_email, 
  LISTING_URL, 
  LOCATION, 
  PRICE, 
  ROOM_TYPE, 
  PEOPLE_COUNT, 
  DESCRIPTION_SUMMARY
FROM ranked_listings
WHERE rank <= 5
ORDER BY user_email, rank;

'''

def fetchData():
  try:
    conn = snowflake_connection()
    cur = conn.cursor()
    print("-----------")
    query_result = cur.execute(query).fetchall()
    return query_result

  except Exception as e:
    print("Exception in fetchData function: ",e)
  finally:
    cur.close()
    conn.close()

def make_recommendations(recommendations):
  user_recommendations = {}
  for rec in recommendations:
    user_email = rec[0]
    listing_info = rec[1:]
    user_recommendations.setdefault(user_email, []).append(listing_info)

  return user_recommendations

def send_notification(recipient_email, listings):
  msg = MIMEMultipart()
  msg['From'] = SMTP_USER
  msg['To'] = recipient_email
  msg['Subject'] = "🏡 Your Top 5 Room Listings Today!"

  body = "Here are your matched listings:\n\n"
  for listing in listings:
    url, location, price, room_type, people_count, summary = listing
    body += f"🏠 {location} | {room_type} | {people_count} People | ${price}\n"
    body += f"Details: {summary}\n"
    body += f"Link: {url}\n\n"

  msg.attach(MIMEText(body, 'plain'))

  server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
  server.starttls()
  server.login(SMTP_USER, SMTP_PASSWORD)
  response = server.sendmail(SMTP_USER, recipient_email, msg.as_string())
  print(f"Email sent to {recipient_email}. Response: {response}")
  server.quit()

def send_email():
  recommendations = fetchData()
  user_recommendations = make_recommendations(recommendations)

  for user_email, listings in user_recommendations.items():
    send_notification(user_email, listings)
    print(f"Email sent to {user_email} with {len(listings)} listings.")