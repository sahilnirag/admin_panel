from django.db import models
from api.models import User
# Create your models here.

class UserActivity(models.Model):
    time = models.TimeField(null=True,blank=True)
    page_url = models.URLField(null = True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        db_table = 'tbl_user_activity'





