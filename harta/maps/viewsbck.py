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

# client = MongoClient("mongodb://localhost:27017/")
# db = client["maps"]
# colectie = db["CV"]
# #din baza de date trebuie citite, sa nu fie statice, in binar sa fie
# cale_imagini = [
#     "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_vechi\\primaria.png",
#      "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_vechi\\teatru.png"
# ]

# nume_imagini = ["Primaria","Teatru Dramatic"]

# def adauga_imagini_in_db():
#     for cale_imagine, nume_imagine in zip(cale_imagini, nume_imagini):
#         # Verifică dacă imaginea există deja în colecție
#         if colectie.find_one({"nume": nume_imagine}):
#             continue

#         with open(cale_imagine, "rb") as image_file:
#             # Decodifică imaginea și comprimă-o
#             imagine = Image.open(BytesIO(image_file.read()))
#             buffer = BytesIO()
#             imagine = imagine.convert('RGB')
#             imagine.save(buffer, format="JPEG")
#             content = buffer.getvalue()

#         colectie.insert_one({"nume": nume_imagine, "imagine": content})

# # Adaugă imaginile doar dacă nu există deja
# adauga_imagini_in_db()

# client.close()

def get_images_centru_civic(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    colectie = db["CC"]

    imagini = list(colectie.find({}, {'_id': 0}))

    for imagine in imagini:
        imagine['imagine'] = base64.b64encode(imagine['imagine']).decode('utf-8')

    client.close()

    return JsonResponse({'imagini': imagini})

def get_images_centru_vechi(request):
    client = MongoClient("mongodb://localhost:27017/")
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






# def aula(request: HttpRequest):
#     url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
#     base_url = 'https://www.unitbv.ro'
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     news_collection = db["aula"]

#     search_query = request.GET.get('q', '')

#     if search_query:
#         filtered_articles = news_collection.find({
#             '$or': [
#                 {'title': {'$regex': search_query, '$options': 'i'}},
#                 {'description': {'$regex': search_query, '$options': 'i'}}
#             ]
#         }).sort("published_date", -1)
#     else:
#         filtered_articles = news_collection.find().sort("published_date", 1)

#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         articles = soup.find_all('article', class_='item')
            
#         for article in articles:
#             title_element = article.find('h5', class_='item_title')
#             description_element = article.find('div', class_='item_introtext')
#             image_element = article.find('img')
#             if title_element and description_element and image_element:
#                 title = title_element.text.strip()
#                 description = description_element.text.strip()
#                 image_url = urljoin(base_url, image_element['src'])
#                 article_url = urljoin(base_url, article.find('a')['href'])
#                 existing_article = news_collection.find_one({'article_url': article_url})
#                 if image_url and not existing_article:
#                     published_date = datetime.now().strftime("%Y-%m-%d")
#                     article_data = {
#                         'title': title,
#                         'article_url': article_url,
#                         'image_url': image_url,
#                         'description': description,
#                         'published_date': published_date,
#                     }
#                     try:
#                         news_collection.insert_one(article_data)
#                     except Exception as e:
#                         print(f"Eroare la inserarea datelor: {str(e)}")

#     articole_list = list(filtered_articles)
#     client.close()

#     context = {'articole': articole_list, 'search_query': search_query}
#     return render(request, 'map/aula.html', context)






# def aula(request: HttpRequest):
#     url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
#     base_url = 'https://www.unitbv.ro'
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     news_collection = db["aulas"]

#     search_query = request.GET.get('q', '')

#     if search_query:
#         filtered_articles = news_collection.find({
#             '$or': [
#                 {'title': {'$regex': search_query, '$options': 'i'}},
#                 {'description': {'$regex': search_query, '$options': 'i'}}
#             ]
#         }).sort("published_date", -1)
#     else:
#         filtered_articles = news_collection.find().sort("published_date", -1)

#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         articles = soup.find_all('article', class_='item')
            
#         for article in articles:
#             title_element = article.find('h5', class_='item_title')
#             description_element = article.find('div', class_='item_introtext')
#             image_element = article.find('img')
#             if title_element and description_element and image_element:
#                 title = title_element.text.strip()
#                 description = description_element.text.strip()
#                 image_url = urljoin(base_url, image_element['src'])
#                 article_url = urljoin(base_url, article.find('a')['href'])
#                 existing_article = news_collection.find_one({'article_url': article_url})
#                 if image_url and not existing_article:
#                     published_date = datetime.now().strftime("%Y-%m-%d")
#                     published_date = datetime.strptime(published_date, "%Y-%m-%d")
#                     article_data = {
#                         'title': title,
#                         'article_url': article_url,
#                         'image_url': image_url,
#                         'description': description,
#                         'published_date': published_date,
#                     }
#                     try:
#                         news_collection.insert_one(article_data)
#                     except Exception as e:
#                         print(f"Eroare la inserarea datelor: {str(e)}")

#     articole_list = list(filtered_articles)

#     current_date = datetime.now().date()
#     new_article_threshold = current_date - timedelta(days=7)  # Consideră articolele mai noi de 7 zile ca fiind noi

#     for articol in articole_list:
#         articol['is_new'] = articol['published_date'].date() > new_article_threshold

#     client.close()

#     context = {'articole': articole_list, 'search_query': search_query}
#     return render(request, 'map/aula.html', context)







# def aula(request: HttpRequest):
#     url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
#     base_url = 'https://www.unitbv.ro'
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     news_collection = db["aulas"] 
#     search_query = request.GET.get('q', '')

#     if search_query:
#         filtered_articles = news_collection.find({
#             '$or': [
#                 {'title': {'$regex': search_query, '$options': 'i'}},
#                 {'description': {'$regex': search_query, '$options': 'i'}}
#             ]
#         }).sort("published_date", -1)
#     else:
#         filtered_articles = news_collection.find().sort("published_date", -1)

#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')
#         articles = soup.find_all('article', class_='item')
            
#         for article in articles:
#             title_element = article.find('h5', class_='item_title')
#             description_element = article.find('div', class_='item_introtext')
#             image_element = article.find('img')
#             if title_element and description_element and image_element:
#                 title = title_element.text.strip()
#                 description = description_element.text.strip()
#                 image_url = urljoin(base_url, image_element['src'])
#                 article_url = urljoin(base_url, article.find('a')['href'])
#                 existing_article = news_collection.find_one({'article_url': article_url})
#                 if image_url and not existing_article:
#                     published_date = datetime.now().strftime("%Y-%m-%d")
#                     published_date = datetime.strptime(published_date, "%Y-%m-%d")
#                     article_data = {
#                         'title': title,
#                         'article_url': article_url,
#                         'image_url': image_url,
#                         'description': description,
#                         'published_date': published_date,
#                     }
#                     try:
#                         news_collection.insert_one(article_data)
#                     except Exception as e:
#                         print(f"Eroare la inserarea datelor: {str(e)}")

#     articole_list = list(filtered_articles)

#     date_str = request.GET.get('date')
#     if date_str:
#         try:
#             selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         except ValueError:
#             selected_date = None
#     else:
#         selected_date = None

#     context = {'articole': articole_list, 'search_query': search_query, 'selected_date': selected_date}
#     client.close()

#     return render(request, 'map/aula.html', context)




def aula(request: HttpRequest):
    url = 'https://www.unitbv.ro/stiri-si-evenimente.html'
    base_url = 'https://www.unitbv.ro'
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["aulas"]
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
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["aulas"]

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








# @require_http_methods(["GET"])
# def data_aula(request):
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     news_collection = db["aulas"]

#     date_str = request.GET.get('date')
#     if date_str:
#         try:
#             selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#             selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day)
#         except ValueError:
#             selected_datetime = None
#     else:
#         selected_datetime = None

#     if selected_datetime:
#         events = list(news_collection.find({'published_date': selected_datetime}))
        
#         formatted_events = [
#             {
#                 'title': event['title'],
#                 'article_url': event['article_url'],
#                 'description':event['description'],
#                 'image_url': event['image_url'],
#                 'published_date': event['published_date'].strftime("%Y-%m-%d")
#             }
#             for event in events
#         ]
#     else:
#         formatted_events = []

#     client.close()
#     return JsonResponse({'events': formatted_events})




@require_http_methods(["GET"])
def data_aula(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["aulas"]

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
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["primaria"]
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='post')

        for article in articles:
            title_element = article.find('h1', class_='entry-title')
            image_element = article.find('img', class_='thumbnail')
            description_element = article.find('div', class_='entry-summary')

            if title_element and image_element and description_element:
                title = title_element.text.strip()
                image_url = urljoin(base_url, image_element['src'])
                description = description_element.text.strip()
                article_url = title_element.find('a')['href']
                existing_article = news_collection.find_one({'article_url': article_url})

                # Încercăm să extragem data din descrierea articolului
                lines = description.split('\n')
                date = "Data necunoscută"
                for line in lines:
                    date_match = re.match(r'(\d{1,2}\s*[a-zA-Z\s]+)', line)
                    if date_match:
                        date = date_match.group(1)
                        break

                if image_url and not existing_article:
                    article_data.append({
                        'title': title,
                        'date': date,
                        'image_url': image_url,
                        'description': description,
                        'article_url': article_url
                    })

        if article_data:
            news_collection.insert_many(article_data)

        articole = news_collection.find()
        client.close()
        articole_list = list(articole)
        return render(request, 'map/primaria.html', {'articole': articole_list})
    
def get_all_events(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client.maps 
    events_collection = db.aulas 
    primaria_collection = db.primaria  

    events = events_collection.find({})
    primaria_events = primaria_collection.find({})  #  evenimentele din colectia primaria

    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get ("image_url","")} for event in events]
    primaria_events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"),"image_url": event.get ("image_url","")} for event in primaria_events]

    client.close()

    # Combina listele de evenimente din ambele colecii
    combined_events_list = events_list + primaria_events_list

    return JsonResponse({'events': combined_events_list})




