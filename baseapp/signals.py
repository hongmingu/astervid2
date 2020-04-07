from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from object.models import *
from relation.models import *
from notice.models import *
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now
from object.numbers import *

from baseapp.constants import *

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from decimal import Decimal


from authapp import texts


@receiver(post_save, sender=Post)
def created_post(sender, instance, created, **kwargs):
    if created:
        user_log = UserLog.objects.create(user=instance.user, content=LOG_POST)
        user_unique_log = UserUniqueLog.objects.update_or_create(user=instance.user)

        try:
            with transaction.atomic():
                from pyfcm import FCMNotification

                push_service = FCMNotification(api_key=texts.FCM_API_KEY)

                # registration_ids = []
                # registration_ids.append(instance.user.userfirebaseinstanceid.instance_id)
                text = "none"
                ping_id = "none"
                if instance.ping_id is not None and instance.ping_text is None:
                    # 핑 텍스트 기본값
                    text = "need_ping_text"
                    ping_id = instance.ping_id
                elif instance.ping_text is not None:
                    # 핑은 있되 핑 텍스트는 바뀜
                    text = instance.ping_text
                else:
                    # 핑도없고 핑 텍스트도 없고 포스트텍스트
                    text = instance.text
                from baseapp.constants import FCM_OPT_POST
                data_message = {
                    "opt": FCM_OPT_POST,
                    "full_name": instance.user.userfullname.full_name,
                    "photo": instance.user.userphoto.file_300_url(),
                    "instance_id": uuid.uuid4().hex,
                    "ping_id": ping_id,
                    "text": text
                }

                id_list = []
                follows = Follow.objects.filter(follow=instance.user)

                for follow in follows:
                    if follow.user.userfirebaseinstanceid.instance_id is not None and follow.user is not instance.user:
                        id_list.append(follow.user.userfirebaseinstanceid.instance_id)

                valid_id_list = push_service.clean_registration_ids(id_list)
                print("valid id list: "+ str(valid_id_list))

                result = push_service.notify_multiple_devices(
                    registration_ids=valid_id_list, data_message=data_message)
        except Exception as e:
            print(e)
            pass


@receiver(post_save, sender=Follow)
def created_follow(sender, instance, created, **kwargs):
    if created:
        user_log = UserLog.objects.create(user=instance.user, content=LOG_FOLLOW)
        user_unique_log = UserUniqueLog.objects.update_or_create(user=instance.user)

        try:
            with transaction.atomic():

                if not instance.user == instance.follow:
                    notice = Notice(user=instance.follow, kind=FOLLOW, uuid=uuid.uuid4().hex)
                    notice.extra_param_full_name = instance.user.userfullname.full_name
                    notice.extra_param_photo = instance.user.userphoto.file_300_url()
                    notice.save()

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
        user_log = UserLog.objects.create(user=instance.user, content=LOG_COMMENT)
        user_unique_log = UserUniqueLog.objects.update_or_create(user=instance.user)

        try:
            with transaction.atomic():
                if not instance.user == instance.post.user:
                    # notice = Notice.objects.create(user=instance.post.user, kind=POST_COMMENT, uuid=uuid.uuid4().hex)
                    # notice_post_comment = NoticePostComment.objects.create(notice=notice, post_comment=instance)
                    notice = Notice(user=instance.post.user, kind=POST_COMMENT, uuid=uuid.uuid4().hex)
                    notice.extra_param_text = instance.text
                    notice.extra_param_full_name = instance.user.userfullname.full_name
                    notice.extra_param_photo = instance.user.userphoto.file_300_url()
                    notice.save()

                    notice_post_comment = NoticePostComment(notice=notice, post_comment=instance)
                    notice_post_comment.save()
                post = instance.post
                post.comment_count = F('comment_count') + 1
                post.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=PostComment)
def deleted_post_comment(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            post = instance.post
            post.comment_count = F('comment_count') - 1
            post.save()
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


# notice post_react
@receiver(post_save, sender=PostReact)
def created_post_react(sender, instance, created, **kwargs):
    if created:
        user_log = UserLog.objects.create(user=instance.user, content=LOG_REACT)
        user_unique_log = UserUniqueLog.objects.update_or_create(user=instance.user)

        try:
            with transaction.atomic():
                if not instance.user == instance.post.user:
                    notice = Notice(user=instance.post.user, kind=POST_REACT, uuid=uuid.uuid4().hex)
                    notice.extra_param_full_name = instance.user.userfullname.full_name
                    notice.extra_param_photo = instance.user.userphoto.file_300_url()
                    notice.save()

                    notice_post_react = NoticePostReact.objects.create(notice=notice, post_react=instance)

                post = instance.post
                post.react_count = F('react_count') + 1
                post.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=PostReact)
def deleted_post_react(sender, instance, **kwargs):
    try:
        with transaction.atomic():

            post = instance.post
            post.react_count = F('react_count') - 1
            post.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticePostReact)
def deleted_notice_post_react(sender, instance, **kwargs):
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

                from pyfcm import FCMNotification

                push_service = FCMNotification(api_key=texts.FCM_API_KEY)

                # registration_ids = []
                # registration_ids.append(instance.user.userfirebaseinstanceid.instance_id)

                from notice.models import get_fcm_opt_by_notice, FOLLOW, POST_REACT, POST_COMMENT

                text = "none"
                instance_id = "none"
                if instance.kind == POST_REACT:
                    full_name = instance.extra_param_full_name
                    photo = instance.extra_param_photo

                elif instance.kind == POST_COMMENT:
                    full_name = instance.extra_param_full_name
                    photo = instance.extra_param_photo
                    text = instance.extra_param_text

                elif instance.kind == FOLLOW:
                    full_name = instance.extra_param_full_name
                    photo = instance.extra_param_photo

                data_message = {
                    "opt": get_fcm_opt_by_notice(instance.kind),
                    "full_name": full_name,
                    "photo": photo,
                    "instance_id": uuid.uuid4().hex,
                    "text": text

                }

                if instance.user.userfirebaseinstanceid.instance_id is not None:
                    result = push_service.notify_single_device(registration_id=instance.user.userfirebaseinstanceid.instance_id, data_message=data_message)

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

