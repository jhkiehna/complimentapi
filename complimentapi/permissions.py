from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from complimentapi.models import Receiver, Compliment


import logging
logger = logging.getLogger('django')


class OwnsReceiver(BasePermission):
    def has_permission(self, request: Request, view: ViewSet) -> bool:
        request_context = request.parser_context.get('kwargs', {})

        receiver = get_object_or_404(Receiver, id=request_context.get('receiver_pk', request_context.get('pk')))

        return request.user.id == receiver.user.id


class OwnsCompliment(BasePermission):
    def has_permission(self, request: Request, view: ViewSet) -> bool:
        compliment = get_object_or_404(Compliment, id=request.parser_context.get('kwargs', {}).get('pk'))

        return compliment.receiver.user.id == request.user.id
