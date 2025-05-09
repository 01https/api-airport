from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
    Ticket
)

User = get_user_model()


class AirportAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123"
        )

        # Get JWT tokens for authentication
        self.user_token = self.get_token_for_user(self.user)
        self.admin_token = self.get_token_for_user(self.admin)

        self.airport1 = Airport.objects.create(
            name="Test Airport 1",
            closest_big_city="Test City 1"
        )
        self.airport2 = Airport.objects.create(
            name="Test Airport 2",
            closest_big_city="Test City 2"
        )

        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=10,
            seats_in_row=6,
            airplane_type=self.airplane_type
        )

        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=500
        )

        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe"
        )

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2023-01-01T10:00:00Z",
            arrival_time="2023-01-01T12:00:00Z"
        )
        self.flight.members.add(self.crew)

        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order
        )

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    # AirportViewSet Tests
    def test_airport_list_unauthenticated(self):
        url = reverse("airport:port-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_list_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:port-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination - response.data['results'] for PageNumberPagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)

    def test_airport_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:port-list")
        data = {
            "name": "New Airport",
            "closest_big_city": "New City"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 3)

    def test_airport_create_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:port-list")
        data = {
            "name": "New Airport",
            "closest_big_city": "New City"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:port-detail", args=[self.airport1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.airport1.name)

    # AirplaneTypeViewSet Tests
    def test_airplane_type_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:airplanes-type-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_airplane_type_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:airplanes-type-list")
        data = {"name": "Airbus A320"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AirplaneType.objects.count(), 2)

    # AirplaneViewSet Tests
    def test_airplane_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:airplanes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_airplane_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:airplanes-detail", args=[self.airplane.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.airplane.name)

    def test_airplane_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:airplanes-list")

        # Створюємо новий тип літака для тесту
        airplane_type = AirplaneType.objects.create(name="Airbus A380")

        data = {
            "name": "New Airplane 787",
            "rows": 30,
            "seats_in_row": 9,
            "airplane_type": airplane_type.name  # Змінили з id на name
        }

        response = self.client.post(url, data, format='json')

        # Діагностичний вивід у разі помилки
        if response.status_code != status.HTTP_201_CREATED:
            print("Validation errors:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airplane.objects.count(), 2)

    # RouteViewSet Tests
    def test_route_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:routes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            data = response.data['results']
            self.assertEqual(len(data), 1)
            # Check that list serializer is used
            self.assertIn("source_airport", data[0])
            self.assertIn("destination_airport", data[0])
        else:
            self.assertEqual(len(response.data), 1)
            self.assertIn("source_airport", response.data[0])
            self.assertIn("destination_airport", response.data[0])

    def test_route_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:routes-detail", args=[self.route.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that detail serializer is used
        self.assertIn("source_airport", response.data)
        self.assertIn("destination_airport", response.data)
        self.assertIn("distance", response.data)

    def test_route_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:routes-list")
        data = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 600
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 2)

    # FlightViewSet Tests
    def test_flight_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:flights-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            data = response.data['results']
            self.assertEqual(len(data), 1)
            self.assertIn("route", data[0])
            self.assertIn("airplane", data[0])
        else:
            self.assertEqual(len(response.data), 1)
            self.assertIn("route", response.data[0])
            self.assertIn("airplane", response.data[0])

    def test_flight_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:flights-detail", args=[self.flight.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that detail serializer is used
        self.assertIn("route", response.data)
        self.assertIn("airplane", response.data)
        self.assertIn("members", response.data)
        self.assertIn("available_seats", response.data)

    def test_flight_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:flights-list")
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": "2023-01-02T10:00:00Z",
            "arrival_time": "2023-01-02T12:00:00Z",
            "members": [self.crew.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)

    # CrewViewSet Tests
    def test_crew_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:crews-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_crew_create_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse("airport:crews-list")
        data = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 2)

    # OrderViewSet Tests
    def test_order_list_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:orders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination
        if 'results' in response.data:
            data = response.data['results']
            self.assertEqual(len(data), 1)
            self.assertIn("id", data[0])
            self.assertIn("created_at", data[0])
        else:
            self.assertEqual(len(response.data), 1)
            self.assertIn("id", response.data[0])
            self.assertIn("created_at", response.data[0])

    def test_order_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:orders-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that retrieve serializer is used
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("tickets", response.data)
        self.assertEqual(len(response.data["tickets"]), 1)

    def test_order_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse("airport:orders-list")
        data = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 2,
                    "flight": self.flight.id
                }
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_order_list_unauthenticated(self):
        url = reverse("airport:orders-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_access_other_user(self):
        new_user = User.objects.create_user(
            email="newuser@example.com",
            password="newpass123"
        )
        new_user_token = self.get_token_for_user(new_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_user_token}')
        url = reverse("airport:orders-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)