from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from object.models import *
from relation.models import *
from notice.models import *
from django.db import transaction
from django.db.models import F
from django.utils.timezone import now
from object.numbers import *

KINDS_CHOICES = (
    (POSTCHAT_START, "start"),
    (POSTCHAT_TEXT, "text"),
    (POSTCHAT_PHOTO, "photo"),
)

'''
@receiver(post_save, sender=PostLike)
def created_post_like(sender, instance, created, **kwargs):
    if created:
        if instance.user == instance.post.user:
            return
        try:
            with transaction.atomic():
                notice = Notice.objects.create(user=instance.post.user, kind=POST_LIKE)
                notice_post_like = NoticePostLike.objects.create(notice=notice, post_like=instance)
                notice_count = instance.post.user.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=NoticePostLike)
def deleted_notice_post_like(sender, instance, **kwargs):
    try:
        if instance.notice:
            try:
                with transaction.atomic():
                    if instance.notice.checked is False:
                        notice_count = instance.notice.user.noticecount
                        notice_count.count = F('count') - 1
                        notice_count.save()
                    instance.notice.delete()
            except Exception as e:
                print(e)
                pass
    except:
        pass

'''

@receiver(post_save, sender=Follow)
def created_follow(sender, instance, created, **kwargs):
    if created:
        if instance.user == instance.follow:
            return
        try:
            with transaction.atomic():

                notice = Notice.objects.create(user=instance.follow, kind=FOLLOW, uuid=uuid.uuid4().hex)
                notice_follow = NoticeFollow.objects.create(notice=notice, follow=instance)
                notice_count = instance.follow.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()

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
    if instance.notice:
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
        if instance.user == instance.follow:
            return
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
    if instance.notice:
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
        if instance.user == instance.follow:
            return
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
    if instance.notice:
        try:
            with transaction.atomic():

                follower_count = instance.group.groupfollowercount
                follower_count.count = F('count') - 1
                follower_count.save()
        except Exception as e:
            print(e)
            pass

@receiver(post_delete, sender=NoticeFollow)#이걸 pre_delete로 해야하나?
def deleted_notice_follow(sender, instance, **kwargs):
    if instance.notice:
        try:
            with transaction.atomic():
                if instance.notice.checked is False:
                    notice_count = instance.notice.user.noticecount
                    notice_count.count = F('count') - 1
                    notice_count.save()
                instance.notice.delete()
        except Exception as e:
            print(e)
            pass


# notice post_comment
@receiver(post_save, sender=PostComment)
def created_post_comment(sender, instance, created, **kwargs):
    if created:
        if instance.user == instance.post.user:
            return
        try:
            with transaction.atomic():
                notice = Notice.objects.create(user=instance.post.user, kind=POST_COMMENT, uuid=uuid.uuid4().hex)
                notice_post_comment = NoticePostComment.objects.create(notice=notice, post_comment=instance)
                notice_count = instance.post.user.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()
        except Exception:
            pass


@receiver(post_delete, sender=NoticePostComment)
def deleted_notice_post_comment(sender, instance, **kwargs):
    if instance.notice:
        try:
            with transaction.atomic():
                instance.notice.delete()
        except Exception:
            pass


# notice post_like
@receiver(post_save, sender=PostLike)
def created_post_like(sender, instance, created, **kwargs):
    if created:
        if instance.user == instance.post.user:
            return
        try:
            with transaction.atomic():
                notice = Notice.objects.create(user=instance.post.user, kind=POST_LIKE, uuid=uuid.uuid4().hex)
                notice_post_like = NoticePostLike.objects.create(notice=notice, post_like=instance)
                notice_count = instance.post.user.noticecount
                notice_count.count = F('count') + 1
                notice_count.save()

                post_like_count = instance.post.postlikecount
                post_like_count.count = F('count') + 1
                post_like_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=PostLike)
def deleted_post_like(sender, instance, **kwargs):
    if instance.notice:
        try:
            with transaction.atomic():
                post_like_count = instance.post.postlikecount
                post_like_count.count = F('count') - 1
                post_like_count.save()
        except Exception as e:
            print(e)
            pass


@receiver(post_delete, sender=NoticePostLike)#이걸 pre_delete로 해야하나?
def deleted_notice_post_like(sender, instance, **kwargs):
    if instance.notice:
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
                post_count = PostCommentCount.objects.create(post=instance)
                post_like_count = PostLikeCount.objects.create(post=instance)
        except Exception as e:
            print(e)
            pass



from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

from decimal import Decimal


def ipn_signal(sender, **kwargs):
    ipn_obj = sender
    user = None
    wallet = None
    print('payment_gross: ' + str(ipn_obj.payment_gross))
    print('custom: ' + str(ipn_obj.custom))
    print('txn_id: ' + str(ipn_obj.txn_id))

    if ipn_obj.custom:
        try:
            user = User.objects.get(username=ipn_obj.custom)
        except Exception as e:
            return
        try:
            wallet = Wallet.objects.get(user=user)
        except Exception as e:
            return
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            with transaction.atomic():
                charge_log, created = ChargeLog.objects.get_or_create(wallet=wallet,
                                                                      transaction_id=ipn_obj.txn_id,
                                                                      gross=Decimal(ipn_obj.payment_gross))
                if created:
                    wallet.gross = F('gross') + Decimal(ipn_obj.payment_gross)
                    wallet.save()
                    # 여러번 실험해서 더플리케이트 실험 하면 됨.
        except Exception as e:
            print(e)
            return
    else:
        pass

