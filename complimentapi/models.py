import datetime
from django.db import models


class User(models.Model):
    email = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    is_active = True

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True


class Receiver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receivers')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Compliment(models.Model):
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE, related_name='compliments')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_retrieved_at = models.DateTimeField(default=datetime.datetime.now())
