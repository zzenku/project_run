from django.contrib import admin

from app_run.models import Run, Challenge, AthleteInfo, Position

admin.site.register(Run)
admin.site.register(AthleteInfo)
admin.site.register(Challenge)
admin.site.register(Position)