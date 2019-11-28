from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from authapp.models import *
from .disposers import *
import uuid
from django.utils.html import escape, _js_escapes, normalize_newlines
from django.utils.timezone import now


class Post(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None)
    ping_id = models.CharField(max_length=34, null=True, default=None)
    text = models.TextField(max_length=2000, null=True, default=None)
    ping_text = models.TextField(max_length=1000, null=True, default=None)
    comment_count = models.PositiveIntegerField(default=0)
    react_count = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user: %s, uuid: %s" % (self.user.userusername.username, self.uuid)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.uuid is None:
            self.uuid = uuid.uuid4().hex
        super().save(force_insert, force_update, using, update_fields)


class PostComment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)

    text = models.TextField(max_length=1000, null=True, blank=True)
    uuid = models.CharField(max_length=34, unique=True, default=None, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post comment: %s" % self.pk

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.uuid = uuid.uuid4().hex
        super().save(force_insert, force_update, using, update_fields)


class PostReact(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post React: %s" % self.pk

    class Meta:
        unique_together = ('user', 'post',)
