import json
import time

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.test import TestCase
from django.urls import reverse
from geopy.distance import geodesic
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.distance import calculate_distance
from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, ChallengeSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress')
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status='init')
        self.run_4 = Run.objects.create(athlete=self.athlete_3, status='in_progress')
        self.position_1 = Position.objects.create(run=self.run_4, latitude=0, longitude=0)
        time.sleep(2)
        self.position_2 = Position.objects.create(run=self.run_4, latitude=1, longitude=1)
        time.sleep(2)
        self.position_3 = Position.objects.create(run=self.run_4, latitude=2, longitude=2)
        time.sleep(2)
        self.position_4 = Position.objects.create(run=self.run_4, latitude=3, longitude=3)
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

    def test_time_run(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_4.id})
        response = self.client.post(url, content_type='application/json')
        self.run_4.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(5 <= self.run_4.run_time_seconds <= 7)

    # def test_get_athlete_info_created(self):
    #     url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
    #     response = self.client.get(url)
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #
    # def test_get_athlete_info_not_created(self):
    #     url = reverse('athlete-info', kwargs={'user_id': self.athlete_1.id})
    #     response = self.client.get(url)
    #     self.assertEqual(status.HTTP_200, response.status_code)
    #
    # def test_put_athlete_info_created(self):
    #     url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
    #     data = {
    #         'weight': 80,
    #         'goals': 'Хочу быть сильным'
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.athlete_2_info.refresh_from_db()
    #     expected_data = {
    #         'weight': self.athlete_2_info.weight,
    #         'goals': self.athlete_2_info.goals
    #     }
    #     serializer_data = AthleteInfoSerializer(self.athlete_2_info).data
    #     self.assertEqual(data, expected_data)
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #
    # def test_put_athlete_info_not_created(self):
    #     url = reverse('athlete-info', kwargs={'user_id': self.athlete_1.id})
    #     data = {
    #         'weight': 80,
    #         'goals': 'Хочу быть сильным'
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     info = AthleteInfo.objects.get(user_id=self.athlete_1.id)
    #     expected_data = {
    #         'weight': info.weight,
    #         'goals': info.goals
    #     }
    #     self.assertEqual(data, expected_data)
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #
    # def test_weight_type_error(self):
    #     url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
    #     data = {
    #         'weight': 'abc',
    #         'goals': 'Хочу быть сильным'
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.athlete_2_info.refresh_from_db()
    #     expected_data = {
    #         'weight': self.athlete_2_info.weight,
    #         'goals': self.athlete_2_info.goals
    #     }
    #     serializer_data = AthleteInfoSerializer(self.athlete_2_info).data
    #     self.assertEqual(data, expected_data)
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)


class ChallengeApiTestCase(APITestCase):
    def setUp(self):
        self.athlete = User.objects.create(username='us1', first_name='Ivan', last_name='Ivanov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Ivan', last_name='Sidorov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Ivan', last_name='Govnov')
        for _ in range(9):
            Run.objects.create(athlete=self.athlete, status='finished', distance=5)
        self.run_10 = Run.objects.create(athlete=self.athlete, status='in_progress', distance=5)
        self.challenge_2 = Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=self.athlete_2)
        self.challenge_3 = Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=self.athlete_3)

    def test_complete_challenge_10(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_10.id})
        response = self.client.post(url)
        self.run_10.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_10.status)
        self.assertEqual('Сделай 10 Забегов!', Challenge.objects.filter(athlete=self.athlete)[0].full_name)

    def test_complete_challenge_50km(self):
        url = reverse('run-stop', kwargs={'run_id': self.run_10.id})
        response = self.client.post(url)
        self.run_10.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('finished', self.run_10.status)
        self.assertTrue(Challenge.objects.filter(athlete=self.athlete, full_name='Пробеги 50 километров!').exists())

    def test_get_challenges(self):
        url = reverse('challenge-list')
        response = self.client.get(url)
        serializer_data = ChallengeSerializer([self.challenge_2, self.challenge_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class LogicTestCase(TestCase):
    def test_distance(self):
        athlete = User.objects.create(username='us', first_name='Ivan', last_name='Ivanov')
        run_1 = Run.objects.create(athlete=athlete, status='in_progress')
        test_pos_1 = Position.objects.create(run=run_1, latitude=12, longitude=50)
        test_pos_2 = Position.objects.create(run=run_1, latitude=12.10, longitude=50.05)
        test_pos_3 = Position.objects.create(run=run_1, latitude=12.20, longitude=50.1)
        test_pos_4 = Position.objects.create(run=run_1, latitude=12.30, longitude=50.15)

        d = 0
        d += geodesic([test_pos_1.latitude, test_pos_1.longitude], [test_pos_2.latitude, test_pos_2.longitude]).km
        d += geodesic([test_pos_2.latitude, test_pos_2.longitude], [test_pos_3.latitude, test_pos_3.longitude]).km
        d += geodesic([test_pos_3.latitude, test_pos_3.longitude], [test_pos_4.latitude, test_pos_4.longitude]).km

        self.assertEqual(d, calculate_distance(run_1))


class PositionCollectibleTestCase(TestCase):
    def test_collectible_items_added(self):
        athlete = User.objects.create(username='us', first_name='Ivan', last_name='Ivanov')

        item = CollectibleItem.objects.create(name='col_item', uid='abcd1234', latitude=20, longitude=20,
                                              picture='https://info.traceparts.com/wp-content/uploads/2024/01/item-logo-without-background-2.png',
                                              value=2)
        run = Run.objects.create(athlete=athlete, status='in_progress')
        test_pos_1 = Position.objects.create(run=run, latitude=10, longitude=10)
        test_pos_2 = Position.objects.create(run=run, latitude=12, longitude=12)
        test_pos_3 = Position.objects.create(run=run, latitude=14, longitude=14)
        url = reverse('position-list')
        data = {'run': run.id, 'latitude': 20, 'longitude': 20}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(athlete.items.last(), item)

