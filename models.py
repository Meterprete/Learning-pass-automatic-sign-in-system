from django.db import models


class UserMac(models.Model):
    mac = models.CharField(max_length=16, null=False, verbose_name='MAC')
    phone = models.CharField(max_length=16, null=False, unique=True, verbose_name='手机号码')
    password = models.CharField(max_length=25, null=False, verbose_name='密码')
    token = models.CharField(max_length=255, null=False, unique=True, verbose_name='口令')
    photo = models.BooleanField(default=False, verbose_name='是否请求拍照')

    def __str__(self):
        return self.phone
