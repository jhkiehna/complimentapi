from rest_framework import serializers

from complimentapi.models import User, Receiver, Compliment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receiver
        fields = '__all__'
        read_only_fields = ['id, user', 'created_at', 'updated_at']


class ComplimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliment
        fields = '__all__'
        read_only_fields = ['id, receiver', 'created_at', 'updated_at']
