from django.contrib.auth.models import User
from geopy.distance import geodesic
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from app_run.distance import calculate_distance
from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class CollectibleItemSerializer(ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['name', 'uid', 'latitude', 'longitude', 'picture', 'value']

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Недопустимое значение широты')
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Недопустимое значение долготы')
        return value


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()
    runs_finished = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


class UserDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['items']


class AthleteSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(ModelSerializer):
    athlete_data = AthleteSerializer(read_only=True, source='athlete')

    class Meta:
        model = Run
        fields = ['created_at', 'athlete', 'comment', 'status', 'distance', 'run_time_seconds', 'speed']


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
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')

    class Meta:
        model = Position
        fields = ['run', 'latitude', 'longitude', 'date_time', 'speed', 'distance']
        read_only_fields = ['distance', 'speed']

    def create(self, validated_data):
        athlete_position = [validated_data.get('latitude'), validated_data.get('longitude')]
        athlete = validated_data.get('run').athlete
        for item in CollectibleItem.objects.all():
            if geodesic(athlete_position, [item.latitude, item.longitude]).m <= 100:
                athlete.items.add(item)
        return super().create(validated_data)

    def validate_run(self, value):
        if value.status != 'in_progress':
            raise serializers.ValidationError('Забег не запущен')
        return value

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Недопустимое значение широты')
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Недопустимое значение долготы')
        return value
