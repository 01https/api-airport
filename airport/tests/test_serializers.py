from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from airport.models import *
from airport.serializers import *

User = get_user_model()


class SerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass")

        self.airport1 = Airport.objects.create(name="A1", closest_big_city="C1")
        self.airport2 = Airport.objects.create(name="A2", closest_big_city="C2")
        self.airplane_type = AirplaneType.objects.create(name="TypeX")
        self.airplane = Airplane.objects.create(
            name="Plane1", rows=5, seats_in_row=4, airplane_type=self.airplane_type
        )
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2, distance=500)
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=now(),
            arrival_time=now() + timedelta(hours=2),
        )

    def test_airport_serializer(self):
        serializer = AirportSerializer(instance=self.airport1)
        self.assertEqual(serializer.data["name"], "A1")

    def test_airplane_serializer(self):
        serializer = AirplaneSerializer(instance=self.airplane)
        self.assertEqual(serializer.data["airplane_type"], "TypeX")

    def test_route_list_serializer(self):
        serializer = RouteListSerializer(instance=self.route)
        self.assertEqual(serializer.data["source_airport"], "A1")
        self.assertEqual(serializer.data["destination_airport"], "A2")

    def test_flight_serializer_fields(self):
        serializer = FlightSerializer(instance=self.flight)
        self.assertEqual(serializer.data["airplane_type"], "TypeX")
        self.assertEqual(serializer.data["departure"], "A1")
        self.assertEqual(serializer.data["arrival"], "A2")
        self.assertEqual(serializer.data["distance"], 500)
        self.assertEqual(serializer.data["row"], 5)
        self.assertEqual(serializer.data["seat_in_row"], 4)
        self.assertEqual(serializer.data["available_seats"], 20)

    def test_ticket_serializer_valid(self):
        data = {"row": 1, "seat": 1, "flight": self.flight.id}
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_ticket_serializer_invalid_taken(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(row=1, seat=1, flight=self.flight, order=order)
        data = {"row": 1, "seat": 1, "flight": self.flight.id}
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("taken_seats", serializer.errors)

    def test_ticket_serializer_invalid_bounds(self):
        data = {"row": 10, "seat": 5, "flight": self.flight.id}  # out of range
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("row", serializer.errors)
        self.assertIn("seat", serializer.errors)

    def test_order_serializer_create(self):
        data = {
            "tickets": [
                {"row": 2, "seat": 3, "flight": self.flight.id}
            ]
        }
        serializer = OrderSerializer(data=data, context={"request": None})
        serializer.context["request"] = type("Request", (), {"user": self.user})()
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save(user=self.user)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_crew_serializer(self):
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        serializer = CrewSerializer(instance=crew)
        self.assertEqual(serializer.data["first_name"], "John")
        self.assertEqual(serializer.data["last_name"], "Doe")