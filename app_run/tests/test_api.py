import json
import time
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from geopy.distance import geodesic
from rest_framework import status
from rest_framework.test import APITestCase

from app_run.distance import calculate_distance
from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem, Subscribe
from app_run.serializers import RunSerializer, UserSerializer, ChallengeSerializer, AthleteInfoSerializer


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.athlete_1 = User.objects.create(username='us1', first_name='Ivan', last_name='Sidorov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Petr', last_name='Petrov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Sidor', last_name='Ivanov')
        self.run_1 = Run.objects.create(athlete=self.athlete_1, status='init')
        self.run_2 = Run.objects.create(athlete=self.athlete_2, status='in_progress')
        self.run_3 = Run.objects.create(athlete=self.athlete_3, status='init')
        self.run_4 = Run.objects.create(athlete=self.athlete_3, status='in_progress')
        self.position_1 = Position.objects.create(run=self.run_4, latitude=0, longitude=0,
                                                  date_time='2025-08-08T14:05:00.00')
        self.position_2 = Position.objects.create(run=self.run_4, latitude=1, longitude=1,
                                                  date_time='2025-08-08T14:05:01.00')
        self.position_3 = Position.objects.create(run=self.run_4, latitude=2, longitude=2,
                                                  date_time='2025-08-08T14:05:02.00')
        self.position_4 = Position.objects.create(run=self.run_4, latitude=3, longitude=3,
                                                  date_time='2025-08-08T14:05:03.00')
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
        users = User.objects.all().annotate(runs_finished=Count('run', filter=Q(run__status='finished')))
        response = self.client.get(url, data={'search': 'Ivan'})
        serializer_data = UserSerializer([users.get(pk=1), users.get(pk=3)], many=True).data
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
        self.assertTrue(3 <= self.run_4.run_time_seconds <= 5)

    def test_get_athlete_info_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_athlete_info_not_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_1.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_put_athlete_info_created(self):
        url = reverse('athlete-info', kwargs={'user_id': self.athlete_2.id})
        data = {
            'weight': 80,
            'goals': 'Хочу быть сильным'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.athlete_2_info.refresh_from_db()
        serializer_data = AthleteInfoSerializer(self.athlete_2_info).data
        data['user_id'] = self.athlete_2.id
        self.assertEqual(data, serializer_data)
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

        serializer = AthleteInfoSerializer(self.athlete_2_info)
        self.assertNotEqual(data, serializer.data)
        self.assertNotEqual(status.HTTP_201_CREATED, response.status_code)

    def test_speed_distance(self):
        athlete = User.objects.create_user(username='user', password='test1234')
        run = Run.objects.create(athlete=athlete, status='in_progress')

        url = reverse('position-list')

        for i in range(10):
            data = {
                'run': run.id,
                'latitude': i,
                'longitude': i,
                'date_time': timezone.now().isoformat()
            }
            response = self.client.post(url, data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            time.sleep(0.01)

        positions = Position.objects.filter(run=run).order_by('date_time')
        self.assertEqual(positions.count(), 10)

        for p in positions:
            # print(f"Lat: {p.latitude}, Lon: {p.longitude}, Speed: {p.speed}, Distance: {p.distance}")
            self.assertIsNotNone(p.speed)
            self.assertIsNotNone(p.distance)
            self.assertIsInstance(p.speed, Decimal)
            self.assertIsInstance(p.distance, Decimal)


class ChallengeApiTestCase(APITestCase):
    def setUp(self):
        self.athlete = User.objects.create(username='us1', first_name='Ivan', last_name='Ivanov')
        self.athlete_2 = User.objects.create(username='us2', first_name='Ivan', last_name='Sidorov')
        self.athlete_3 = User.objects.create(username='us3', first_name='Ivan', last_name='Govnov')
        for _ in range(9):
            Run.objects.create(athlete=self.athlete, status='finished', distance=5)
        self.run_10 = Run.objects.create(athlete=self.athlete, status='in_progress', distance=5)
        Position.objects.create(run=self.run_10, latitude=0, longitude=0)
        Position.objects.create(run=self.run_10, latitude=0, longitude=0.05)
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
        self.run_10.refresh_from_db()
        self.assertTrue(Challenge.objects.filter(athlete=self.athlete, full_name=Challenge.CHALLENGE_50KM).exists())

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
        url = reverse('position-list')
        data = {'run': run.id, 'latitude': 20, 'longitude': 20, 'date_time': '2025-08-08T14:05:03.00'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(athlete.items.last(), item)


class ExtraApiTestCase(APITestCase):
    def setUp(self):
        self.coach = User.objects.create(username='coach', is_staff=True)
        self.athlete = User.objects.create(username='athlete')
        self.other_athlete = User.objects.create(username='athlete2')

        self.subscription = Subscribe.objects.create(coach=self.coach, athlete=self.athlete, rating=5)

        self.run1 = Run.objects.create(athlete=self.athlete, status='finished', distance=5, speed=10)
        self.run2 = Run.objects.create(athlete=self.athlete, status='finished', distance=15, speed=8)

        self.item = CollectibleItem.objects.create(
            name='Test Item', uid='abc123', value=10, latitude=0, longitude=0, picture='test.png'
        )

        self.challenge = Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=self.athlete)

    def test_analytics_for_coach_success(self):
        url = reverse('analytics-coach', kwargs={'id': self.coach.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('longest_run_user', response.data)

    def test_analytics_for_coach_not_found(self):
        url = reverse('analytics-coach', kwargs={'id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rate_coach_success(self):
        url = reverse('rate-coach', kwargs={'id': self.coach.id})
        data = {'athlete': self.athlete.id, 'rating': 4}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.rating, 4)

    def test_rate_coach_not_subscribed(self):
        url = reverse('rate-coach', kwargs={'id': self.coach.id})
        data = {'athlete': self.other_athlete.id, 'rating': 5}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_challenge_summary(self):
        url = reverse('challenge-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any('athletes' in c for c in response.data))

    def test_subscribe_success(self):
        new_athlete = User.objects.create(username='new_athlete')
        url = reverse('subscribe', kwargs={'id': self.coach.id})
        data = {'athlete': new_athlete.id}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscribe.objects.filter(athlete=new_athlete, coach=self.coach).exists())

    def test_subscribe_already_exists(self):
        url = reverse('subscribe', kwargs={'id': self.coach.id})
        data = {'athlete': self.athlete.id}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_users_by_type(self):
        url = reverse('user-list')
        response = self.client.get(url, {'type': 'coach'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(u['type'] == 'coach' for u in response.data))

    def test_show_collectible_items(self):
        url = reverse('show-collectible-items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_show_challenges_filter_by_athlete(self):
        url = reverse('challenge-list')
        response = self.client.get(url, {'athlete': self.athlete.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(c['athlete'] == self.athlete.id for c in response.data))
