from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Tenant(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="users", null=True
    )
