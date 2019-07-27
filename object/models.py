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
    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    uuid = models.CharField(max_length=34, unique=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        solo_post = None
        try:
            solo_post = self.solopost
        except Exception as e:
            pass
        if solo_post is not None:
            return "solo - Post pk: %s, user: %s" % (self.pk, self.user.userusername.username)
        else:
            return "group - Post pk: %s, user: %s" % (self.pk, self.user.userusername.username)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('baseapp:post', kwargs={'uuid': self.uuid})

    def get_obj_type(self):
        solo_post = None
        try:
            solo_post = self.solopost
        except Exception as e:
            pass
        if solo_post is not None:
            return "solo"
        else:
            return "group"


class PostText(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(max_length=5000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Post pk: %s" % self.post.pk


class DeletedPost(models.Model):
    username = models.CharField(max_length=34, null=True, blank=True, default=None)
    user_id = models.CharField(max_length=34, null=True, blank=True, default=None)
    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    obj_type = models.CharField(max_length=10, null=True, blank=True, default=None)
    obj_id = models.CharField(max_length=34, null=True, blank=True, default=None)
    post_uuid = models.CharField(max_length=34, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Post pk: %s, user: %s" % (self.pk, self.username)


class DeletedPostText(models.Model):
    deleted_post = models.ForeignKey(DeletedPost, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(max_length=5000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Post pk: %s" % self.deleted_post.pk


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(max_length=1000, null=True, blank=True)
    uuid = models.CharField(max_length=34, unique=True, default=None, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post comment: %s" % self.pk


class PostCommentCount(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post: %s" % self.post.pk


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post Like: %s" % self.pk

    class Meta:
        unique_together = ('user', 'post',)


class PostLikeCount(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "post Like Count: %s" % self.pk


class Group(models.Model):

    name = models.TextField(max_length=1000, null=True, blank=True, default=None)
    description = models.TextField(max_length=2000, null=True, blank=True, default=None)
    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "group name: %s, desc: %s" % (self.name, self.description)

    def get_main_name(self):
        return self.groupmainname.group_name.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('baseapp:group_posts', kwargs={'uuid': self.uuid})


class Solo(models.Model):

    name = models.TextField(max_length=1000, null=True, blank=True, default=None)
    description = models.TextField(max_length=2000, null=True, blank=True, default=None)
    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "solo name: %s, desc: %s" % (self.name, self.description)

    def get_main_name(self):
        return self.solomainname.solo_name.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('baseapp:solo_posts', kwargs={'uuid': self.uuid})


class GroupDate(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    date = models.DateField(default=None, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "group date: %s, %s" % (self.pk, self.updated)

    class Meta:
        unique_together = ('group', 'date',)


class SoloDate(models.Model):
    solo = models.ForeignKey(Solo, on_delete=models.SET_NULL, null=True, blank=True)
    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    date = models.DateField(default=None, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "solo date: %s, %s" % (self.pk, self.updated)

    class Meta:
        unique_together = ('solo', 'date',)


class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, null=True, blank=True)
    group_date = models.ForeignKey("GroupDate", on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.group, self.pk)

    class Meta:
        unique_together = ('group', 'post',)


class SoloPost(models.Model):
    solo = models.ForeignKey(Solo, on_delete=models.CASCADE, null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, null=True, blank=True)
    solo_date = models.ForeignKey("SoloDate", on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.solo, self.pk)

    class Meta:
        unique_together = ('solo', 'post',)


class GroupName(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255, blank=True, null=True, default=None)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.name, self.pk)

    class Meta:
        unique_together = ('name', 'group',)


class GroupMainName(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True)
    group_name = models.ForeignKey(GroupName, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.group_name.name, self.pk)

    class Meta:
        unique_together = ('group', 'group_name',)


class SoloName(models.Model):
    solo = models.ForeignKey(Solo, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255, blank=True, null=True, default=None)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.name, self.pk)

    class Meta:
        unique_together = ('name', 'solo',)


class SoloMainName(models.Model):
    solo = models.OneToOneField(Solo, on_delete=models.CASCADE, null=True, blank=True)
    solo_name = models.ForeignKey(SoloName, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "name: %s, desc: %s" % (self.solo_name.name, self.pk)

    class Meta:
        unique_together = ('solo', 'solo_name',)


class GroupPhoto(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    file_50 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path_group_celeb_photo_50, max_length=1000)
    file_300 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path_group_celeb_photo_300, max_length=1000)
    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)

    description = models.TextField(max_length=1000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "desc: %s" % self.description

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


class GroupMainPhoto(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True)
    group_photo = models.ForeignKey(GroupPhoto, on_delete=models.SET_NULL, null=True, blank=True)

    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)

    description = models.TextField(max_length=1000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "desc: %s" % self.description

    if settings.DEPLOY:

        def file_50_url(self):
            if self.group_photo:
                return self.group_photo.file_50.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.group_photo:
                return self.group_photo.file_300.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_300.png"
    else:
        def file_50_url(self):
            if self.group_photo:
                return self.group_photo.file_50.url
            return "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.group_photo:
                return self.group_photo.file_300.url
            return "/media/default/default_photo_300.png"


class SoloPhoto(models.Model):
    solo = models.ForeignKey(Solo, on_delete=models.CASCADE, null=True, blank=True)
    file_50 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path_solo_celeb_photo_50, max_length=1000)
    file_300 = models.ImageField(null=True, blank=True, default=None, upload_to=get_file_path_solo_celeb_photo_300, max_length=1000)
    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)
    main = models.BooleanField(default=False)

    description = models.TextField(max_length=1000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "desc: %s" % self.description

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


class SoloMainPhoto(models.Model):
    solo = models.OneToOneField(Solo, on_delete=models.CASCADE, null=True, blank=True)
    solo_photo = models.ForeignKey(SoloPhoto, on_delete=models.SET_NULL, null=True, blank=True)

    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)

    description = models.TextField(max_length=1000, null=True, blank=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "desc: %s" % self.description

    if settings.DEPLOY:

        def file_50_url(self):
            if self.solo_photo:
                return self.solo_photo.file_50.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.solo_photo:
                return self.solo_photo.file_300.url
            return settings.AWS_S3_SCHEME + settings.AWS_S3_CUSTOM_DOMAIN + "/media/default/default_photo_300.png"
    else:
        def file_50_url(self):
            if self.solo_photo:
                return self.solo_photo.file_50.url
            return "/media/default/default_photo_50.png"

        def file_300_url(self):
            if self.solo_photo:
                return self.solo_photo.file_300.url
            return "/media/default/default_photo_300.png"


class Member(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    solo = models.ForeignKey(Solo, on_delete=models.CASCADE, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "solo: %s - group: %s" % (self.solo.name, self.group.name)

    class Meta:
        unique_together = ('group', 'solo',)


# =--------------------------------------------------------------------------------------------------------------
    # >>> Decimal('10.50') - Decimal('0.20')
    # Decimal('10.30')


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user: %s - wallet gross: %s $" % (self.user.username, self.gross)


class ChargeLog(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)

    kind = models.CharField(max_length=255, blank=True, null=True, default=None)

    transaction_id = models.CharField(max_length=255, blank=True, null=True, default=None)
    user_id = models.CharField(max_length=34, blank=True, null=True, default=None)
    username = models.CharField(max_length=34, blank=True, null=True, default=None)

    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)

    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user: %s - transaction_id: %s $" % (self.wallet.user.userusername.username, self.transaction_id)

    class Meta:
        unique_together = ('wallet', 'transaction_id',)


class PayLog(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)

    kind = models.CharField(max_length=255, blank=True, null=True, default=None)

    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)

    post_uuid = models.CharField(max_length=34, blank=True, null=True, default=None)
    user_id = models.CharField(max_length=34, blank=True, null=True, default=None)
    username = models.CharField(max_length=34, blank=True, null=True, default=None)

    uuid = models.CharField(max_length=34, unique=True, blank=True, null=True, default=None)

    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "pay user: %s - amount: %s $" % (self.post.user.userusername.username, self.gross)

    class Meta:
        unique_together = ('wallet', 'post',)
