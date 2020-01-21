from django.db import models


# Create your models here.

class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='用户名', primary_key=True)
    nickname = models.CharField(max_length=30, verbose_name='昵称')
    email = models.CharField(max_length=50,verbose_name='邮箱,',null=True)
    password = models.CharField(max_length=32)
    sign = models.CharField(max_length=50,verbose_name='个性签名',default='')
    info = models.CharField(max_length=150,verbose_name='个人描述',default='')
    avatar = models.ImageField(upload_to='avatar/')

    class Meta:
        db_table = 'user_profile'
