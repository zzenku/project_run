from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


class RunViewSet(ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=1)
        elif type == 'athlete':
            qs = qs.filter(is_staff=0)
        return qs.filter(is_superuser=False)


class RunStartView(APIView):
    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 0 and request.data['status'] == 1:
            run.status = request.data['status']
            run.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Забег начат'})
        raise ValueError


class RunStopView(APIView):
    def patch(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 1 and request.data['status'] == 2:
            run.status = request.data['status']
            run.save()
            return Response(status=status.HTTP_200_OK, data={'message': 'Забег завершён'})
        raise ValueError


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
