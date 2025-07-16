from django.test import TestCase
from django.contrib.auth import get_user_model
from airport.models import (
    Airport, Airplane, AirplaneType, Route,
    Flight, Order, Ticket, Crew
)
from django.utils.timezone import now, timedelta

User = get_user_model()


class ModelTests(TestCase):

    def test_create_airport(self):
        airport = Airport.objects.create(name="Test Airport", closest_big_city="City")
        self.assertEqual(str(airport), "Test Airport")

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(name="B737", rows=10, seats_in_row=6, airplane_type=airplane_type)
        self.assertEqual(str(airplane), "B737")

    def test_create_route(self):
        source = Airport.objects.create(name="A", closest_big_city="CityA")
        dest = Airport.objects.create(name="B", closest_big_city="CityB")
        route = Route.objects.create(source=source, destination=dest, distance=500)
        self.assertEqual(str(route), "A, B")

    def test_flight_properties(self):
        airplane_type = AirplaneType.objects.create(name="Airbus")
        airplane = Airplane.objects.create(name="A320", rows=5, seats_in_row=4, airplane_type=airplane_type)
        source = Airport.objects.create(name="X", closest_big_city="CityX")
        dest = Airport.objects.create(name="Y", closest_big_city="CityY")
        route = Route.objects.create(source=source, destination=dest, distance=800)
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2)
        )
        flight.members.add(crew)

        user = User.objects.create_user(email="test@test.com", password="testpass")
        order = Order.objects.create(user=user)
        Ticket.objects.create(flight=flight, order=order, row=1, seat=1)

        self.assertEqual(str(flight), "X, Y - A320")
        self.assertEqual(flight.available_seats, 5 * 4 - 1)
        self.assertEqual(flight.taken_seats_list, 1)
        self.assertIn({"row": 1, "seat": 1}, flight.taken_seats_detail)

    def test_order_str(self):
        user = User.objects.create_user(email="test@test.com", password="testpass")
        order = Order.objects.create(user=user)
        self.assertTrue(str(order).endswith(", test@test.com"))

    def test_ticket_str(self):
        airplane_type = AirplaneType.objects.create(name="Embraer")
        airplane = Airplane.objects.create(name="E190", rows=4, seats_in_row=4, airplane_type=airplane_type)
        source = Airport.objects.create(name="M", closest_big_city="CityM")
        dest = Airport.objects.create(name="N", closest_big_city="CityN")
        route = Route.objects.create(source=source, destination=dest, distance=600)
        flight = Flight.objects.create(route=route, airplane=airplane, departure_time=now(), arrival_time=now())
        user = User.objects.create_user(email="test@test.com", password="testpass")
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(row=2, seat=3, flight=flight, order=order)
        self.assertEqual(str(ticket), f"2, 3, {order}")

    def test_crew_full_name(self):
        crew = Crew.objects.create(first_name="Alice", last_name="Smith")
        self.assertEqual(crew.full_name, "Alice Smith")
        self.assertEqual(str(crew), "Alice Smith")