def cinema_city(request):
    url = 'https://www.cinemacity.ro/#/buy-tickets-by-cinema?in-cinema=1829&at=2024-05-27&view-mode=list'
    movie_data = []

    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    movies_collection = db["cinemacity"]

    # Configurarea opțiunilor pentru Chrome
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
            # Extrage titlul filmului și link-ul
            title_link_element = movie_container.find('a', class_='qb-movie-link')
            title = title_link_element.find('h3').text.strip() if title_link_element else "Titlu indisponibil"
            movie_link = title_link_element['href'] if title_link_element else None

            # Extrage descrierea filmului
            description_element = movie_container.find('div', class_='qb-movie-info-wrapper')
            description_text = description_element.find('div', class_='pt-xs').text.strip() if description_element else "Descriere indisponibilă"
            genres, duration = (description_text.split('|') + [""])[:2]
            description = f"{genres.strip()} - {duration.strip()}"

            # Căutăm link-ul către imaginea posterului
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
            # Extrage orele de difuzare
            showtime_elements = movie_container.find_all('a', class_='btn btn-primary btn-lg')
            showtimes = [showtime_element.text.strip() for showtime_element in showtime_elements]

            # Adaugăm link-ul imaginii posterului în datele filmului
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
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    aula_collection = db["aulas"] 

    events = aula_collection.find({})
    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get("image_url","")} for event in events]

    client.close()
    return JsonResponse({'events': events_list})

