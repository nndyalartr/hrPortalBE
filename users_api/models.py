from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.
class User(AbstractUser):
    id=models.UUIDField(default=uuid.uuid4,max_length=500,primary_key=True,editable=False)
    first_name=models.CharField(blank=True,null=True)
    last_name=models.CharField(blank=True,null=True)
    email=models.EmailField(max_length=100,unique=True)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["first_name","last_name"]

    class Meta:
        verbose_name="users"
        db_table="user"
        verbose_name_plural="users"