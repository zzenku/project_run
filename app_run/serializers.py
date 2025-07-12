from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from app_run.models import Run


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


class AthleteSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(ModelSerializer):
    athlete_data = AthleteSerializer(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = ['id', 'athlete_data', 'created_at', 'comment']