valid_ipn_received.connect(ipn_signal)
'''
@receiver(post_save, sender=TestModel_2)
def create_update_log(sender, instance, created, **kwargs):
    if created:
        TestModelLog_2.objects.create(description=instance.description, status=20)
    else:
        TestModelLog_2.objects.create(description=instance.description, status=33)


@receiver(post_delete, sender=TestModel_2)
def delete_log(sender, instance, **kwargs):
    TestModelLog_2.objects.create(description=instance.description, status=2038)

# 값 포함해서 보내기 ------
def save(self, commit=True):
    user = super(CustomFormThing, self).save(commit=False)
    #set some other attrs on user here ...
    user._some = 'some'
    user._other = 'other'
    if commit:
        user.save()

    return user

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    some_id = getattr(instance, '_some', None)
    other_id = getattr(instance, '_other', None)

    if created:
# 값 포함해서 보내기 end -----
'''

# 여기 datetime 을 instance.updated 로 할지 now() 로 할지 결정해야한다 .
'''
    ['DoesNotExist', 'Meta', 'MultipleObjectsReturned', 'PAYMENT_STATUS_CHOICES', '__class__', '__delattr__',
     '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__',
     '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__',
     '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__',
     '__unicode__', '__weakref__', '_check_column_name_clashes', '_check_field_name_clashes', '_check_fields',
     '_check_id_field', '_check_index_together', '_check_local_fields', '_check_long_column_names',
     '_check_m2m_through_same_relationship', '_check_managers', '_check_model', '_check_model_name_db_lookup_clashes',
     '_check_ordering', '_check_swappable', '_check_unique_together', '_do_insert', '_do_update', '_get_FIELD_display',
     '_get_next_or_previous_by_FIELD', '_get_next_or_previous_in_order', '_get_pk_val', '_get_unique_checks', '_meta',
     '_perform_date_checks', '_perform_unique_checks', '_postback', '_save_parents', '_save_table', '_set_pk_val',
     '_state', '_verify_postback', 'address_city', 'address_country', 'address_country_code', 'address_name',
     'address_state', 'address_status', 'address_street', 'address_zip', 'amount', 'amount1', 'amount2', 'amount3',
     'amount_per_cycle', 'auction_buyer_id', 'auction_closing_date', 'auction_multi_item', 'auth_amount', 'auth_exp',
     'auth_id', 'auth_status', 'business', 'case_creation_date', 'case_id', 'case_type', 'charset', 'check', 'clean',
     'clean_fields', 'clear_flag', 'contact_phone', 'created_at', 'currency_code', 'custom', 'date_error_message',
     'delete', 'exchange_rate', 'first_name', 'flag', 'flag_code', 'flag_info', 'for_auction', 'format', 'from_db',
     'from_view', 'full_clean', 'get_deferred_fields', 'get_endpoint', 'get_next_by_created_at',
     'get_next_by_updated_at', 'get_previous_by_created_at', 'get_previous_by_updated_at', 'handling_amount', 'id',
     'initial_payment_amount', 'initialize', 'invoice', 'ipaddress', 'is_billing_agreement',
     'is_billing_agreement_cancel', 'is_billing_agreement_create', 'is_recurring', 'is_recurring_cancel',
     'is_recurring_create', 'is_recurring_failed', 'is_recurring_payment', 'is_recurring_skipped',
     'is_recurring_suspended', 'is_recurring_suspended_due_to_max_failed_payment', 'is_refund', 'is_reversed',
     'is_subscription', 'is_subscription_cancellation', 'is_subscription_end_of_term', 'is_subscription_failed',
     'is_subscription_modified', 'is_subscription_payment', 'is_subscription_signup', 'is_transaction', 'item_name',
     'item_number', 'last_name', 'mc_amount1', 'mc_amount2', 'mc_amount3', 'mc_currency', 'mc_fee', 'mc_gross',
     'mc_handling', 'mc_shipping', 'memo', 'mp_id', 'next_payment_date', 'notify_version', 'num_cart_items', 'objects',
     'option_name1', 'option_name2', 'option_selection1', 'option_selection2', 'outstanding_balance', 'parent_txn_id',
     'password', 'payer_business_name', 'payer_email', 'payer_id', 'payer_status', 'payment_cycle', 'payment_date',
     'payment_gross', 'payment_status', 'payment_type', 'pending_reason', 'period1', 'period2', 'period3',
     'period_type', 'pk', 'posted_data_dict', 'prepare_database_save', 'product_name', 'product_type', 'profile_status',
     'protection_eligibility', 'quantity', 'query', 'reason_code', 'reattempt', 'receipt_id', 'receiver_email',
     'receiver_id', 'recur_times', 'recurring', 'recurring_payment_id', 'refresh_from_db', 'remaining_settle',
     'residence_country', 'response', 'retry_at', 'rp_invoice_id', 'save', 'save_base', 'send_signals',
     'serializable_value', 'set_flag', 'settle_amount', 'settle_currency', 'shipping', 'shipping_method', 'subscr_date',
     'subscr_effective', 'subscr_id', 'tax', 'test_ipn', 'time_created', 'transaction_entity', 'transaction_subject',
     'txn_id', 'txn_type', 'unique_error_message', 'updated_at', 'username', 'validate_unique', 'verify',
     'verify_secret', 'verify_sign']
'''