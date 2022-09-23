from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
#
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fio = models.TextField(max_length=500, blank=True)
    bank = models.CharField(max_length=600, blank=True)


class Users_Reg(models.Model):
    fio = models.TextField()
    email=models.EmailField()
    bank = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    comment = models.TextField()

    def __str__(self):
        return self.email

