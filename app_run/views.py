from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from app_run.distance import calculate_distance
from app_run.models import Run, AthleteInfo, Challenge, Position
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, \
    PositionSerializer
from geopy.distance import geodesic


class RunUserPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    pagination_class = RunUserPagination


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['run']


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all().annotate(runs_finished=Count(Case(When(run__status='finished', then=1))))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = RunUserPagination

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=1)
        elif type == 'athlete':
            qs = qs.filter(is_staff=0)
        return qs.filter(is_superuser=False)


class RunStartView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Забег начат'})
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RunStopView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 'in_progress':
            run.status = 'finished'
            run.save()
            if Run.objects.filter(athlete=run.athlete,status='finished').count() == 10 and not Challenge.objects.filter(
                    athlete=run.athlete, full_name='Сделай 10 Забегов!').exists():
                Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=run.athlete)
            run.distance = calculate_distance(run)
            run.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Забег завершён'})
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AthleteInfoView(APIView):
    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = AthleteInfoSerializer(data=request.data)
        if serializer.is_valid():
            AthleteInfo.objects.update_or_create(user_id=user, defaults=serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED, data={'message': 'Данные успешно добавлены'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        info, created = AthleteInfo.objects.get_or_create(user_id=user, defaults={'weight': 0, 'goals': ''})
        serializer_data = AthleteInfoSerializer(info).data
        return Response(status=status.HTTP_200_OK, data=serializer_data)


@api_view(['GET'])
def show_challenges(request):
    challenges = Challenge.objects.all()
    athlete = request.GET.get('athlete')
    if athlete:
        challenges = challenges.filter(athlete=athlete)
    serializer_data = ChallengeSerializer(challenges, many=True).data
    return Response(serializer_data)


@api_view(['GET'])
def company_details_view(request):
    company_name = settings.COMPANY_NAME
    slogan = settings.SLOGAN
    contacts = settings.CONTACTS
    return Response({
        'company_name': company_name,
        'slogan': slogan,
        'contacts': contacts
    })
