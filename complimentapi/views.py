import os
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer

from complimentapi.models import User
from complimentapi.serializers import UserSerializer

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
            '&state=state_parameter_passthrough_value' \
            .format(' '.join(scopes), redirect_uri, oauth_client_id)

        return Response(headers={'Location': oauth_url}, status=302)

    @action(detail=False, methods=['get'], name='OAuth Callback')
    def oauth_callback(self, request: Request) -> Response:
        logger.info(request.query_params)
        try:
            response_data = {}
            response_data.update(request.query_params)

            # Check access denied or no code
            if request.query_params.get('error') == 'access_denied' or not request.query_params.get('code'):
                return Response(401)

            # Make request for access token
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
            response_data.update(token_response_data)

            logger.info(token_response_data)

            # Make request for user info
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

            return Response(JSONRenderer().render(UserSerializer(user).data), 200)          
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response(500)

