import certifi
import os
os.environ["SSL_CERT_FILE"] = certifi.where()
from django.shortcuts import render, redirect
from django.http import JsonResponse
from pymongo import MongoClient
import base64
from io import BytesIO
from PIL import Image
from .models import Location
from .models import ChatHistory
from django.http import HttpRequest
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from dotenv import load_dotenv
from django.views.decorators.http import require_http_methods
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import logging
import urllib3.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import time
import re
from bson import json_util
from datetime import datetime, timedelta
from django.core.paginator import Paginator
load_dotenv()  



def get_images_centru_civic(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    
    db = client["maps"]
    
    colectie = db["CC"]

    imagini = list(colectie.find({}, {'_id': 0}))

    for imagine in imagini:
        imagine['imagine'] = base64.b64encode(imagine['imagine']).decode('utf-8')

    client.close()

    return JsonResponse({'imagini': imagini})

def get_images_centru_vechi(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    colectie = db["CV"]

    imagini = list(colectie.find({}, {'_id': 0}))

    for imagine in imagini:
        imagine['imagine'] = base64.b64encode(imagine['imagine']).decode('utf-8')

    client.close()

    return JsonResponse({'imagini': imagini})

def harta(request):
    locations = Location.objects.all()
    return render(request, 'map/harta.html', {'locations': locations})
    

def streetview(request):
    locations = Location.objects.all()
    return render(request, 'map/streetview.html', {'locations': locations})








def aula(request: HttpRequest):
    url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
    base_url = 'https://www.unitbv.ro'
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
   
    db = client["maps"]
    news_collection = db["aula"]
    search_query = request.GET.get('q', '')

    if search_query:
        filtered_articles = news_collection.find({
            '$or': [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        }).sort("published_date", -1)
    else:
        filtered_articles = news_collection.find().sort("published_date", -1)

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='item')

        for article in articles:
            title_element = article.find('h5', class_='item_title')
            description_element = article.find('div', class_='item_introtext')
            image_element = article.find('img')
            if title_element and description_element and image_element:
                title = title_element.text.strip()
                description = description_element.text.strip()
                image_url = urljoin(base_url, image_element['src'])
                article_url = urljoin(base_url, article.find('a')['href'])
                existing_article = news_collection.find_one({'article_url': article_url})
                if image_url and not existing_article:
                    published_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    article_data = {
                        'title': title,
                        'article_url': article_url,
                        'image_url': image_url,
                        'description': description,
                        'published_date': published_date,
                    }
                    try:
                        news_collection.insert_one(article_data)
                    except Exception as e:
                        print(f"Eroare la inserarea datelor: {str(e)}")

    articole_list = list(filtered_articles)

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = None
    else:
        selected_date = None

    context = {'articole': articole_list, 'search_query': search_query, 'selected_date': selected_date}
    client.close()

    return render(request, 'map/aula.html', context)



@require_http_methods(["GET"])
def events_by_date_aula(request):
    load_dotenv()
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    
    db = client["maps"]
    news_collection = db["aula"]

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day)
        except ValueError:
            selected_datetime = None
    else:
        selected_datetime = None

    if selected_datetime:
        events = list(news_collection.find({'published_date': selected_datetime}))
        formatted_events = [
            {
                'title': event['title'],
                'published_date': event['published_date'].strftime("%Y-%m-%d")
            }
            for event in events
        ]
    else:
        formatted_events = []

    client.close()
    return render(request, 'map/events_by_date_aula.html', {'events': formatted_events, 'selected_date': selected_date})







@require_http_methods(["GET"])
def data_aula(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    news_collection = db["aula"]

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_of_day = datetime.combine(selected_date, datetime.min.time())
            end_of_day = datetime.combine(selected_date, datetime.max.time())
        except ValueError:
            start_of_day = None
            end_of_day = None
    else:
        start_of_day = None
        end_of_day = None

    if start_of_day and end_of_day:
        events = list(news_collection.find({
            'published_date': {
                '$gte': start_of_day,
                '$lt': end_of_day
            }
        }))
        
        formatted_events = [
            {
                'title': event['title'],
                'article_url': event['article_url'],
                'description': event['description'],
                'image_url': event['image_url'],
                'published_date': event['published_date'].strftime("%Y-%m-%d")
            }
            for event in events
        ]
    else:
        formatted_events = []

    client.close()
    return JsonResponse({'events': formatted_events})



def primaria(request: HttpRequest):
    url = 'https://cultura.brasovcity.ro/category/evenimente-culturale-ro/'
    article_data = []
    base_url = 'https://cultura.brasovcity.ro'
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    news_collection = db["primaria"]
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.post')

        existing_article_urls = set(news_collection.distinct('article_url'))

        for article in articles:
            title_element = article.select_one('h1.entry-title')
            image_element = article.select_one('img.thumbnail')
            description_element = article.select_one('div.entry-summary')

            if title_element and image_element and description_element:
                title = title_element.text.strip()
                image_url = urljoin(base_url, image_element['src'])
                description = description_element.text.strip()
                article_url = title_element.select_one('a')['href'] if title_element.select_one('a') else None

                
                if article_url not in existing_article_urls:
                        article_data.append({
                            'title': title,
                           
                            'image_url': image_url,
                            'description': description,
                            'article_url': article_url
                        })
                        existing_article_urls.add(article_url)
                   

        if article_data:
            news_collection.insert_many(article_data)

        articole = news_collection.find()
        client.close()
        articole_list = list(articole)
        return render(request, 'map/primaria.html', {'articole': articole_list})



def get_all_events(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client.maps 
    events_collection = db.aula 
    primaria_collection = db.primaria  

    events = events_collection.find({})
    primaria_events = primaria_collection.find({}) 

    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get ("image_url","")} for event in events]
    primaria_events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"),"image_url": event.get ("image_url","")} for event in primaria_events]

    client.close()

    # combine the event lists from both collections
    combined_events_list = events_list + primaria_events_list

    return JsonResponse({'events': combined_events_list})




def cinema_city(request):
    url = 'https://www.cinemacity.ro/#/buy-tickets-by-cinema?in-cinema=1829&at=2024-05-27&view-mode=list'
    movie_data = []

    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    movies_collection = db["cinemacity"]

    # configure options for Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service('C:/Users/rusuv/Desktop/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)
        time.sleep(10)  # Wait for the initial page load

        # Wait until the movie containers are present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.row.qb-movie')))

        # Get the page source HTML
        html_source = driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')
        movie_containers = soup.find_all('div', class_='row qb-movie')

        for movie_container in movie_containers:
            # Extract the movie title and link
            title_link_element = movie_container.find('a', class_='qb-movie-link')
            title = title_link_element.find('h3').text.strip() if title_link_element else "Titlu indisponibil"
            movie_link = title_link_element['href'] if title_link_element else None

            # movie description
            description_element = movie_container.find('div', class_='qb-movie-info-wrapper')
            description_text = description_element.find('div', class_='pt-xs').text.strip() if description_element else "Descriere indisponibilă"
            genres, duration = (description_text.split('|') + [""])[:2]
            description = f"{genres.strip()} - {duration.strip()}"

            # link to the poster image
            poster_link = movie_container.find('div', class_='movie-poster-container')
            if poster_link:
                poster_img = poster_link.find('img')
                if poster_img:
                    poster_link = poster_img.get('data-src') or poster_img.get('src')
                else:
                    poster_link = None
            else:
                poster_link = None

            print(poster_link)
            
            showtime_elements = movie_container.find_all('a', class_='btn btn-primary btn-lg')
            showtimes = [showtime_element.text.strip() for showtime_element in showtime_elements]

           
            movie_data.append({
                'title': title,
                'description': description,
                'poster_link': poster_link,
                'showtimes': showtimes,
                'movie_link': movie_link
            })

            # Insert/update data in MongoDB
            movies_collection.update_one(
                {'title': title},
                {'$set': {
                    'title': title,
                    'description': description,
                    'poster_link': poster_link,
                    'showtimes': showtimes,
                    'movie_link': movie_link
                }},
                upsert=True
            )

    finally:
        driver.quit()

    movies = list(movies_collection.find())
    client.close()

    return render(request, 'map/cinema_city.html', {'movies': movies})






def events_aula(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    aula_collection = db["aula"] 

    events = aula_collection.find({})
    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get("image_url","")} for event in events]

    client.close()
    return JsonResponse({'events': events_list})

