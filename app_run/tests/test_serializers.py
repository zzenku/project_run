from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.test import TestCase

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


class RunSerializerTestCase(TestCase):
    def test_run_ok(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init', run_time_seconds=0)
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress', run_time_seconds=0)
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status='finished', run_time_seconds=0)
        runs = Run.objects.all().select_related('athlete').order_by('id')
        data = RunSerializer(runs, many=True).data
        expected_data = [
            {
                'id': self.run_1.id,
                'athlete_data': {
                    'id': self.athlete_1.id,
                    'username': 'us1',
                    'last_name': 'Sidorov',
                    'first_name': 'Ivan'
                },
                'created_at': data[0]['created_at'],
                'comment': '',
                'status': 'init',
                'distance': '0.0000',
                'run_time_seconds': 0,
                'athlete': self.athlete_1.id,
            },
            {
                'id': self.run_2.id,
                'athlete_data': {
                    'id': self.athlete_2.id,
                    'username': 'us2',
                    'last_name': 'Petrov',
                    'first_name': 'Petr'
                },
                'created_at': data[1]['created_at'],
                'comment': '',
                'status': 'in_progress',
                'distance': '0.0000',
                'run_time_seconds': 0,
                'athlete': self.athlete_2.id,
            },
            {
                'id': self.run_3.id,
                'athlete_data': {
                    'id': self.athlete_3.id,
                    'username': 'us3',
                    'last_name': 'Ivanov',
                    'first_name': 'Sidor'
                },
                'created_at': data[2]['created_at'],
                'comment': '',
                'status': 'finished',
                'distance': '0.0000',
                'run_time_seconds': 0,
                'athlete': self.athlete_3.id,

            }
        ]
        print(data)
        print('\n', expected_data)
        self.assertEqual(data, expected_data)


class UserSerializerTestCase(TestCase):
    def test_athlete_ok(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress', distance=0, run_time_seconds=0)
        self.run_3 = Run.objects.create(athlete=self.athlete_1, status='in_progress', distance=0, run_time_seconds=0)
        self.run_4 = Run.objects.create(athlete=self.athlete_1, status='finished', distance=0, run_time_seconds=0)
        self.run_5 = Run.objects.create(athlete=self.athlete_2, status='finished', distance=0, run_time_seconds=0)
        self.run_6 = Run.objects.create(athlete=self.athlete_2, status='finished', distance=0, run_time_seconds=0)
        self.run_7 = Run.objects.create(athlete=self.athlete_3, status='finished', distance=0, run_time_seconds=0)
        self.run_8 = Run.objects.create(athlete=self.athlete_3, status='finished', distance=0, run_time_seconds=0)
        self.run_9 = Run.objects.create(athlete=self.athlete_3, status='finished', distance=0, run_time_seconds=0)

        users = User.objects.all().annotate(runs_finished=Count(Case(When(run__status='finished', then=1))))
        data = UserSerializer(users, many=True).data
        expected_data = [
            {
                'id': 1,
                'date_joined': data[0]['date_joined'],
                'username': self.athlete_1.username,
                'last_name': 'Sidorov',
                'first_name': 'Ivan',
                'type': 'athlete',
                'runs_finished': 1
            },
            {
                'id': 2,
                'date_joined': data[1]['date_joined'],
                'username': self.athlete_2.username,
                'last_name': 'Petrov',
                'first_name': 'Petr',
                'type': 'athlete',
                'runs_finished': 2
            },
            {
                'id': 3,
                'date_joined': data[2]['date_joined'],
                'username': self.athlete_3.username,
                'last_name': 'Ivanov',
                'first_name': 'Sidor',
                'type': 'athlete',
                'runs_finished': 3
            }
        ]
        self.assertEqual(data, expected_data)
