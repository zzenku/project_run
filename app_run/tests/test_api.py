import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress')
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status='init')

    def test_get_runs(self):
        url = reverse('run-list')
        response = self.client.get(url)
        runs = Run.objects.all()
        serializer_data = RunSerializer(runs, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search_user(self):
        url = reverse('user-list')
        users = User.objects.filter(id__in=[self.athlete_1.id, self.athlete_3.id])
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
        data = {'status': 'in_progress'}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.run_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('in_progress', self.run_1.status)

    def test_run_stop(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_2.id})
        data = {'status': 'finished'}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.run_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_2.status)

    def test_run_start_string(self):
        url = reverse('run-start', kwargs={'run_id': self.run_1.id})
        data = {'status': 'in_progress'}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.run_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('in_progress', self.run_1.status)

    def test_run_stop_string(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_2.id})
        data = {'status': 'finished'}
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.run_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_2.status)

