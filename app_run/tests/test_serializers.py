from django.contrib.auth.models import User
from django.test import TestCase

from app_run.models import Run
from app_run.serializers import RunSerializer


class RunSerializerTestCase(TestCase):
    def test_ok(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status=0)
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status=1)
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status=0)

        runs = Run.objects.all().select_related('athlete')
        data = RunSerializer(runs, many=True).data
        expected_data = [
            {
                'id': self.run_1.id,
                'athlete_data': {
                    'id': 1,
                    'username': 'us1',
                    'last_name': 'Sidorov',
                    'first_name': 'Ivan'
                },
                'created_at': data[0]['created_at'],
                'comment': '',
                'status': 0,
                'athlete': self.athlete_1.id
            },
            {
                'id': self.run_2.id,
                'athlete_data': {
                    'id': 2,
                    'username': 'us2',
                    'last_name': 'Petrov',
                    'first_name': 'Petr'
                },
                'created_at': data[0]['created_at'],
                'comment': '',
                'status': 1,
                'athlete': self.athlete_2.id
            },
            {
                'id': self.run_3.id,
                'athlete_data': {
                    'id': 3,
                    'username': 'us3',
                    'last_name': 'Ivanov',
                    'first_name': 'Sidor'
                },
                'created_at': data[0]['created_at'],
                'comment': '',
                'status': 0,
                'athlete': self.athlete_3.id
            }
        ]
        print(data)
        self.assertEqual(data, expected_data)