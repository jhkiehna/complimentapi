import os
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from complimentapi.models import Receiver, User
from complimentapi.serializers import UserSerializer, ReceiverSerializer
from complimentapi.permissions import OwnsReceiver

import logging
logger = logging.getLogger('django')

oauth_client_id: str = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
oauth_client_secret: str = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
redirect_uri: str = 'http://localhost:8000/auth/oauth_callback'
scopes: list = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


class AuthViewSet(viewsets.GenericViewSet):
    """
    A viewset for auth actions.
    """

    @action(detail=False, methods=['get'], name='Login')
    def login(self, request: Request) -> Response:
        oauth_url: str = 'https://accounts.google.com/o/oauth2/v2/auth?include_granted_scopes=true' \
            '&scope={}' \
            '&redirect_uri={}' \
            '&client_id={}' \
            '&response_type=code' \
            .format(' '.join(scopes), redirect_uri, oauth_client_id)

        return Response(headers={'Location': oauth_url}, status=302)

    @action(detail=False, methods=['get'], name='OAuth Callback')
    def oauth_callback(self, request: Request) -> Response:
        try:
            # Check access denied or no code
            if request.query_params.get('error') == 'access_denied' or not request.query_params.get('code'):
                return Response(401)

            # Make request for access token and get user info
            token_response_data = requests.post(
                'https://oauth2.googleapis.com/token',
                {
                    'client_id': oauth_client_id,
                    'client_secret': oauth_client_secret,
                    'code': request.query_params.get('code'),
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                }
            ).json()

            user_info = requests.get(
                'https://www.googleapis.com/userinfo/v2/me',
                headers={'Authorization': 'Bearer {}'.format(token_response_data.get('access_token'))}
            ).json()

            if user_info.get('error'):
                logger.info(user_info)
                raise Exception('something went wrong')

            # Get or create user
            user, _ = User.objects.get_or_create(
                email=user_info.get('email'), defaults={
                    'first_name': user_info.get('given_name'),
                    'last_name': user_info.get('family_name')
                }
            )

            # Create jwt to client
            refresh = RefreshToken.for_user(user)

            # In production, this would be changed to a redirect to the frontend, with the token in a qs param
            return Response({'access': str(refresh.access_token)}, 200)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response(500)

    @action(detail=False, methods=['get'], name='Me', permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data, 200)


class ReceiverViewSet(viewsets.ViewSet):
    """
    Viewset for Receiver actions.
    """
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = super().get_permissions()

        if self.action in ['retrieve', 'update']:
            permissions.append(OwnsReceiver())

        return permissions

    def list(self, request: Request) -> Response:
        queryset = Receiver.objects.filter(user=request.user)
        return Response(ReceiverSerializer(queryset, many=True).data)

    def retrieve(self, request: Request, pk: int = None) -> Response:
        return Response(ReceiverSerializer(Receiver.objects.get(id=pk)).data)

    def create(self, request: Request) -> Response:
        serializer = ReceiverSerializer(data={**request.data, 'user': request.user.id})
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        serializer.save(user=request.user)

        return Response(serializer.data)

    def update(self, request: Request, pk: int = None) -> Response:
        receiver = Receiver.objects.get(id=pk)
        serializer = ReceiverSerializer(receiver, data=request.data, partial=True)

        if not serializer.is_valid():
            logger.info(serializer.data)
            return Response(serializer.errors, 400)

        serializer.update(receiver, serializer.validated_data)

        return Response(serializer.data)
