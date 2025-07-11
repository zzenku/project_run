from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def company_details_view(request):
    return Response({
        'company_name': 'Раз-Бег!',
        'slogan': 'Крылатые атлеты начинают свой разбег!',
        'contacts': 'Город Атлантида, улица Карла Маркса, дом 52'
    })
