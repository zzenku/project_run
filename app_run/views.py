from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Sum, Max, Min, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import load_workbook
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from app_run.distance import calculate_distance
from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, \
    PositionSerializer, CollectibleItemSerializer, UserDetailSerializer


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
    queryset = User.objects.all().annotate(runs_finished=Count('id'), filter=Q(run__status='finished'))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = RunUserPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()

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
            run.distance = calculate_distance(run)
            run.save()
            finished_runs = Run.objects.filter(athlete=run.athlete, status='finished')
            finished_runs_data = finished_runs.aggregate(Count('id'), Sum('distance'))
            if finished_runs_data.get('id__count') == 10 and not Challenge.objects.filter(
                    athlete=run.athlete,
                    full_name='Сделай 10 Забегов!').exists():
                Challenge.objects.create(full_name='Сделай 10 Забегов!', athlete=run.athlete)
            if finished_runs_data.get('distance__sum') >= 50 and not Challenge.objects.filter(
                    athlete=run.athlete,
                    full_name='Пробеги 50 километров!').exists():
                Challenge.objects.create(full_name='Пробеги 50 километров!', athlete=run.athlete)
            duration = Position.objects.filter(run=run).aggregate(max_date=Max('date_time'), min_date=Min('date_time'))
            run.run_time_seconds = int((duration.get('max_date')-duration.get('min_date')).seconds)
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
def show_collectible_items(request):
    return Response(CollectibleItemSerializer(CollectibleItem.objects.all(), many=True).data)


@api_view(['POST'])
def upload_collectible_items(request):
    file = request.FILES.get('file')
    if not file:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Файл не передан'})

    xl = load_workbook(file)
    active_list = xl.active

    invalid_rows = []

    for row in active_list.iter_rows(min_row=2):
        row_data = {
            'name': row[0].value,
            'uid': row[1].value,
            'value': row[2].value,
            'latitude': row[3].value,
            'longitude': row[4].value,
            'picture': row[5].value
        }

        serializer = CollectibleItemSerializer(data=row_data)
        if serializer.is_valid():
            serializer.save()
        else:
            invalid_rows.append([i.value for i in row])

    return Response(status=status.HTTP_200_OK, data=invalid_rows)


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