def events_primaria(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    primaria_collection = db["primaria"] 

    events = primaria_collection.find({})
    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get("image_url","")} for event in events]

    client.close()
    return JsonResponse({'events': events_list})

def events_teatru(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    teatru_collection = db["teatru"]

    events = teatru_collection.find({}, {'_id': 0})
    events_list = [{"title": event["title"], "author": event["author"], "date_time": event["date_time"], "title_link": event["title_link"], "image_url":event["image_url"]} for event in events]

    client.close()
    return JsonResponse({'events': events_list})


def events_filme(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    movies_collection = db["cinemacity"]

    events = movies_collection.find({}, {'_id': 0})
    events_list = [{"title": event["title"], "description": event["description"], "showtimes": event["showtimes"], "movie_link": event["movie_link"], "poster_link": event["poster_link"]} for event in events]

    client.close()
    return JsonResponse({'events': events_list})



@csrf_exempt
def chat_with_mistral(request):
    load_dotenv()
    response_content = ""
    if request.method == 'POST':
    
        user_input = request.POST.get('message', '')
        if not user_input:
            return render(request, 'map/harta.html', {'error': 'Nu a fost furnizată nicio intrare'})

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return render(request, 'map/harta.html', {'error': 'Cheia API Mistral nu a fost găsită'})

        client = MistralClient(api_key=api_key)
        model = "mistral-large-latest"

        
        MONGODB_URI = os.environ.get('MONGODB_URI')
        mongo_client = MongoClient(MONGODB_URI)
        db = mongo_client.maps
        collections = {
            "cinemacity": db.cinemacity,
            "aula": db.aula,
            "primaria": db.primaria,
            "teatru": db.teatru
        }
        response_content = "Ne pare rău, nu am înțeles întrebarea ta. Poți încerca să reformulezi sau să adresezi o altă întrebare."
# Locatia pe harta a filmului unde se poate de uitat
# UNde pot vedea filmul garfield?        

# Intreaga colectie de filme:
# Ce filme sunt?
        
# Recomandare de filme in functie de gen:
# "Recomandă-mi filme de comedie"

# Interogare despre filmele care rulează în prezent:
# "Ce filme rulează acum?"

# Cautare filme după categorie:
# "Ce filme din categoria thriller sunt acum?"

# Detalii despre un anumit film:
# "Detalii despre filmul Garfield"



# Trailer pentru un anumit film:
# "Arata-mi trailer-ul pentru filmul Prieteni imaginari"

# Durata unui film:
# "Cât durează filmul Gardienii planetei?"


# Recomandari de filme similare:
# "Recomandă-mi filme similare cu Furiosa"


        
        if re.search(r'unde pot (vedea|viziona) filmul', user_input.lower()):
          
            
            movie_title_match = re.search(r'unde pot (?:vedea|viziona) filmul\s+(.*)', user_input.lower())
            if movie_title_match:
                movie_title = movie_title_match.group(1)
                chat_history = ChatHistory.objects.all().order_by('-created_at')
                movie = collections["cinemacity"].find_one({"title": {"$regex": movie_title, "$options": "i"}})
                if movie:
                    response_content = f"Filmul '{movie['title']}' poate fi vizionat la Cinema City, Cinema One și Eliana Mall. Locațiile sunt indicate pe hartă."



                    cinema_locations = {
                    'Cinema City': [45.65027328171806, 25.61105450714932],
                    'Cinema One': [45.67304981680509, 25.61427215362855],
                    'Eliana Mall': [45.65766218042808, 25.56141399964052]
                     }
                    #cinema_city_coords = [45.65027328171806, 25.61105450714932] # Coordonatele corecte ale Cinema City
                    return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input, 'cinema_locations': cinema_locations})
                    # return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input, 'cinema_city_coords': cinema_city_coords})
                else:
                    response_content = f"Ne pare rău, nu am găsit filmul '{movie_title}' în programul Cinema City."
                   

        elif re.search(r'(ce filme (sunt|disponibile|există)|(filme|ce) (rulează|ruleaza) acum)', user_input.lower()):
            current_date = datetime.now().strftime("%Y-%m-%d")
            cinema_movies = list(collections["cinemacity"].find({"showtimes": {"$exists": True, "$ne": []}}))
            if cinema_movies:
                movie_list = "\n".join([f"- {movie['title']} ({movie['description']})" for movie in cinema_movies])
                response_content = f"Filmele care rulează acum la Cinema City sunt:\n{movie_list}"
            else:
                response_content = "Nu am găsit informații despre filmele care rulează acum la Cinema City."

        elif re.search(r'recomand(ă|a|)', user_input.lower()):
            genre_match = re.search(r'comedie|horror|acțiune|actiune|aventură|aventura|ficțiune|fictiune|thriller|animație|animatie|dramă|drama|documentar|fantastic', user_input.lower())
            if genre_match:
                genre = genre_match.group().capitalize().replace("ă", "a").replace("ț", "t").replace("ș", "s")
                cinema_movies = list(collections["cinemacity"].find({"description": {"$regex": genre}}))
                if cinema_movies:
                    movie_recommendations = [f"- {movie['title']} ({movie['description']})\nLink: {movie['movie_link']}" for movie in cinema_movies[:3]]
                    response_content = f"Iată câteva recomandări de filme din categoria '{genre}':\n" + "\n".join(movie_recommendations)
                else:
                    response_content = f"Ne pare rău, nu am găsit recomandări de filme din categoria '{genre}'."
            else:
                response_content = "Te rog specifică o categorie de filme (de exemplu: comedie, acțiune, dramă) pentru a primi recomandări."







        
        elif re.search(r'(ce filme (sunt||există)|(filme|ce) (categorie|categoria))', user_input.lower()):
            genre_match = re.search(r'comedie|horror|acțiune|actiune|aventură|aventura|ficțiune|fictiune|thriller|animație|animatie|dramă|drama|documentar|fantastic', user_input.lower())
            if genre_match:
                genre = genre_match.group().capitalize().replace("ă", "a").replace("ț", "t").replace("ș", "s")
                cinema_movies = list(collections["cinemacity"].find({"description": {"$regex": genre}}))
                if cinema_movies:
                    movie_recommendations = [f"- {movie['title']} ({movie['description']})\nLink: {movie['movie_link']}" for movie in cinema_movies[:3]]
                    response_content = f"Iată filme din categoria '{genre}':\n" + "\n".join(movie_recommendations)
                else:
                    response_content = f"Ne pare rău, nu am găsit filme din categoria '{genre}'."
          






        elif re.search(r'(rulează|ruleaza) acum', user_input.lower()):
                cinema_movies = list(collections["cinemacity"].find())
                if cinema_movies:
                    movie_titles = [f"- {movie['title']} ({movie['description']})" for movie in cinema_movies]
                    response_content = "Filmele disponibile acum la Cinema City sunt:\n" + "\n".join(movie_titles)
                else:
                    response_content = "Ne pare rău, nu am găsit informații despre filmele care rulează acum."

        
        elif re.search(r'detalii', user_input.lower()):
            movie_match = re.search(r'detalii despre filmul\s+(.+)', user_input.lower())
            if movie_match:
                movie_title = movie_match.group(1)
                movie = collections["cinemacity"].find_one({"title": {"$regex": f"^{re.escape(movie_title)}$", "$options": "i"}})
                if movie:
                    response_content = f"Detalii despre filmul '{movie['title']}':\n"
                    response_content += f"- Titlu: {movie['title']}\n"
                    response_content += f"- Descriere: {movie['description']}\n"
                    response_content += f"- Link trailer: {movie.get('movie_link', 'N/A')}\n"
                    
                else:
                    similar_movies = list(collections["cinemacity"].find({"title": {"$regex": movie_title, "$options": "i"}}, {"title": 1, "_id": 0}).limit(3))
                    if similar_movies:
                        movie_suggestions = [movie["title"] for movie in similar_movies]
                        response_content = f"Ne pare rău, nu am găsit detalii despre filmul '{movie_title}'. "
                        response_content += f"Iată câteva sugestii de filme similare:\n- " + "\n- ".join(movie_suggestions)
                        response_content += "\n\nPentru a obține detalii despre unul dintre aceste filme, te rog specifică titlul exact al filmului."
                    else:
                        response_content = f"Ne pare rău, nu am găsit detalii despre filmul '{movie_title}'. "
                        response_content += "Te rugăm să verifici dacă ai introdus corect titlul filmului sau încearcă să cauți un alt film."
            else:
                response_content = "Te rog specifică un film pentru a obține detalii, folosind formatul 'Detalii despre filmul [Numele Filmului]'."

     
        elif re.search(r'trailer', user_input.lower()):
            movie_match = re.search(r'trailer (pentru|la)\s+(.+)', user_input.lower())
            if movie_match:
                movie_title = movie_match.group(2)
                movie = collections["cinemacity"].find_one({"title": {"$regex": movie_title, "$options": "i"}})
                if movie:
                    response_content = f"Trailer-ul pentru filmul '{movie['title']}' ar trebui să fie disponibil aici: {movie['movie_link']}"
                else:
                    response_content = f"Ne pare rău, nu am găsit filmul '{movie_title}' în baza de date."
            else:
                response_content = "Te rog specifică un film pentru a obține link-ul către pagina unde s-ar putea găsi trailer-ul (de exemplu: 'trailer pentru Numele Filmului')."
            
        elif re.search(r'similar', user_input.lower()):
                movie_match = re.search(r'similar[ea]?\s+cu\s+(.+)', user_input.lower())
                if movie_match:
                    movie_title = movie_match.group(1)
                    movie = collections["cinemacity"].find_one({"title": {"$regex": movie_title, "$options": "i"}})
                    if movie:
                        genres = re.findall(r'\b(?:Comedie|Horror|Acțiune|Aventură|Ficțiune|Thriller|Animație|Dramă|Documentar|Fantastic)\b', movie['description'])
                        similar_movies = list(collections["cinemacity"].find({"description": {"$regex": "|".join(genres), "$options": "i"}}))
                        similar_movies = [m for m in similar_movies if m['_id'] != movie['_id']]
                        if similar_movies:
                            movie_recommendations = [f"- {m['title']} ({m['description']})" for m in similar_movies[:3]]
                            response_content = f"Filme similare cu '{movie['title']}':\n" + "\n".join(movie_recommendations)
                        else:
                            response_content = f"Ne pare rău, nu am găsit filme similare cu '{movie['title']}'."
                    else:
                        response_content = f"Ne pare rău, nu am găsit filmul '{movie_title}'."
                else:
                    response_content = "Te rog specifică un film pentru a primi recomandări similare (de exemplu: 'filme similare cu Numele Filmului')."
   
         

