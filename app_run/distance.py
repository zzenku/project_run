from geopy.distance import geodesic

from app_run.models import Position


def calculate_distance(run):
    positions_list = [[i.latitude, i.longitude] for i in Position.objects.filter(run=run)]
    distance = 0
    for i in range(len(positions_list) - 1):
        distance += geodesic(positions_list[i], positions_list[i + 1]).km
    return distance
