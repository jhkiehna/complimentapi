from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from complimentapi.models import Receiver


import logging
logger = logging.getLogger('django')


class OwnsReceiver(BasePermission):
    def has_permission(self, request: Request, view: ViewSet) -> bool:
        receiver = get_object_or_404(Receiver, id=request.parser_context.get('kwargs', {}).get('pk'))

        if receiver.id not in [user_receiver.id for user_receiver in request.user.receivers.all()]:
            return False

        return True