# Afișarea tuturor evenimentelor și anunțurilor
#Ce evenimente sunt la aula?"

# afisarea festivalurilor
#Ce festivaluri sunt la aula?

# ce concerte sunt la aula
# ce expozitii sunt la aula
# ce conferinte sunt la aula 
# ce concursuri sunt la aula



        #   # Scenariul 1: Afișarea tuturor evenimentelor și anunțurilor


        elif re.search(r'(aula|universitate|facultate|stiri|unitbv)', user_input.lower()):
            if re.search(r'evenimente', user_input.lower()):
                events = list(collections["aula"].find())
                if events:
                    event_list = "\n".join([f"- {event['title']} ({event['description']})" for event in events])
                    response_content = f"Evenimentele și anunțurile de la Aula Universității sunt:\n{event_list}"
                else:
                    response_content = "Nu am găsit evenimente sau anunțuri în acest moment."

            elif re.search(r'(ce|care|cand|unde).*\bconferinte.*\b(aula|universitate)', user_input.lower()):
                conferences = list(collections["aula"].find({"$or": [
                    {"title": {"$regex": "conferinta|conference|congress|simpozion", "$options": "i"}},
                    {"description": {"$regex": "conferinta|conference|congress|simpozion", "$options": "i"}}
                ]}))
                if conferences:
                    conference_list = "\n".join([f"- {conference['title']} ({conference['description']})" for conference in conferences])
                    response_content = f"Conferințele programate la Aula Universității sunt:\n{conference_list}"
                else:
                    response_content = "Nu am găsit conferințe programate la Aula Universității."

            elif re.search(r'(ce|care|cand|unde).*\bexpozitii.*\b(aula|universitate)', user_input.lower()):
                exhibitions = list(collections["aula"].find({"$or": [
                    {"title": {"$regex": "expozitie|exhibition|expo", "$options": "i"}},
                    {"description": {"$regex": "expozitie|exhibition|expo", "$options": "i"}}
                ]}))
                if exhibitions:
                    exhibition_list = "\n".join([f"- {exhibition['title']} ({exhibition['description']})" for exhibition in exhibitions])
                    response_content = f"Expozițiile programate la Aula Universității sunt:\n{exhibition_list}"
                else:
                    response_content = "Nu am găsit expoziții programate la Aula Universității."

            elif re.search(r'(ce|care|cand|unde).*\bconcerte.*\b(aula|universitate)', user_input.lower()):
                concerts = list(collections["aula"].find({"$or": [
                    {"title": {"$regex": "concert|recital", "$options": "i"}},
                    {"description": {"$regex": "concert|recital", "$options": "i"}}
                ]}))
                if concerts:
                    concert_list = "\n".join([f"- {concert['title']} ({concert['description']})" for concert in concerts])
                    response_content = f"Concertele programate la Aula Universității sunt:\n{concert_list}"
                else:
                    response_content = "Nu am găsit concerte programate la Aula Universității."


        

        ### Scenariul 5: Afișarea evenimentelor speciale (de exemplu, festivaluri, gale)
            elif re.search(r'(ce|care|cand|unde).*\bfestival.*\b(aula|universitate)', user_input.lower()):
                festivals = list(collections["aula"].find({"$or": [
                    {"title": {"$regex": "festival|gala", "$options": "i"}},
                    {"description": {"$regex": "festival|gala", "$options": "i"}}
                ]}))
                if festivals:
                    festival_list = "\n".join([f"- {festival['title']} ({festival['description']})" for festival in festivals])
                    response_content = f"Festivalurile și galele programate la Aula Universității sunt:\n{festival_list}"
                else:
                    response_content = "Nu am găsit festivaluri sau gale programate la Aula Universității."

        ### Scenariul 6: Afișarea concursurilor și competițiilor
            elif re.search(r'(ce|care|cand|unde).*\bconcursuri.*\b(aula|universitate)', user_input.lower()):
                competitions = list(collections["aula"].find({"$or": [
                    {"title": {"$regex": "concurs|competition|challenge", "$options": "i"}},
                    {"description": {"$regex": "concurs|competition|challenge", "$options": "i"}}
                ]}))
                if competitions:
                    competition_list = "\n".join([f"- {competition['title']} ({competition['description']})" for competition in competitions])
                    response_content = f"Concursurile și competițiile programate la Aula Universității sunt:\n{competition_list}"
                else:
                    response_content = "Nu am găsit concursuri sau competiții programate la Aula Universității."


        elif re.search(r'(ce|care|cand|unde).*\bevenimente.*\bprimarie', user_input.lower()):
                events = list(collections["primaria"].find({}))
                if events:
                    event_list = "\n".join([f"- {event['title']} ({event['description']})" for event in events])
                    response_content = f"Evenimentele programate la Primărie sunt:\n{event_list}"
                else:
                    response_content = "Nu am găsit evenimente programate la Primărie."




        elif re.search(r'(ce piese (sunt|există) de|piese (de|lui)) ([A-Za-z\s]+)', user_input.lower()):
                author_match = re.search(r'(ce piese (sunt|există) de|piese (de|lui)) ([A-Za-z\s]+)', user_input.lower())
                if author_match:
                    author = author_match.group(4).strip().title()
                    theater_plays = list(collections["teatru"].find({"author": {"$regex": author, "$options": "i"}}))
                    if theater_plays:
                        play_recommendations = [f"- {play['title']} ({play['date_time']})" for play in theater_plays]
                        response_content = f"Iată piesele de teatru de {author} din baza noastră de date:\n" + "\n".join(play_recommendations)
                    else:
                        response_content = f"Ne pare rău, nu am găsit piese de teatru de {author} în baza noastră de date."
                    




        elif re.search(r'(ce piese (sunt|există) (în|in) luna|piese din luna|arată-mi piesele din) ([a-zA-Z]+|\d{1,2})', user_input.lower()):
            month_match = re.search(r'([a-zA-Z]+|\d{1,2})$', user_input.lower())
            if month_match:
                month = month_match.group(1)
                if month.isdigit():
                    month_num = int(month)
                else:
                    month_dict = {'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4, 'mai': 5, 'iunie': 6,
                                'iulie': 7, 'august': 8, 'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12}
                    month_num = month_dict.get(month.lower())
                
                if month_num:
                    month_regex = f"{month_num:02d}\."
                    theater_plays = list(collections["teatru"].find({"date_time": {"$regex": month_regex}}))
                    if theater_plays:
                        play_recommendations = [f"- {play['title']} de {play['author']} ({play['date_time']})" for play in theater_plays]
                        response_content = f"Iată piesele de teatru programate în luna {month}:\n" + "\n".join(play_recommendations)
                    else:
                        response_content = f"Ne pare rău, nu am găsit piese de teatru programate în luna {month}."
                else:
                    response_content = "Nu am putut identifica luna specificată. Te rog să încerci din nou."
        
        # Integrates the Mistral API for queries not covered by the database
        else:
            try:
                chat_response = client.chat(
                    model=model,
                    messages=[ChatMessage(role="user", content=user_input)]
                )
                print(f"Răspunsul de la API-ul Mistral: {chat_response}") 
                print(f"Structura răspunsului: {vars(chat_response)}")
                mistral_response_content = chat_response.choices[0].message.content
                response_content = f"Răspuns de la Mistral: {mistral_response_content}"

                chat_history = ChatHistory(user_message=user_input, ai_response=response_content)
                chat_history.save()
            except Exception as e:
                print(f"Eroare în timpul comunicării cu API-ul Mistral: {str(e)}")  # Adăugăm această linie pentru depanare
                response_content = f"Ne pare rău, a apărut o eroare în timpul comunicării cu API-ul Mistral: {str(e)}"
        
        print(user_input)
        print(f"Răspunsul din view: {response_content}")


        return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input})
    return render(request, 'map/harta.html', {'response': response_content})

