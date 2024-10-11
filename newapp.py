import streamlit as st
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from newsapi import NewsApiClient
import os
import sqlite3
import pandas as pd
import re
import requests

load_dotenv()
client = OpenAI(api_key = os.getenv("API_KEY"))
newsapi = NewsApiClient(api_key = os.getenv("NEWS_API_KEY"))
openweatherkey = os.getenv("OPEN_WEATHER_API")

def kall_guide(modell, natur, byliv, shopping, weather_data):
    
    completion = client.chat.completions.create(
        model=modell,
        messages=
        [
            {"role": "system", "content": ("Du er en hyggelig turistguide i Oslo og omegn som gir lettleste tips til aktiviteter. Unngå nummererte lister. Bruk en vennlig, uformell og lokal tone som passer for turister i Oslo. Tilpass anbefalingene etter dato og tid på døgnet. Hvis tidspunktet er natt(ikke kveld), si på en vennlig måte at det beste nå er å hvile. Vurder kulturelle, historiske eller moderne attraksjoner basert på brukerens interesse.")},
            {"role": "user", "content": f"hva kan man gjøre i oslo på {option} om man er interesert i {prompt}. tidsrommet for besøket er {dag}. på en skala fra 0-3 er det {natur}interesse for natur,{byliv} interesse for byliv, {shopping} interesse for shopping. aktuele nyheter om oslo som er formatert med strukturen title, description, content som du skal ha med i beregningen er {st.session_state['combined_articles']}. fortell også om en nyhetssak som er relevant for tidspunktet som er satt og/eller interessen. Vennligst unngå å nevne Nobelprisen med mindre brukerens interesse er knyttet til det. unngå nummererte lister. bruk informasjon om været: {weather_data} "}
        ]
    )

    koordinater = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [
            {"role": "system", "content": ("du finner steder fra teksten og du skriver en liste over steder med koordinater i formatet: Stednavn: (lat, lon). Hvis du ikke har nøyaktig posisjon, gi nærmeste beregning.")},
            {"role": "user", "content": f"{completion.choices[0].message.content}"}
        ]
    )
    response_content = completion.choices[0].message.content
    st.write(response_content)

    # Extract coordinates from the response content
    coordinates = extract_coordinates(koordinater.choices[0].message.content)
    
    # If coordinates are found, create a DataFrame and display the map
    if coordinates:
        df = pd.DataFrame(coordinates, columns=["lat", "lon"])
        st.map(df)

def extract_coordinates(response_content):
   
    # Example regex to find latitude and longitude pairs
    pattern = r"\(([-+]?\d*\.\d+), ([-+]?\d*\.\d+)\)"
    matches = re.findall(pattern, response_content)

    # Convert matches to float and create a list of tuples
    coordinates = [(float(lat), float(lon)) for lat, lon in matches]

    return coordinates


def get_news():
    today_start = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
    all_articles = newsapi.get_everything(q='oslo', from_param=today_start)

    articles = all_articles.get('articles', [])

    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            content TEXT
        )
    ''')

    if 'combined_articles' not in st.session_state:
        st.session_state['combined_articles'] = []

    for article in articles:
        title = article.get('title', 'No title')
        description = article.get('description', 'No description')
        content = article.get('content', 'No content')

        cursor.execute("SELECT COUNT(*) FROM news WHERE title = ?", (title,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                    INSERT INTO news (title, description, content)
                    VALUES (?, ?, ?)
                ''', (title, description, content))

        combined = f"Title: {title}\n\nDescription: {description}\n\nContent: {content}\n{'-'*80}\n"
        st.session_state['combined_articles'].append(combined)

    if 'news_articles' not in st.session_state:
        st.session_state['news_articles'] = all_articles

    conn.commit()
    conn.close()
    

def fetch_news_from_db():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT title, description, content FROM news")
    articles = cursor.fetchall()

    conn.close()

    if 'combined_articles' not in st.session_state:
        st.session_state['combined_articles'] = []

    st.session_state['combined_articles'] = []

    for article in articles:
        title, description, content = article
        combined = f"Title: {title}\n\nDescription: {description}\n\nContent: {content}\n{'-'*80}\n"
        st.session_state['combined_articles'].append(combined)

    #st.write(st.session_state['combined_articles'])


if 'combined_articles' not in st.session_state: 
    fetch_news_from_db()

base_url = "https://api.openweathermap.org/data/2.5/weather"
city = "oslo"
params = {
    'q': city,
    'appid': openweatherkey,
    'units': 'metric',
    'exclude': 'hourly,minutely'
}


wresponse = requests.get(base_url, params=params)
weather_data = wresponse.json()
#st.json(weather_data) 

st.title("Oslo turist guide")
st.write("Hei, hva kan jeg hjelpe med?")

today = datetime.datetime.now()
day4 = today + datetime.timedelta(days=4)
dec_31 = datetime.date(today.year + 3, 12, 31)

dag = st.date_input(
    "Når er du i Oslo?",
    (today, day4),
    today,
    dec_31,
    format="DD.MM.YYYY"
)

option = st.selectbox(
    "Når på dagen?",
    ("Morgen", "Dag", "Kveld", "Natt")
)

prompt = st.text_input("Hva er din interesse?")

modell = st.sidebar.selectbox(
    "modell",
    ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo")
)

natur = st.sidebar.slider(
    "natur",
    0, 3, 0
)

byliv = st.sidebar.slider(
    "byliv",
    0, 3, 0
)

shopping = st.sidebar.slider(
    "shopping",
    0, 3, 0
)

if st.button("Guide me"):
    kall_guide(modell, natur, byliv, shopping, weather_data)

if st.sidebar.button("hent nyheter"):
    get_news()

if st.sidebar.button("Show Database Contents"):
    st.sidebar.write(st.session_state['combined_articles'])

#thumbs = st.feedback("thumbs")

st.sidebar.image("Image.png")