def events_primaria(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    primaria_collection = db["primaria"] 

    events = primaria_collection.find({})
    events_list = [{"title": event["title"], "description": event.get("description", ""), "article_url": event.get("article_url", "#"), "image_url": event.get("image_url","")} for event in events]

    client.close()
    return JsonResponse({'events': events_list})

def events_teatru(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    teatru_collection = db["teatru"]

    events = teatru_collection.find({}, {'_id': 0})
    events_list = [{"title": event["title"], "author": event["author"], "date_time": event["date_time"], "title_link": event["title_link"], "image_url":event["image_url"]} for event in events]

    client.close()
    return JsonResponse({'events': events_list})


def events_filme(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    movies_collection = db["cinemacity"]

    events = movies_collection.find({}, {'_id': 0})
    events_list = [{"title": event["title"], "description": event["description"], "showtimes": event["showtimes"], "movie_link": event["movie_link"], "poster_link": event["poster_link"]} for event in events]

    client.close()
    return JsonResponse({'events': events_list})



# def teatru(request):
#     url = 'https://teatrulsicaalexandrescu.ro/program-5/'

#     try:
#         response = requests.get(url)
#         response.raise_for_status() 
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching webpage: {e}")
#         return render(request, 'map/teatru.html', {'error': 'Eroare la încărcarea paginii web.'})

#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Selectăm toate div-urile care conțin informațiile despre spectacole
#     show_sections = soup.select('div#gridrow-prg') 

#     shows_data = []

#     for section in show_sections:
#         # Nu mai excludem niciun div, deoarece toate conțin informații relevante
        
#         # Extragem data și ora
#         date_time_element = section.select_one('section.av_textblock_section div p')
#         date_time = date_time_element.get_text(separator=" ").strip() if date_time_element else "Data/ora indisponibilă"
        
#         # Extragem titlul și link-ul
#         title_link_element = section.select_one('section.av_textblock_section div p a')
#         title = title_link_element.text.strip() if title_link_element else "Titlu indisponibil"
#         title_link = title_link_element['href'] if title_link_element and title_link_element.has_attr('href') else None
        
#         # Extragem autorul
#         author_element = section.select_one('section.av_textblock_section div p:nth-of-type(2)')
#         author = author_element.text.strip() if author_element else "Autor indisponibil"

#         # Extragem imaginea
#         image_element = section.select_one('div.avia-image-container-inner img')
#         image_url = image_element['src'] if image_element else "Imagine indisponibilă"

#         show_data = {
#             'title': title,
#             'title_link': title_link,
#             'author': author,
#             'image_url': image_url,
#             'date_time': date_time,
#         }
#         shows_data.append(show_data)
#     try:
#         client = MongoClient("mongodb://localhost:27017/")
#         db = client["maps"]
#         shows_collection = db["teatru"]

#         # Ștergem toate datele existente din colecție
#         shows_collection.delete_many({})
#         # Insert data into MongoDB
#         shows_collection.insert_many(shows_data)  

#     except Exception as e:
#         logging.error(f"Error connecting to or updating MongoDB: {e}")
#         return render(request, 'map/teatru.html', {'error': 'Eroare la baza de date.'})
#     finally:
#         client.close()

#     # Pass the list of all shows data to the template
#     return render(request, 'map/teatru.html', {'shows':shows_data})



# @csrf_exempt
# def chat_with_mistral(request):
#     load_dotenv()
#     if request.method == 'POST':
#         user_input = request.POST.get('message', '')
#         if not user_input:
#             return render(request, 'map/harta.html', {'error': 'No input provided'})

#         api_key = os.getenv("MISTRAL_API_KEY")
#         if not api_key:
#             return render(request, 'map/harta.html', {'error': 'Mistral API key not found'})

#         client = MistralClient(api_key=api_key)
#         model = "mistral-large-latest"

#         # Conectare la MongoDB
#         mongo_client = MongoClient("mongodb://localhost:27017/")
#         db = mongo_client.maps
#         collections = {
#             "cinemacity": db.cinemacity,
#             "Events": db.aulas,
#             "primaria": db.primaria,
#             "teatru": db.teatru
#         }

#         # Verifică diferite tipuri de întrebări
#         if re.search(r'(aula|universitate|facultate|stiri|unitbv)', user_input.lower()):
#             aula_events = list(collections["Events"].find({}))
#             if aula_events:
#                 response_content = "Iată evenimentele de la Aula Universitatii și UNITBV:\n" + \
#                                    "\n".join([f"Titlu: {event['title']}, Descriere: {event['description']}"
#                                               for event in aula_events])
#             else:
#                 response_content = "Nu am găsit evenimente la Aula Universitatii sau UNITBV în baza de date."

#         elif re.search(r'(cinema|film)', user_input.lower()):
#             cinema_movies = list(collections["cinemacity"].find())
#             if cinema_movies:
#                 response_content = "Iată filmele disponibile la Cinema City:\n" + \
#                                    "\n".join([f"Titlu: {movie['title']}, Descriere: {movie['description']}"
#                                               for movie in cinema_movies])
#             else:
#                 response_content = "Nu am găsit informații despre filme la Cinema City în baza de date."

#         elif re.search(r'(primarie|cultura|brasov)', user_input.lower()):
#             primarie_events = list(collections["primaria"].find())
#             if primarie_events:
#                 primarie_response = "Iată câteva evenimente culturale de la Primăria Brașov:\n" + \
#                                     "\n".join([f"Titlu: {event['title']}, Descriere: {event['description']}"
#                                                for event in primarie_events])
#             else:
#                 primarie_response = "Nu am gasit evenimente culturale de la Primăria Brașov în baza de date"
#             mongo_client.close()
#             return render(request, 'map/harta.html', {'response': primarie_response})

#         elif re.search(r'(teatru|piese|spectacole)', user_input.lower()):
#             teatru_events = list(collections["teatru"].find({}))
#             if teatru_events:
#                 teatru_response = "Iată câteva piese de teatru disponibile:\n" + \
#                                   "\n".join([f"Titlu: {event['title']}, Autor: {event['author']}, Data: {event['date_time']}, Link: {event['title_link']}"
#                                              for event in teatru_events])
#             else:
#                 teatru_response = "Nu am găsit piese de teatru în baza de date."
#             mongo_client.close()
#             return render(request, 'map/harta.html', {'response': teatru_response})

#         else:
#             try:
#                 chat_response = client.chat(
#                     model=model,
#                     messages=[ChatMessage(role="user", content=user_input)]
#                 )
#                 response_content = chat_response.choices[0].message.content


#                 chat_history = ChatHistory(user_message=user_input, ai_response=response_content)
#                 chat_history.save()

#             except Exception as e:
#                 mongo_client.close()
#                 return render(request, 'map/harta.html', {'error': str(e)})
                

#         mongo_client.close()
#         chat_history = ChatHistory.objects.all().order_by('-created_at')
#         return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input})
        
#     return render(request, 'map/harta.html')
@csrf_exempt
def chat_with_mistral(request):
    load_dotenv()

    if request.method == 'POST':
        user_input = request.POST.get('message', '')
        if not user_input:
            return render(request, 'map/harta.html', {'error': 'Nu a fost furnizată nicio intrare'})

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return render(request, 'map/harta.html', {'error': 'Cheia API Mistral nu a fost găsită'})

        client = MistralClient(api_key=api_key)
        model = "mistral-large-latest"

        # Conectare la MongoDB
        mongo_client = MongoClient("mongodb://localhost:27017/")
        db = mongo_client.maps
        collections = {
            "cinemacity": db.cinemacity,
            "aulas": db.aulas,
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
                    response_content = f"Filmul '{movie['title']}' poate fi vizionat la Cinema City. Locația Cinema City este indicată pe hartă."
            
                    cinema_city_coords = [45.65027328171806, 25.61105450714932] # Coordonatele corecte ale Cinema City
                    return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input, 'cinema_city_coords': cinema_city_coords})
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
                        response_content = f"Trailer-ul pentru filmul '{movie['title']}' poate fi găsit aici: {movie['poster_link']}"
                    else:
                        response_content = f"Ne pare rău, nu am găsit trailer-ul pentru filmul '{movie_title}'."
                else:
                    response_content = "Te rog specifică un film pentru a obține link-ul către trailer (de exemplu: 'trailer pentru Numele Filmului')."
       
       
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
   
         
#Afișarea detaliilor unui anumit eveniment
#Detalii despre Expoziția Paula Modersohn-Becker şi colonia de artişti din Worpswede"

# Afișarea tuturor evenimentelor și anunțurilor
#Ce evenimente sunt la Aula Universității?"





        # elif re.search(r'(aula|universitate|facultate|stiri|unitbv)', user_input.lower()):
        #     if re.search(r'evenimente', user_input.lower()):
        #         # Scenariul 1: Afișarea tuturor evenimentelor și anunțurilor
        #         events = list(collections["aulas"].find())
        #         if events:
        #             event_list = "\n".join([f"- {event['title']} ({event['published_date']})" for event in events])
        #             response_content = f"Evenimentele și anunțurile de la Aula Universității sunt:\n{event_list}"
        #         else:
        #             response_content = "Nu am găsit evenimente sau anunțuri în acest moment."
            
        # elif re.search(r'detalii', user_input.lower()):
        #         # Scenariul 2: Afișarea detaliilor unui anumit eveniment
        #         event_match = re.search(r'detalii despre\s+(.+)', user_input.lower())
        #         if event_match:
        #             event_title = event_match.group(1)
        #             event = collections["aulas"].find_one({"title": {"$regex": event_title, "$options": "i"}})
        #             if event:
        #                 response_content = f"Detalii despre evenimentul '{event['title']}':\n"
        #                 response_content += f"- Descriere: {event['description']}\n"
                        
        #                 response_content += f"- Link: {event['article_url']}"
        #             else:
        #                 response_content = f"Nu am găsit detalii despre evenimentul '{event_title}'."
        #         else:
        #             response_content = "Te rog specifică un eveniment pentru a obține detalii (de exemplu: 'detalii despre Numele Evenimentului')."

        # elif re.search(r'perioada', user_input.lower()):
        #         # Scenariul 4: Căutarea evenimentelor dintr-o anumită perioadă
        #         period_match = re.search(r'(evenimente|anunțuri)\s+în\s+(\w+)', user_input.lower())
        #         if period_match:
        #             period = period_match.group(2)
        #             events = list(collections["aulas"].find({"published_date": {"$regex": period, "$options": "i"}}))
        #             if events:
        #                 event_list = "\n".join([f"- {event['title']} ({event['published_date']})" for event in events])
        #                 response_content = f"Evenimentele și anunțurile din perioada '{period}' sunt:\n{event_list}"
        #             else:
        #                 response_content = f"Nu am găsit evenimente sau anunțuri în perioada '{period}'."
        #         else:
        #             response_content = "Te rog specifică o perioadă pentru a căuta evenimente (de exemplu: 'evenimente în iunie')."

        # elif re.search(r'link', user_input.lower()):
        #         # Scenariul 3: Afișarea link-ului unui eveniment
        #         event_match = re.search(r'link\s+pentru\s+(.+)', user_input.lower())
        #         if event_match:
        #             event_title = event_match.group(1)
        #             event = collections["aulas"].find_one({"$or": [
        #                 {"title": {"$regex": event_title, "$options": "i"}},
        #                 {"description": {"$regex": event_title, "$options": "i"}}
        #             ]})
        #             if event:
        #                 response_content = f"Link-ul pentru evenimentul '{event['title']}' este: {event['article_url']}"
        #             else:
        #                 response_content = f"Nu am găsit link-ul pentru evenimentul '{event_title}'."
        #         else:
        #             response_content = "Te rog specifică un eveniment pentru a obține link-ul (de exemplu: 'link pentru Numele Evenimentului')."
           
        # elif re.search(r'imagine', user_input.lower()):
        #         # Scenariul 4: Afișarea imaginii unui eveniment  
        #         event_match = re.search(r'imagine\s+pentru\s+(.+)', user_input.lower())
        #         if event_match:
        #             event_title = event_match.group(1)
        #             event = collections["aulas"].find_one({"title": {"$regex": event_title, "$options": "i"}})
        #             if event:
        #                 response_content = f"Imaginea pentru evenimentul '{event['title']}' poate fi găsită aici: {event['image_url']}"
        #             else:
        #                 response_content = f"Nu am găsit imaginea pentru evenimentul '{event_title}'."
        #         else:
        #             response_content = "Te rog specifică un eveniment pentru a obține imaginea (de exemplu: 'imagine pentru Numele Evenimentului')."
            
        # elif re.search(r'unde\s+(se desfășoară|are loc)', user_input.lower()):
        #         # Scenariul 5: Întrebări despre locul de desfășurare al evenimentelor
        #         event_match = re.search(r'unde\s+(se desfășoară|are loc)\s+(.+)', user_input.lower())
        #         if event_match:
        #             event_title = event_match.group(2)
        #             event = collections["aulas"].find_one({"title": {"$regex": event_title, "$options": "i"}})
        #             if event:
        #                 location = re.search(r'Aula\s+[^,.]+', event['description'])
        #                 if location:
        #                     response_content = f"Evenimentul '{event['title']}' se desfășoară la {location.group()}."
        #                 else:
        #                     response_content = f"Nu am găsit informații exacte despre locul de desfășurare al evenimentului '{event['title']}', dar acesta are loc probabil la una dintre aulele Universității Transilvania."
        #             else:
        #                 response_content = f"Nu am găsit evenimentul '{event_title}'."
        #         else:
        #             response_content = "Te rog specifică un eveniment pentru a afla locul de desfășurare (de exemplu: 'unde are loc Numele Evenimentului')."

            

        # elif re.search(r'(gratuite|intrare liberă|fără taxă)', user_input.lower()):
        #         # Scenariul 6: Afișarea evenimentelor cu intrare liberă
        #         events = list(collections["aulas"].find({"description": {"$regex": "intrare liberă|gratuit|fără taxă", "$options": "i"}}))
        #         if events:
        #             event_list = "\n".join([f"- {event['title']} ({event['published_date']})" for event in events])
        #             response_content = f"Evenimentele cu intrare liberă sunt:\n{event_list}"
        #         else:
        #             response_content = "Nu am găsit evenimente cu intrare liberă."

        # else:
        #         # Scenariul 7: Căutarea unui eveniment după titlu sau cuvinte cheie
        #         events = list(collections["aulas"].find({"$or": [{"title": {"$regex": user_input, "$options": "i"}}, {"description": {"$regex": user_input, "$options": "i"}}]}))
        #         if events:
        #             event_list = "\n".join([f"- {event['title']} ({event['published_date']})" for event in events])
        #             response_content = f"Evenimentele și anunțurile găsite pentru '{user_input}' sunt:\n{event_list}"
        #         else:
        #             response_content = f"Nu am găsit evenimente sau anunțuri pentru '{user_input}'."








        # Integrează API-ul Mistral pentru întrebări care nu sunt acoperite de baza de date
        else:
            try:
                chat_response = client.chat(
                    model=model,
                    messages=[ChatMessage(role="user", content=user_input)]
                )
                response_content = chat_response.choices[0].message.content

                chat_history = ChatHistory(user_message=user_input, ai_response=response_content)
                chat_history.save()
            except Exception as e:
                mongo_client.close()
                return render(request, 'map/harta.html', {'error': str(e)})

        mongo_client.close()
        chat_history = ChatHistory.objects.all().order_by('-created_at')
        return render(request, 'map/harta.html', {'response': response_content, 'user_input': user_input})
    
    return render(request, 'map/harta.html')
@csrf_exempt
def clear_chat_history(request):
    ChatHistory.objects.all().delete()
    return redirect('chat_with_mistral')



    



# def extract_date(date_time):
#     try:
#         date_part = date_time.split(',')[1]  # Împărțim șirul după virgulă și luăm a doua parte
#         date_part = date_part.split(' ')[1]  # Împărțim din nou șirul după spațiu și luăm a doua parte
#         return date_part.strip()  # Eliminăm spațiile de la început și sfârșit
#     except IndexError:
#         return "Indisponibil"


# def teatru(request):
#     url = 'https://teatrulsicaalexandrescu.ro/program-5/'

#     try:
#         response = requests.get(url)
#         response.raise_for_status() 
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching webpage: {e}")
#         return render(request, 'map/teatru.html', {'error': 'Eroare la încărcarea paginii web.'})

#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Selectăm toate div-urile care conțin informațiile despre spectacole
#     show_sections = soup.select('div#gridrow-prg') 

#     shows_data = []

#     for section in show_sections:
#         # Nu mai excludem niciun div, deoarece toate conțin informații relevante
        
#         # Extragem data și ora
#         date_time_element = section.select_one('section.av_textblock_section div p')
#         date_time = date_time_element.get_text(separator=" ").strip() if date_time_element else "Data/ora indisponibilă"
        
#         # Extragem titlul și link-ul
#         title_link_element = section.select_one('section.av_textblock_section div p a')
#         title = title_link_element.text.strip() if title_link_element else "Titlu indisponibil"
#         title_link = title_link_element['href'] if title_link_element and title_link_element.has_attr('href') else None
        
#         # Extragem autorul
#         author_element = section.select_one('section.av_textblock_section div p:nth-of-type(2)')
#         author = author_element.text.strip() if author_element else "Autor indisponibil"

#         # Extragem imaginea
#         image_element = section.select_one('div.avia-image-container-inner img')
#         image_url = image_element['src'] if image_element else "Imagine indisponibilă"

#         show_data = {
#             'title': title,
#             'title_link': title_link,
#             'author': author,
#             'image_url': image_url,
#             'date_time': date_time,
#         }
#         shows_data.append(show_data)

#         # Actualizăm colecția "teatru" cu câmpul "datanoua"
#         datanoua = extract_date(date_time)
#         show_data['datanoua'] = datanoua

#     try:
#         client = MongoClient("mongodb://localhost:27017/")
#         db = client["maps"]
#         shows_collection = db["teatru99"]

#         # Ștergem toate datele existente din colecție
#         shows_collection.delete_many({})
#         # Insert data into MongoDB
#         shows_collection.insert_many(shows_data)  

#     except Exception as e:
#         logging.error(f"Error connecting to or updating MongoDB: {e}")
#         return render(request, 'map/teatru.html', {'error': 'Eroare la baza de date.'})
#     finally:
#         client.close()

#     # Pass the list of all shows data to the template
#     return render(request, 'map/teatru.html', {'shows':shows_data})





# @require_http_methods(["GET"])
# def data_teatru(request):
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     news_collection = db["teatru99"]

#     date_str = request.GET.get('date')
#     if date_str:
#         # Try parsing the date in both "d.mm.yyyy" and "dd.mm.yyyy" formats
#         try:
#             selected_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%d.%m.%Y")
#             print(f"Selected date: {selected_date}")
#         except ValueError:
#             try:
#                 selected_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d.%m.%Y")
#                 print(f"Selected date: {selected_date}")
#             except ValueError:
#                 selected_date = None
#                 print("Invalid date format")
#     else:
#         selected_date = None
#         print("No date provided")

#     events = []
#     if selected_date:
#         # Query the collection with both "d.mm.yyyy" and "dd.mm.yyyy" formats
#         events = list(news_collection.find({'datanoua': {'$in': [selected_date, selected_date.lstrip('0')]}}))
#         print(f"Found {len(events)} events")
#         print(events)
#         print(selected_date)
        
#         formatted_events = [
#             {
#                 'title': event['title'],
#                 'title_link': event['title_link'],
#                 'author': event['author'],
#                 'image_url': event['image_url'],
#                 'date_time': event['date_time'],
#                 'datanoua': event['datanoua']
#             }
#             for event in events
#         ]
#     else:
#         formatted_events = []
#         print("No events found")

#     client.close()
#     return JsonResponse({'events': formatted_events})




@require_http_methods(["GET"])
def events_by_date_teatru(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["teatru999"]

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
        date_part = date_time.split(',')[1]  # Împărțim șirul după virgulă și luăm a doua parte
        date_part = date_part.split(' ')[1]  # Împărțim din nou șirul după spațiu și luăm a doua parte
        return date_part.strip()  # Eliminăm spațiile de la început și sfârșit
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

    # Selectăm toate div-urile care conțin informațiile despre spectacole
    show_sections = soup.select('div#gridrow-prg')

    shows_data = []

    for section in show_sections:
        # Nu mai excludem niciun div, deoarece toate conțin informații relevante
        
        # Extragem data și ora
        date_time_element = section.select_one('section.av_textblock_section div p')
        date_time = date_time_element.get_text(separator=" ").strip() if date_time_element else "Data/ora indisponibilă"
        
        # Extragem titlul și link-ul
        title_link_element = section.select_one('section.av_textblock_section div p a')
        title = title_link_element.text.strip() if title_link_element else "Titlu indisponibil"
        title_link = title_link_element['href'] if title_link_element and title_link_element.has_attr('href') else None
        
        # Extragem autorul
        author_element = section.select_one('section.av_textblock_section div p:nth-of-type(2)')
        author = author_element.text.strip() if author_element else "Autor indisponibil"

        # Extragem imaginea
        image_element = section.select_one('div.avia-image-container-inner img')
        image_url = image_element['src'] if image_element else "Imagine indisponibilă"

        show_data = {
            'title': title,
            'title_link': title_link,
            'author': author,
            'image_url': image_url,
            'date_time': date_time,
        }
        shows_data.append(show_data)

        # Actualizăm colecția "teatru" cu câmpul "datanoua"
        datanoua = extract_date(date_time)
        formatted_date = format_date(datanoua)
        show_data['datanoua'] = formatted_date

    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["maps"]
        shows_collection = db["teatru999"]

        # Ștergem toate datele existente din colecție
        shows_collection.delete_many({})
        # Insert data into MongoDB
        shows_collection.insert_many(shows_data)  

    except Exception as e:
        logging.error(f"Error connecting to or updating MongoDB: {e}")
        return render(request, 'map/teatru.html', {'error': 'Eroare la baza de date.'})
    finally:
        client.close()

    # Pass the list of all shows data to the template
    return render(request, 'map/teatru.html', {'shows': shows_data})


@require_http_methods(["GET"])
def data_teatru(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    news_collection = db["teatru999"]

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





def cinema_city_coord(request):
    
    cinema_city_coords = [45.65027328171806, 25.61105450714932] 
    return render(request, 'harta.html', {'cinema_city_coords': cinema_city_coords})