@csrf_exempt
def clear_chat_history(request):
    ChatHistory.objects.all().delete()
    return redirect('chat_with_mistral')






@require_http_methods(["GET"])
def events_by_date_teatru(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    news_collection = db["teatru"]

    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%d.%m.%Y")
            print(f"Selected date: {selected_date}")
        except ValueError:
            try:
                selected_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d.%m.%Y")
                print(f"Selected date: {selected_date}")
            except ValueError:
                selected_date = None
                print("Invalid date format")
    else:
        selected_date = None
        print("No date provided")

    events = []
    if selected_date:
        events = list(news_collection.find({'datanoua': {'$in': [selected_date, selected_date.lstrip('0')]}}))
        print(f"Found {len(events)} events")
        print(events)
        print(selected_date)
        
        formatted_events = [
            {
                'title': event['title'],
                'title_link': event['title_link'],
                'author': event['author'],
                'image_url': event['image_url'],
                'date_time': event['date_time'],
                'datanoua': event['datanoua']
            }
            for event in events
        ]
    else:
        formatted_events = []
        print("No events found")

    client.close()
    return render(request, 'map/events_by_date_teatru.html', {'events': formatted_events, 'selected_date': selected_date})




def extract_date(date_time):
    try:
        date_part = date_time.split(',')[1]  #split the string after the comma and take the second part
        date_part = date_part.split(' ')[1]  #split the string by space again and take the second part
        return date_part.strip()  # remove leading and trailing spaces
    except IndexError:
        return "Indisponibil"


def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "Indisponibil"





def teatru(request):
    url = 'https://teatrulsicaalexandrescu.ro/program-5/'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching webpage: {e}")
        return render(request, 'map/teatru.html', {'error': 'Eroare la încărcarea paginii web.'})

    soup = BeautifulSoup(response.content, 'html.parser')
    show_sections = soup.select('div#gridrow-prg')
    new_shows_data = []
    for section in show_sections:
        
        
        
        date_time_element = section.select_one('section.av_textblock_section div p')
        date_time = date_time_element.get_text(separator=" ").strip() if date_time_element else "Data/ora indisponibilă"
        
        # extract the title and link
        title_link_element = section.select_one('section.av_textblock_section div p a')
        title = title_link_element.text.strip() if title_link_element else "Titlu indisponibil"
        title_link = title_link_element['href'] if title_link_element and title_link_element.has_attr('href') else None
        
        # extract the author
        author_element = section.select_one('section.av_textblock_section div p:nth-of-type(2)')
        author = author_element.text.strip() if author_element else "Autor indisponibil"

        # extract the image
        image_element = section.select_one('div.avia-image-container-inner img')
        image_url = image_element['src'] if image_element else "Imagine indisponibilă"

        show_data = {
            'title': title,
            'title_link': title_link,
            'author': author,
            'image_url': image_url,
            'date_time': date_time,
        }
        datanoua = extract_date(date_time)
        formatted_date = format_date(datanoua)
        show_data['datanoua'] = formatted_date
        new_shows_data.append(show_data)

    try:
        MONGODB_URI = os.environ.get('MONGODB_URI')
        client = MongoClient(MONGODB_URI)
        db = client["maps"]
        shows_collection = db["teatru"]

        # Obține spectacolele existente
        existing_shows = list(shows_collection.find())

        # Adaugă noile spectacole
        for show in new_shows_data:
            shows_collection.update_one(
                {'title': show['title'], 'date_time': show['date_time']},
                {'$set': show},
                upsert=True
            )

        # Obține toate spectacolele actualizate
        all_shows = list(shows_collection.find().sort('datanoua', -1))

        # Paginare
        paginator = Paginator(all_shows, 10)  # 10 spectacole per pagină
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    except Exception as e:
        logging.error(f"Error connecting to or updating MongoDB: {e}")
        return render(request, 'map/teatru.html', {'error': 'Eroare la baza de date.'})
    finally:
        client.close()

    return render(request, 'map/teatru.html', {'page_obj': page_obj})


@require_http_methods(["GET"])
def data_teatru(request):
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    news_collection = db["teatru"]

    date_str = request.GET.get('date')
    if date_str:
        # Try parsing the date in "YYYY-MM-DD" format
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            print(f"Selected date: {selected_date}")
        except ValueError:
            selected_date = None
            print("Invalid date format")
    else:
        selected_date = None
        print("No date provided")

    events = []
    if selected_date:
        events = list(news_collection.find({'datanoua': selected_date}))
        print(f"Found {len(events)} events")
        print(events)
        
        formatted_events = [
            {
                'title': event['title'],
                'title_link': event['title_link'],
                'author': event['author'],
                'image_url': event['image_url'],
                'date_time': event['date_time'],
                'datanoua': event['datanoua']
            }
            for event in events
        ]
    else:
        formatted_events = []
        print("No events found")

    client.close()
    return JsonResponse({'events': formatted_events})





# def cinema_city_coord(request):
    
#     cinema_city_coords = [45.65027328171806, 25.61105450714932] 
#     return render(request, 'harta.html', {'cinema_city_coords': cinema_city_coords})

def cinema_locations(request):
    cinema_locations = {
        'Cinema City': [45.65027328171806, 25.61105450714932],
        'Cinema One': [45.67304981680509, 25.61427215362855],
        'Eliana Mall': [45.65766218042808, 25.56141399964052]
    }
    return render(request, 'map/harta.html', {'cinema_locations': cinema_locations})




def aula_scheduler():
    url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
    base_url = 'https://www.unitbv.ro'
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
   
    db = client["maps"]
    news_collection = db["aula"]

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='item')

        for article in articles:
            title_element = article.find('h5', class_='item_title')
            description_element = article.find('div', class_='item_introtext')
            image_element = article.find('img')
            if title_element and description_element and image_element:
                title = title_element.text.strip()
                description = description_element.text.strip()
                image_url = urljoin(base_url, image_element['src'])
                article_url = urljoin(base_url, article.find('a')['href'])
                existing_article = news_collection.find_one({'article_url': article_url})
                if image_url and not existing_article:
                    published_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    article_data = {
                        'title': title,
                        'article_url': article_url,
                        'image_url': image_url,
                        'description': description,
                        'published_date': published_date,
                    }
                    try:
                        news_collection.insert_one(article_data)
                    except Exception as e:
                        print(f"Eroare la inserarea datelor: {str(e)}")

    client.close()



