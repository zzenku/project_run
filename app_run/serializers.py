from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from app_run.models import Run, AthleteInfo, Challenge, Position


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
        read_only_fields = ['user_id']

    def validate_weight(self, value):
        if 0 < value < 900:
            return value
        raise serializers.ValidationError('Недопустимое значение')


class ChallengeSerializer(ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['full_name', 'athlete']


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = ['run', 'latitude', 'longitude']

    def validate_run(self, value):
        if value.status != 'in_progress':
            raise serializers.ValidationError('Забег не запущен')
        return value

    def validate(self, data):
        latitude = data['latitude']
        longitude = data['longitude']
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise serializers.ValidationError('Недопустимое значение координат')
        return data




