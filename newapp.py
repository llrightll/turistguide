import streamlit as st
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from newsapi import NewsApiClient
import os

load_dotenv()
client = OpenAI(api_key = os.getenv("API_KEY"))
newsapi = NewsApiClient(api_key = os.getenv("NEWS_API_KEY"))

def kall_guide():
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [
            {"role": "system", "content": ("Du er en hyggelig turistguide i Oslo og omegn som gir lettleste tips til aktiviteter. Unngå nummererte lister. Bruk en vennlig, uformell og lokal tone som passer for turister i Oslo. Tilpass anbefalingene etter dato og tid på døgnet. Hvis tidspunktet er natt(ikke kveld), si på en vennlig måte at det beste nå er å hvile. Vurder kulturelle, historiske eller moderne attraksjoner basert på brukerens interesse. når du har nevnt steder, skriv en liste på slutten med koordinater for stedene. bruk formatet 'lokasjon, adresse, lat, long'. hvis du ikke har nøyaktig posjisjon, bruk nermeste beregning")},
            {"role": "user", "content": f"hva kan man gjøre i oslo på {option} om man er interesert i {prompt}. tidsrommet for besøket er {dag} "}
        ]
    )
    st.write(completion.choices[0].message.content)


def get_news():
    startdag = datetime.datetime.now() + datetime.timedelta(days=-10)
    all_articles = newsapi.get_everything(q='oslo', from_param=startdag)
    #st.write(all_articles)

st.title("Oslo turist guide")

st.write("Hei, hva kan jeg hjelpe med?")

get_news()

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

if st.button("Guide me"):
    kall_guide()