def primaria_scheduler():
    url = 'https://cultura.brasovcity.ro/category/evenimente-culturale-ro/'
    article_data = []
    base_url = 'https://cultura.brasovcity.ro'
    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    news_collection = db["primaria"]
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.post')

        existing_article_urls = set(news_collection.distinct('article_url'))

        for article in articles:
            title_element = article.select_one('h1.entry-title')
            image_element = article.select_one('img.thumbnail')
            description_element = article.select_one('div.entry-summary')

            if title_element and image_element and description_element:
                title = title_element.text.strip()
                image_url = urljoin(base_url, image_element['src'])
                description = description_element.text.strip()
                article_url = title_element.select_one('a')['href'] if title_element.select_one('a') else None

                if article_url not in existing_article_urls:
                    article_data.append({
                        'title': title,
                        'image_url': image_url,
                        'description': description,
                        'article_url': article_url
                    })
                    existing_article_urls.add(article_url)

        if article_data:
            news_collection.insert_many(article_data)

    client.close()




def cinema_city_scheduler():
    url = 'https://www.cinemacity.ro/#/buy-tickets-by-cinema?in-cinema=1829&at=2024-05-27&view-mode=list'
    movie_data = []

    MONGODB_URI = os.environ.get('MONGODB_URI')
    client = MongoClient(MONGODB_URI)
    db = client["maps"]
    movies_collection = db["cinemacity"]

    # configure options for Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service('C:/Users/rusuv/Desktop/chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)
        time.sleep(10)  # Wait for the initial page load

        # Wait until the movie containers are present
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.row.qb-movie')))

        # Get the page source HTML
        html_source = driver.page_source

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_source, 'html.parser')
        movie_containers = soup.find_all('div', class_='row qb-movie')

        for movie_container in movie_containers:
            # Extract the movie title and link
            title_link_element = movie_container.find('a', class_='qb-movie-link')
            title = title_link_element.find('h3').text.strip() if title_link_element else "Titlu indisponibil"
            movie_link = title_link_element['href'] if title_link_element else None

            # movie description
            description_element = movie_container.find('div', class_='qb-movie-info-wrapper')
            description_text = description_element.find('div', class_='pt-xs').text.strip() if description_element else "Descriere indisponibilă"
            genres, duration = (description_text.split('|') + [""])[:2]
            description = f"{genres.strip()} - {duration.strip()}"

            # link to the poster image
            poster_link = movie_container.find('div', class_='movie-poster-container')
            if poster_link:
                poster_img = poster_link.find('img')
                if poster_img:
                    poster_link = poster_img.get('data-src') or poster_img.get('src')
                else:
                    poster_link = None
            else:
                poster_link = None

            print(poster_link)
            
            showtime_elements = movie_container.find_all('a', class_='btn btn-primary btn-lg')
            showtimes = [showtime_element.text.strip() for showtime_element in showtime_elements]

           
            movie_data.append({
                'title': title,
                'description': description,
                'poster_link': poster_link,
                'showtimes': showtimes,
                'movie_link': movie_link
            })

            # Insert/update data in MongoDB
            movies_collection.update_one(
                {'title': title},
                {'$set': {
                    'title': title,
                    'description': description,
                    'poster_link': poster_link,
                    'showtimes': showtimes,
                    'movie_link': movie_link
                }},
                upsert=True
            )

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
        client.close()

    print(f"Updated {len(movie_data)} movies in the database.")




