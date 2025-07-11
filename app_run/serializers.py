from rest_framework.serializers import ModelSerializer

from app_run.models import Run


class RunSerializer(ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'