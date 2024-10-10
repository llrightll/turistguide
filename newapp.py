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
            {"role": "user", "content": f"hva kan man gjøre i oslo på {option} om man er interesert i {prompt}. tidsrommet for besøket er {dag}. aktuele nyheter om oslo som er formatert med strukturen title, description, content som du skal ha med i beregningen er {st.session_state['combined_articles']}. fortell også om en nyhetssak som er relevant"}
        ]
    )
    st.write(completion.choices[0].message.content)


def get_news():
    startdag = datetime.datetime.now() + datetime.timedelta(days=-10)
    all_articles = newsapi.get_everything(q='oslo', from_param='2024-09-29')

    if 'news_articles' not in st.session_state:
        st.session_state['news_articles'] = all_articles

    articles = st.session_state['news_articles'].get('articles', [])

    if 'combined_articles' not in st.session_state:
        st.session_state['combined_articles'] = []

    for article in articles:
        title = article.get('title', 'No title')
        description = article.get('description', 'No description')
        content = article.get('content', 'No content')

        combined = f"Title: {title}\n\nDescription: {description}\n\nContent: {content}\n{'-'*80}\n"

        #combined = f"Title: {title}\n\nDescription: {description}\n\nContent: {content}\n{'-'*80}\n"

        st.session_state['combined_articles'].append(combined)
    
    #for article in st.session_state['combined_articles']:
        #st.write(article)


if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True
    get_news()


st.write(st.session_state['combined_articles'])
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

if st.button("Guide me"):
    kall_guide()