def teatru_scheduler():
    url = 'https://teatrulsicaalexandrescu.ro/program-5/'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching webpage: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    show_sections = soup.select('div#gridrow-prg')
    new_shows_data = []
    for section in show_sections:
        date_time_element = section.select_one('section.av_textblock_section div p')
        date_time = date_time_element.get_text(separator=" ").strip() if date_time_element else "Data/ora indisponibilă"
        
        title_link_element = section.select_one('section.av_textblock_section div p a')
        title = title_link_element.text.strip() if title_link_element else "Titlu indisponibil"
        title_link = title_link_element['href'] if title_link_element and title_link_element.has_attr('href') else None
        
        author_element = section.select_one('section.av_textblock_section div p:nth-of-type(2)')
        author = author_element.text.strip() if author_element else "Autor indisponibil"

        image_element = section.select_one('div.avia-image-container-inner img')
        image_url = image_element['src'] if image_element else "Imagine indisponibilă"

        show_data = {
            'title': title,
            'title_link': title_link,
            'author': author,
            'image_url': image_url,
            'date_time': date_time,
        }
        datanoua = extract_date(date_time)
        formatted_date = format_date(datanoua)
        show_data['datanoua'] = formatted_date
        new_shows_data.append(show_data)

    try:
        MONGODB_URI = os.environ.get('MONGODB_URI')
        client = MongoClient(MONGODB_URI)
        db = client["maps"]
        shows_collection = db["teatru"]

        # Adaugă noile spectacole
        for show in new_shows_data:
            shows_collection.update_one(
                {'title': show['title'], 'date_time': show['date_time']},
                {'$set': show},
                upsert=True
            )

        logging.info(f"Updated {len(new_shows_data)} shows in the database.")

    except Exception as e:
        logging.error(f"Error connecting to or updating MongoDB: {e}")
    finally:
        client.close()