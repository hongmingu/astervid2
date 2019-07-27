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


@receiver(post_save, sender=SoloFollow)
def created_solo_follow(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                follower_count = instance.solo.solofollowercount
                follower_count.count = F('count') + 1
                follower_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=SoloFollow)
def deleted_solo_follow(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            follower_count = instance.solo.solofollowercount
            follower_count.count = F('count') - 1
            follower_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_save, sender=GroupFollow)
def created_group_follow(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():

                from django.db.models import F
                follower_count = instance.group.groupfollowercount
                follower_count.count = F('count') + 1
                follower_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=GroupFollow)
def deleted_group_follow(sender, instance, **kwargs):
    try:
        with transaction.atomic():

            follower_count = instance.group.groupfollowercount
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
@receiver(post_save, sender=PostLike)
def created_post_like(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                if not instance.user == instance.post.user:
                    notice = Notice.objects.create(user=instance.post.user, kind=POST_LIKE, uuid=uuid.uuid4().hex)
                    notice_post_like = NoticePostLike.objects.create(notice=notice, post_like=instance)

                post_like_count = instance.post.postlikecount
                post_like_count.count = F('count') + 1
                post_like_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=PostLike)
def deleted_post_like(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            post_like_count = instance.post.postlikecount
            post_like_count.count = F('count') - 1
            post_like_count.save()
    except Exception as e:
        print(e)
        pass


@receiver(post_delete, sender=NoticePostLike)
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
                post_like_count = PostLikeCount.objects.create(post=instance)
        except Exception as e:
            print(e)
            pass


@receiver(pre_delete, sender=Post)
def deleted_post(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            username = ''
            user_id = ''
            gross = 0
            obj_type = ''
            obj_id = ''
            post_uuid = ''
            try:
                username = instance.user.userusername.username
                user_id = instance.user.username
                gross = instance.gross
                try:
                    obj_id = instance.solopost.solo.uuid
                    obj_type = "solo"
                except Exception as e:
                    try:
                        obj_id = instance.grouppost.group.uuid
                        obj_type = "group"
                    except Exception as e:
                        pass
                post_uuid = instance.uuid
            except Exception as e:
                print(e)
                pass
            deleted_post = DeletedPost.objects.create(username=username,
                                                      user_id=user_id,
                                                      obj_id=obj_id,
                                                      obj_type=obj_type,
                                                      post_uuid=post_uuid,
                                                      gross=gross)
            text = ''
            try:
                text = PostText.objects.filter(post=instance).last().text
            except Exception as e:
                print(e)
                pass
            deleted_post_text = DeletedPostText.objects.create(deleted_post=deleted_post, text=text)
    except Exception as e:
        print(e)
        pass


def ipn_signal(sender, **kwargs):
    ipn_obj = sender
    user = None
    wallet = None
    if ipn_obj.custom:
        try:
            user = User.objects.get(username=ipn_obj.custom)
        except Exception as e:
            print(e)
            return
        try:
            wallet = Wallet.objects.get(user=user)
        except Exception as e:
            print(e)
            return
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            with transaction.atomic():
                charge_log, created = ChargeLog.objects.get_or_create(wallet=wallet,
                                                                      transaction_id=ipn_obj.txn_id)
                if created:
                    wallet.gross = F('gross') + Decimal(ipn_obj.payment_gross)
                    wallet.save()
                    charge_log.gross = Decimal(ipn_obj.payment_gross)
                    charge_log.username = user.userusername.username
                    charge_log.kind = 'paypal'
                    charge_log.uuid = uuid.uuid4().hex
                    charge_log.user_id = user.username
                    charge_log.save()
        except Exception as e:
            print(e)
            return
    else:
        pass


valid_ipn_received.connect(ipn_signal)
