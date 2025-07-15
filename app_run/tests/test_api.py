import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress')
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status='init')
        self.athlete_2_info = AthleteInfo.objects.create(user_id=self.athlete_2, weight=0, goals='')

    def test_get_runs(self):
        url = reverse('run-list')
        response = self.client.get(url)
        runs = Run.objects.all()
        serializer_data = RunSerializer(runs, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search_user(self):
        url = reverse('user-list')
        users = User.objects.filter(id__in=[self.athlete_1.id, self.athlete_3.id]).annotate(
            runs_finished=Count(Case(When(run__status='finished', then=1))))
        response = self.client.get(url, data={'search': 'Ivan'})
        serializer_data = UserSerializer(users, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_only_one(self):
        url = reverse('run-detail', args=(self.run_1.id,))
        response = self.client.get(url)
        runs = Run.objects.get(id=self.run_1.id)
        serializer_data = RunSerializer(runs).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_run_start(self):
        url = reverse('run-start', kwargs={'run_id': self.run_1.id})
        response = self.client.post(url, content_type='application/json')
        self.run_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('in_progress', self.run_1.status)

    def test_run_stop(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_2.id})
        response = self.client.post(url, content_type='application/json')
        self.run_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_2.status)

    def test_run_start_string(self):
        url = reverse('run-start', kwargs={'run_id': self.run_1.id})
        response = self.client.post(url, content_type='application/json')
        self.run_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('in_progress', self.run_1.status)

    def test_run_stop_string(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_2.id})
        response = self.client.post(url, content_type='application/json')
        self.run_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_2.status)

    def test_get_athlete_info_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_athlete_info_not_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_1.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200, response.status_code)

    def test_put_athlete_info_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
        data = {
            'weight': 80,
            'goals': 'Хочу быть сильным'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.athlete_2_info.refresh_from_db()
        expected_data = {
            'weight': self.athlete_2_info.weight,
            'goals': self.athlete_2_info.goals
        }
        serializer_data = AthleteInfoSerializer(self.athlete_2_info).data
        self.assertEqual(data, expected_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_put_athlete_info_not_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_1.id})
        data = {
            'weight': 80,
            'goals': 'Хочу быть сильным'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        info = AthleteInfo.objects.get(user_id=self.athlete_1.id)
        expected_data = {
            'weight': info.weight,
            'goals': info.goals
        }
        self.assertEqual(data, expected_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_weight_type_error(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
        data = {
            'weight': 'abc',
            'goals': 'Хочу быть сильным'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.athlete_2_info.refresh_from_db()
        expected_data = {
            'weight': self.athlete_2_info.weight,
            'goals': self.athlete_2_info.goals
        }
        serializer_data = AthleteInfoSerializer(self.athlete_2_info).data
        self.assertEqual(data, expected_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
