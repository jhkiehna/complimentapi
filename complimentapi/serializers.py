from rest_framework import serializers

from complimentapi.models import User, Receiver

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receiver
        fields = '__all__'
        read_only_fields = ['id, user_id']
