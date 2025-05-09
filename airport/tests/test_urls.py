from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from airport.views import *

class TestUrls(APITestCase):
    def test_airport_urls(self):
        url = reverse('airport:port-list')
        self.assertEqual(resolve(url).view_name, 'airport:port-list')
        self.assertEqual(resolve(url).func.cls, AirportViewSet)

    def test_airplane_urls(self):
        url = reverse('airport:airplanes-list')
        self.assertEqual(resolve(url).view_name, 'airport:airplanes-list')
        self.assertEqual(resolve(url).func.cls, AirplaneViewSet)

    def test_airplane_type_urls(self):
        url = reverse('airport:airplanes-type-list')
        self.assertEqual(resolve(url).view_name, 'airport:airplanes-type-list')
        self.assertEqual(resolve(url).func.cls, AirPlaneTypeViewSet)

    def test_route_urls(self):
        url = reverse('airport:routes-list')
        self.assertEqual(resolve(url).view_name, 'airport:routes-list')
        self.assertEqual(resolve(url).func.cls, RouteViewSet)

    def test_flight_urls(self):
        url = reverse('airport:flights-list')
        self.assertEqual(resolve(url).view_name, 'airport:flights-list')
        self.assertEqual(resolve(url).func.cls, FlightViewSet)

    def test_order_urls(self):
        url = reverse('airport:orders-list')
        self.assertEqual(resolve(url).view_name, 'airport:orders-list')
        self.assertEqual(resolve(url).func.cls, OrderViewSet)

    def test_crew_urls(self):
        url = reverse('airport:crews-list')
        self.assertEqual(resolve(url).view_name, 'airport:crews-list')
        self.assertEqual(resolve(url).func.cls, CrewViewSet)

    def test_url_patterns_count(self):
        from airport.urls import router
        self.assertEqual(len(router.registry), 7)