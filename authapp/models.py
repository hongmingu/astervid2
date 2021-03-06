import binascii

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings


import uuid
import os


# Create your models here.


class UserUsername(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    username = models.CharField(max_length=30, unique=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "UserUsername for %s" % self.user

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('baseapp:user_profile', kwargs={'user_username': self.username})


class UserFullName(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=30)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "UserName for %s" % self.user


class UserPrimaryEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_permitted = models.BooleanField(default=False)

    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "PrimaryEmail for %s" % self.user


class UserPrimaryEmailAuthToken(models.Model):
    user_primary_email = models.ForeignKey(UserPrimaryEmail, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255)

    uid = models.CharField(max_length=64)
    token = models.CharField(max_length=34, unique=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        email = self.user_primary_email
        return "AuthToken for %s" % email


class UserPasswordResetToken(models.Model):
    user_primary_email = models.ForeignKey(UserPrimaryEmail, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255)

    uid = models.CharField(max_length=64)
    token = models.CharField(max_length=34, unique=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user_primary_email is not None:
            email = self.user_primary_email
        else:
            email = "No email"
        return "PasswordAuthToken for %s" % email


class UserDelete(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "UserDelete for %s" % self.user.userusername.username


class UserFirebaseInstanceId(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instance_id = models.CharField(max_length=255, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "UserDelete for %s" % self.user.userusername.username


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    usernum =instance.user.username

    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "300_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/%s/userphoto' % usernum, filename)


def get_file_path_50(instance, filename):
    ext = filename.split('.')[-1]
    usernum = instance.user.username

    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "50_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/%s/userphoto' % usernum, filename)


class UserPhoto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    file_50 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path, max_length=1000)
    file_300 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path_50, max_length=1000)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "UserPhoto pk: %s, username: %s" % (self.pk, self.user.userusername.username)

    if settings.DEPLOY:

        def file_50_url(self):
            if self.file_50:
                return self.file_50.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.file_300:
                return self.file_300.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_300.png"
    else:
        def file_50_url(self):
            if self.file_50:
                return self.file_50.url
            return "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.file_300:
                return self.file_300.url
            return "/media/default/default_photo_300.png"


class UserToken(models.Model):
    """
    The default authorization token model.
    """
    token = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return "token: %s, username: %s" % (self.token, self.user.userusername.username)


class UserLog(models.Model):
    """
    Log of users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "username: %s, content: %s, " % (self.user.userusername.username, self.content)


class UserUniqueLog(models.Model):
    """
    Unique log of users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "username: %s, content: %s, " % (self.user.userusername.username, self.updated)


def test_get_file_path(instance, filename):
    ext = filename.split('.')[-1]

    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "300_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/%s/testphoto' % filename)


def test_get_file_path_50(instance, filename):
    ext = filename.split('.')[-1]

    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "50_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/%s/testphoto' % filename)


class TestPhoto(models.Model):
    file_50 = models.ImageField(null=True, blank=True, default=None, upload_to=test_get_file_path, max_length=1000)
    file_300 = models.ImageField(null=True, blank=True, default=None, upload_to=test_get_file_path_50, max_length=1000)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "TestPhoto pk: %s, created: %s" % (self.pk, self.created)

    if settings.DEPLOY:

        def file_50_url(self):
            if self.file_50:
                return self.file_50.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.file_300:
                return self.file_300.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_300.png"
    else:
        def file_50_url(self):
            if self.file_50:
                return self.file_50.url
            return "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.file_300:
                return self.file_300.url
            return "/media/default/default_photo_300.png"