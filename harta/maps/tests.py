from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
class MapViewsTestCase(TestCase):
   
    def test_harta_view(self):
        response = self.client.get(reverse('harta'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map/harta.html')

    def test_primaria_view(self):
        response = self.client.get(reverse('primaria'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map/primaria.html')

    @patch('maps.views.MongoClient')
    def test_get_all_events(self, mock_mongo_client):
        mock_collection = mock_mongo_client.return_value.maps.aulas
        mock_collection.find.return_value = [
            {'title': 'Event 1', 'description': 'Description 1'},
            {'title': 'Event 2', 'description': 'Description 2'}
        ]

        response = self.client.get(reverse('get_all_events'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['events']), 2)

    @patch('maps.views.webdriver')
    def test_cinema_city_view(self, mock_webdriver):
        mock_driver = mock_webdriver.Chrome.return_value
        mock_driver.page_source = '<div class="row qb-movie"><h3>Movie 1</h3></div>'

        response = self.client.get(reverse('cinema_city'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map/cinema_city.html')

   



   