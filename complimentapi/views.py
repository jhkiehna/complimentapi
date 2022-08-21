from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


class AuthViewSet(viewsets.GenericViewSet):
    """
    A viewset for auth actions.
    """

    @action(detail=False, methods=['get'], name='Login')
    def login(self, request):
        
        return Response({'test': 'test'})