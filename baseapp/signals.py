from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from object.models import *
from relation.models import *
from notice.models import *
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now
from object.numbers import *

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from decimal import Decimal


@receiver(post_save, sender=Follow)
def created_follow(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():

                if not instance.user == instance.follow:
                    notice = Notice.objects.create(user=instance.follow, kind=FOLLOW, uuid=uuid.uuid4().hex)
                    notice_follow = NoticeFollow.objects.create(notice=notice, follow=instance)

                following_count = instance.user.followingcount
                following_count.count = F('count') + 1
                following_count.save()
                follower_count = instance.follow.followercount
                follower_count.count = F('count') + 1
                follower_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=Follow)
def deleted_follow(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            following_count = instance.user.followingcount
            following_count.count = F('count') - 1
            following_count.save()
            follower_count = instance.follow.followercount
            follower_count.count = F('count') - 1
            follower_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticeFollow)
def deleted_notice_follow(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            instance.notice.delete()
    except Exception as e:
        print(e)
        pass


# notice post_comment
@receiver(post_save, sender=PostComment)
def created_post_comment(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                if not instance.user == instance.post.user:
                    notice = Notice.objects.create(user=instance.post.user, kind=POST_COMMENT, uuid=uuid.uuid4().hex)
                    notice_post_comment = NoticePostComment.objects.create(notice=notice, post_comment=instance)

                post_comment_count = instance.post.postcommentcount
                post_comment_count.count = F('count') + 1
                post_comment_count.save()
        except Exception:
            pass


@receiver(post_delete, sender=PostComment)
def deleted_post_comment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            post_comment_count = instance.post.postcommentcount
            post_comment_count.count = F('count') - 1
            post_comment_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticePostComment)
def deleted_notice_post_comment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            instance.notice.delete()
    except Exception:
        pass


# notice post_like
@receiver(post_save, sender=PostReact)
def created_post_like(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                if not instance.user == instance.post.user:
                    notice = Notice.objects.create(user=instance.post.user, kind=POST_LIKE, uuid=uuid.uuid4().hex)
                    notice_post_like = NoticePostReact.objects.create(notice=notice, post_react=instance)

                post_react_count = instance.post.postreactcount
                post_react_count.count = F('count') + 1
                post_react_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=PostReact)
def deleted_post_like(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            post_react_count = instance.post.postreactcount
            post_react_count.count = F('count') - 1
            post_react_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticePostReact)
def deleted_notice_post_like(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            instance.notice.delete()
    except Exception as e:
        print(e)
        pass


@receiver(post_save, sender=Notice)
def created_notice(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                notice_count = instance.user.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=Notice)
def deleted_notice(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if instance.checked is False:
                notice_count = instance.user.noticecount
                notice_count.count = F('count') - 1
                notice_count.save()
    except Exception as e:
        print(e)
        pass


# ======================================================================================================================


@receiver(post_save, sender=Post)
def created_post(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                post_comment_count = PostCommentCount.objects.create(post=instance)
                post_react_count = PostReactCount.objects.create(post=instance)
        except Exception as e:
            print(e)
            pass

