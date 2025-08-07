"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import company_details_view, RunViewSet, UserViewSet, RunStartView, RunStopView, AthleteInfoView, \
    show_challenges, PositionViewSet, show_collectible_items, upload_collectible_items, SubscribeView, \
    ChallengeSummaryView, RateCoachView

router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)
router.register('api/positions', PositionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details_view),
    path('api/runs/<int:run_id>/start/', RunStartView.as_view(), name='run-start'),
    path('api/runs/<int:run_id>/stop/', RunStopView.as_view(), name='run-stop'),
    path('api/athlete_info/<int:user_id>/', AthleteInfoView.as_view(), name='athlete-info'),
    path('api/challenges/', show_challenges, name='challenge-list'),
    path('api/collectible_item/', show_collectible_items),
    path('api/upload_file/', upload_collectible_items),
    path('api/subscribe_to_coach/<int:id>/', SubscribeView.as_view()),
    path('api/challenges_summary/', ChallengeSummaryView.as_view()),
    path('api/rate_coach/<int:id>/', RateCoachView.as_view()),
    path('', include(router.urls)),
]
