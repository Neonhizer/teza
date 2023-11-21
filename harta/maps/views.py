# from django.http import JsonResponse, HttpResponse
# from django.shortcuts import render, redirect
# from .models import Location, Event
# from bs4 import BeautifulSoup
# import requests
# from pymongo import MongoClient
# import datetime
# from urllib.parse import urljoin

# import base64


# # Conectare la MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client["maps"]
# colectie = db["CC"]

# # Lista cu căile către fișierele locale
# cale_imagini = ["C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\aftar.jpg", 
#                 "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\aula.jpg",
#                 "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\kruhnen.png",
#                 "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\temple.png"
#                 ]

# nume_imagini = ["Aftar Hours", "Aula UniTBv", "Kruhnen Musik Halle", "Temple"]

# # Iterare prin fiecare imagine și adăugare în MongoDB
# for cale_imagine, nume_imagine in zip(cale_imagini, nume_imagini):
#     with open(cale_imagine, "rb") as image_file:
#         content = image_file.read()
    
#     colectie.insert_one({"nume": nume_imagine, "imagine": content})

# # Închidere conexiune
# client.close()



# def get_images(request):
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["maps"]
#     colectie = db["CC"]

#     imagini = list(colectie.find({}, {'_id': 0}))

#     for imagine in imagini:
#         imagine['imagine'] = base64.b64encode(imagine['imagine']).decode('utf-8')

#     client.close()

#     return JsonResponse({'imagini': imagini})





# # from django.http import JsonResponse
# # from .models import Imagine
# # from django.core.files.storage import default_storage
# # from django.core.files.base import ContentFile

# # def get_image(request, image_id):
# #     try:
# #         imagine = Imagine.objects.get(id=image_id)
# #         imagine_path = imagine.imagine.path
# #         with default_storage.open(imagine_path, 'rb') as image_file:
# #             image_data = image_file.read()
# #         return JsonResponse({'success': True, 'image_data': image_data.decode('latin-1')})
# #     except Imagine.DoesNotExist:
# #         return JsonResponse({'success': False, 'message': 'Imaginea nu există'})

# def harta(request):
#     locations = Location.objects.all()
#     return render(request, 'map/afisareimag.html', {'locations': locations})


# def scrape_bizbrasov(request):
#     url = "https://www.bizbrasov.ro/2023/08/30/zilele-inteligentei-artificiale-2023-la-aula-universitatii/"
#     response = requests.get(url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Extrage URL-ul imaginii
#         image_element = soup.find('figure', class_='wp-block-image')
#         image_url = image_element.find('img')['src'] if image_element else None

#         # Conectare la MongoDB
#         client = MongoClient("mongodb://localhost:27017/")  
#         db = client["maps"]  
#         news_collection = db["CentruCivic"]  

#         # Adaugare imagine in baza de date
#         if image_url:
#             article_data = {
#                 'image_url': image_url,
#                 # Alte câmpuri relevante pot fi adăugate aici
#             }
#             news_collection.insert_one(article_data)

#         # Închiderea conexiunii la MongoDB
#         client.close()

#     return render(request, 'map/aula.html')


# def streetview(request):
#     locations = Location.objects.all()
#     return render(request, 'map/streetview.html', {'locations': locations})


from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
import base64
from io import BytesIO
from PIL import Image
from .models import Location

client = MongoClient("mongodb://localhost:27017/")
db = client["maps"]
colectie = db["CC"]

cale_imagini = [
    "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\aftar.jpg",
    "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\aula.jpg",
    "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\kruhnen.png",
    "C:\\Users\\rusuv\\Desktop\\teza\\harta\\maps\\centru_civic\\temple.png"
]

nume_imagini = ["Aftar Hours", "Aula UniTBv", "Kruhnen Musik Halle", "Temple"]

def adauga_imagini_in_db():
    for cale_imagine, nume_imagine in zip(cale_imagini, nume_imagini):
        # Verifică dacă imaginea există deja în colecție
        if colectie.find_one({"nume": nume_imagine}):
            continue

        with open(cale_imagine, "rb") as image_file:
            # Decodifică imaginea și comprimă-o
            imagine = Image.open(BytesIO(image_file.read()))
            buffer = BytesIO()
            imagine = imagine.convert('RGB')
            imagine.save(buffer, format="JPEG")
            content = buffer.getvalue()

        colectie.insert_one({"nume": nume_imagine, "imagine": content})

# Adaugă imaginile doar dacă nu există deja
adauga_imagini_in_db()

client.close()

def get_images(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["maps"]
    colectie = db["CC"]

    imagini = list(colectie.find({}, {'_id': 0}))

    for imagine in imagini:
        imagine['imagine'] = base64.b64encode(imagine['imagine']).decode('utf-8')

    client.close()

    return JsonResponse({'imagini': imagini})


def harta(request):
    locations = Location.objects.all()
    return render(request, 'map/afisareimag.html', {'locations': locations})


# def streetview(request):
#     locations = Location.objects.all()
#     return render(request, 'map/streetview.html', {'locations': locations})




