from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from app_run.models import Run


class RunSerializer(ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'
