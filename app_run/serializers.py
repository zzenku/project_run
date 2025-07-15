from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from app_run.models import Run, AthleteInfo


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()
    runs_finished = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

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
        fields = '__all__'


class AthleteInfoSerializer(ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = ['user_id', 'weight', 'goals']

    def validate_weight(self, value):
        if 0 < value < 900:
                return value
        raise serializers.ValidationError('Недопустимое значение')
