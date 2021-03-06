import json
import urllib
from urllib.parse import urlparse

import random
from PIL import Image
from django.utils import dateparse
from io import BytesIO
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse

from authapp import options
from .texts import *
from .token import account_activation_token
from authapp.utils import token_authenticate
from baseapp.utils import user_primary_email_validate, user_full_name_validate, \
    password_username_validate, password_validate, make_id
from object.models import *
from relation.models import *
from notice.models import *
from django.utils.html import escape, _js_escapes, normalize_newlines
from object.numbers import *
from decimal import Decimal

from django.db.models import F
from django.utils.timezone import localdate

from .constants import *
from .utils import *
from .pings import *
from .opts import *
from django.utils import timezone


# Create your models here.
# 좋아요 비공개 할 수 있게
# 챗스톡, 페이지픽, 임플린, 챗카부 순으로 만들자.

# ---------------------------------------------------------------------------------------------------------------------------

@csrf_exempt
def user_fully_update(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    user_id = request.POST.get('user_id', None)

    get_user = get_user_by_id(user_id)

    step = 50

    followings = Follow.objects.filter(user=get_user).order_by('-created').distinct()[:step]

    following_result = []

    for item in followings:
        following_result.append(get_serialized_user(item.follow, user, False))
    print(following_result)

    followers = Follow.objects.filter(follow=get_user).order_by('-created').distinct()[:step]

    follower_result = []

    for item in followers:
        follower_result.append(get_serialized_user(item.user, user, False))

    return JsonResponse({'rc': SUCCEED_RESPONSE,
                         'content_follower': follower_result,
                         'content_following': following_result,
                         'user': get_serialized_user(get_user, user, True)}, safe=False)


@csrf_exempt
def forgot_password(request):
    import authapp
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    account = request.POST.get('account', None)

    user, code = get_user_by_account(account)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': code}, safe=False)

    user_primary_email = user.userprimaryemail

    checker_while_loop = 0
    counter_if_loop = 0
    uid = None
    token = None

    while checker_while_loop is 0:
        if counter_if_loop <= 9:

            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
                token = account_activation_token.make_token(user)
                UserPasswordResetToken.objects.create(
                    user_primary_email=user_primary_email,
                    uid=uid,
                    token=token,
                    email=user_primary_email.email,
                )

            except IntegrityError as e:
                if 'UNIQUE constraint' in str(e.args):
                    counter_if_loop = counter_if_loop + 1
                else:
                    return JsonResponse({'rc': FAILED_RESPONSE, 'content': INVALID_TOKEN}, safe=False)
        checker_while_loop = 1

    # Send Email
    subject = '[' + authapp.texts.SITE_NAME + ']' + authapp.texts.PASSWORD_RESET_SUBJECT

    message = render_to_string('authapp/_password_reset_email.html', {
        'username': user.userusername.username,
        'name': user.userfullname.full_name,
        'email': user_primary_email.email,
        'domain': authapp.texts.SITE_DOMAIN,
        'site_name': authapp.texts.SITE_NAME,
        'uid': uid,
        'token': token,
    })

    email_list = [user_primary_email.email]
    print(email_list)
    #
    # send_mail(
    #     subject=subject, message=message, from_email=authapp.options.DEFAULT_FROM_EMAIL,
    #     recipient_list=email_list
    # )
    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': asterisk_total(user_primary_email.email)}, safe=False)


@csrf_exempt
def password_set(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    current_password = request.POST.get('current_password', None)

    new_password = request.POST.get('new_password', None)
    new_password_confirm = request.POST.get('new_password_confirm', None)

    success, user = get_user_token(user.userusername, current_password)

    print(user)
    if not success:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    # username 작성시에 password 랑 같지 않게 짜져야 할 것이다.

    password_success, password_code = password_validate(new_password)
    if not password_success or (new_password != new_password_confirm):
        return JsonResponse({'rc': 1, 'content': {'code': password_code}}, safe=False)

    try:
        with transaction.atomic():
            user.set_password(new_password)
            user.save()
    except Exception as e:
        print(e)
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': INVALID_TOKEN}, safe=False)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': VALIDATE_OK}, safe=False)


@csrf_exempt
def profile_change(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    username = request.POST.get('username', None)
    full_name = request.POST.get('full_name', None)
    email = request.POST.get('email', None)

    print(username)
    print(full_name)
    print(email)
    # validating email and password
    print(user.userusername.username)
    print(user.userfullname.full_name)
    print(user.userprimaryemail.email)
    if UserPrimaryEmail.objects.filter(email=email).exclude(user=user).exists():
        print("here")
        return JsonResponse({'rc': 1, 'content': USER_EMAIL_EXIST_PROBLEM}, safe=False)

    if UserUsername.objects.filter(username=username).exclude(user=user).exists():
        print("here")
        return JsonResponse({'rc': 1, 'content': USER_EMAIL_EXIST_PROBLEM}, safe=False)

    username_success, username_code = user_username_validate(username)
    if not username_success:
        return JsonResponse({'rc': 1, 'content': username_code}, safe=False)

    email_success, email_code = user_primary_email_validate(email)
    if not email_success:
        return JsonResponse({'rc': 1, 'content': email_code}, safe=False)

    full_name_success, full_name_code = user_full_name_validate(full_name)
    if not full_name_success:
        return JsonResponse({'rc': 1, 'content': full_name_code}, safe=False)

    try:
        with transaction.atomic():
            user_username = user.userusername
            user_full_name = user.userfullname
            user_primary_email = user.userprimaryemail
            user_username.username = username
            user_full_name.full_name = full_name
            user_primary_email.email = email

            user_username.save()
            user_full_name.save()
            user_primary_email.save()
    except Exception as e:
        print(e)
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': INVALID_TOKEN}, safe=False)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': VALIDATE_OK}, safe=False)


@csrf_exempt
def get_following(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    user_id = request.POST.get('user_id', None)

    get_user = get_user_by_id(user_id)

    step = 50

    followings = Follow.objects.filter(user=get_user).order_by('-created').distinct()[:step]

    result = []

    for item in followings:
        result.append(get_serialized_user(item.follow, user, False))
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def get_follower(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    user_id = request.POST.get('user_id', None)

    get_user = get_user_by_id(user_id)

    step = 50

    followers = Follow.objects.filter(follow=get_user).order_by('-created').distinct()[:step]

    result = []

    for item in followers:
        result.append(get_serialized_user(item.user, user, False))
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def get_react(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    post_id = request.POST.get('post_id', None)

    post = get_post_by_id(post_id)

    step = 5
    print(str(end_id))

    if end_id is None:
        objs = PostReact.objects.filter(Q(post=post)).exclude().order_by('-created').distinct().all()
    else:
        try:
            user = User.objects.get(username=end_id)
            obj = PostReact.objects.get(Q(post=post) & Q(user=user))
        except Exception as e:
            print(e)
            return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

        objs = PostReact.objects.filter(
            Q(post=post) &
            Q(pk__lt=obj.pk)
        ).exclude().order_by('-created').distinct()[:step]

    result = []
    obj_index = 0
    for item in objs:
        obj_index += 1
        # if obj_index is step-1:
        #     break
        result.append(get_serialized_react(item, user))
    if objs.count() < step:
        """
        posts are loaded fully
        """

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def get_comment(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    post_id = request.POST.get('post_id', None)

    post = get_post_by_id(post_id)

    step = 5
    print(str(end_id))

    if end_id is None:
        objs = PostComment.objects.filter(Q(post=post)).exclude().order_by('-created').distinct().all()
    else:
        try:
            obj = PostComment.objects.get(uuid=end_id)
        except PostComment.DoesNotExist as e:
            print(e)
            return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

        objs = PostComment.objects.filter(
            Q(post=post) &
            Q(pk__lt=obj.pk)
        ).exclude().order_by('-created').distinct()[:step]

    result = []
    obj_index = 0
    for item in objs:
        obj_index += 1
        # if obj_index is step-1:
        #     break
        result.append(get_serialized_comment(item, user))

    print(str(result))
    if objs.count() < step:
        """
        posts are loaded fully
        """

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def change_profile_photo(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    print("request: " + str(request))
    print("request: " + str(request.FILES['uploaded_file']))
    end_id = request.POST.get('end_id', None)

    from io import BytesIO
    from PIL import Image
    from django.core.files.uploadedfile import SimpleUploadedFile
    import os
    import magic

    mime = magic.Magic(mime=True)
    file_loc = BytesIO(request.FILES['uploaded_file'].read())

    print(mime.from_buffer(file_loc.read()))

    PIL_TYPE = 'jpeg'
    FILE_EXTENSION = 'jpg'
    #
    user_photo, created = UserPhoto.objects.get_or_create(user=user)
    image = Image.open(file_loc)

    # Save the thumbnail
    temp_handle = BytesIO()
    image.save(temp_handle, PIL_TYPE, quality=90)
    temp_handle.seek(0)

    # Save image to a SimpleUploadedFile which can be saved into ImageField
    print(os.path.split(request.FILES['uploaded_file'].name)[-1])
    suf = SimpleUploadedFile(os.path.split(request.FILES['uploaded_file'].name)[-1],
                             temp_handle.read(), content_type='image/jpeg')
    # Save SimpleUploadedFile into image field
    user_photo.file_300.save(
        '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
        suf, save=True)

    temp_handle.close()

    print(user_photo.file_300.url)
    end_id = request.POST.get('end_id', None)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': user_photo.file_300_url()}, safe=False)


@csrf_exempt
def get_notice(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)

    step = 5
    print(str(end_id))

    post_last = timezone.now()
    post_before = timezone.now() - timezone.timedelta(minutes=30)

    if end_id is None:
        objs = Notice.objects.filter(
            Q(checked=False)
            | (Q(created__range=(post_before, post_last)) & (Q(checked=True)))
        ).exclude().order_by(
            '-created').distinct().all()
    else:
        try:
            obj = Notice.objects.get(uuid=end_id)
        except Notice.DoesNotExist as e:
            print(e)
            return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

        objs = Notice.objects.filter(
            Q(pk__lt=obj.pk)
        ).exclude().order_by('-created').distinct()[:step]

    result = []

    obj_index = 0
    for item in objs:
        obj_index += 1
        # if obj_index is step - 1:
        #     break
        result.append(get_serialized_notice(item, user, False, False))
    # is empty
    if objs.count() == 0:
        result.append(get_serialized_notice(True, True, True, True))

    if objs.count() < step:
        """
        posts are loaded fully
        """

    objs.update(checked=True)
    print(str(result))
    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def log_out(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    registration_id = request.POST.get('fcm_token', None)

    if registration_id is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    firebase_id, created = UserFirebaseInstanceId.objects.get_or_create(user=user)
    print(firebase_id.instance_id)
    exist_firebase_instance_ids = UserFirebaseInstanceId.objects.filter(instance_id=registration_id).all()
    if exist_firebase_instance_ids.exists():
        for item in exist_firebase_instance_ids:
            item.instance_id = None
            item.save()

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': created}, safe=False)


@csrf_exempt
def fcm_push(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    registration_id = request.POST.get('fcm_token', None)

    if registration_id is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    firebase_id, created = UserFirebaseInstanceId.objects.get_or_create(user=user)
    print(firebase_id.instance_id)

    if firebase_id.instance_id != registration_id:
        exist_firebase_instance_ids = UserFirebaseInstanceId.objects.filter(instance_id=registration_id).all()
        if exist_firebase_instance_ids.exists():
            for item in exist_firebase_instance_ids:
                item.instance_id = None
                item.save()
        # todo: 여기 제대로 동작하나 확인.
        firebase_id.instance_id = registration_id
        firebase_id.save()
    # from pyfcm import FCMNotification
    #
    # push_service = FCMNotification(api_key="AAAAtW7jvvs:APA91bHmJB1UsjuwRiggVmOMnyDPMOd-PJ0t-WxQ0jLV0eku9dLS2LPIvraOecrf-QmI0SR-crle-fYclihygLx7drwVpLkLo2QRFenbG1OIvHWYObPmi8b8FXvrIv9F-3UttK6qISYu")
    #
    # registration_ids = [
    #     ]
    #
    # for i in range(10):
    #     registration_ids.append(registration_id)
    #
    # data_message = {
    #     "opt": "",
    #     "body": "great match!",
    #     "Room": "PortugalVSDenmark"
    # }
    # message_body = "Hi john, your customized news for today is ready"
    #
    # result = push_service.notify_multiple_devices(registration_ids=registration_ids, data_message=data_message)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': created}, safe=False)


@csrf_exempt
def search(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    step = 50

    search_word = request.POST.get('search_word', None)

    users = User.objects.filter(Q(userusername__username__icontains=search_word) |
                                Q(userfullname__full_name__icontains=search_word)).exclude(
        Q(username=user.username)).order_by('-userusername__created').distinct()[:step]

    if users is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    # todo: 이제 get user profile url 이랑 디테일 정리.
    result = []

    for item in users:
        result.append(get_serialized_user(item, user, False))

    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def follow(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    user_id = request.POST.get('user_id', None)

    user_find = User.objects.get(username=user_id)
    if user_find is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    if user == user_find:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    follow_given, created = Follow.objects.get_or_create(user=user, follow=user_find)
    if created is False:
        follow_given.delete()

    # todo: 이제 get user profile url 이랑 디테일 정리.

    result = []
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': created}, safe=False)


@csrf_exempt
def get_user_profile(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    user_id = request.POST.get('user_id', None)

    user_find = User.objects.get(username=user_id)
    if user_find is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)
    # todo: 이제 get user profile url 이랑 디테일 정리.

    result = []
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def get_follow_feed(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    step = 10
    print(str(end_id))

    # todo: received feed 마지막에 넣을 리스트.
    """
                    if end_id == '':
                    posts = Post.objects.filter(Q(user__ffollow__user=request.user)
                                                | Q(grouppost__group__is_group_followed__user=request.user)
                                                | Q(solopost__solo__is_solo_followed__user=request.user)
                                                ).exclude(Q(user=request.user)).order_by('-created').distinct()[:step]
                else:
                    end_post = None
                    try:
                        end_post = Post.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    posts = Post.objects.filter((Q(user__ffollow__user=request.user)
                                                | Q(grouppost__group__is_group_followed__user=request.user)
                                                | Q(solopost__solo__is_solo_followed__user=request.user))
                                                & Q(pk__lt=end_post.pk)).exclude(
                        Q(user=request.user)).order_by('-created').distinct()[:step]
    """
    posts = None
    post_last = timezone.now()
    post_before = timezone.now() - timezone.timedelta(minutes=30)
    if end_id is None:
        pass
    else:
        pass
    if end_id is None:
        pass
        posts = Post.objects.filter(
            (Q(user__ffollow__user=user) | Q(user=user))
            & Q(created__range=(post_before, post_last))
        ).exclude().order_by('-created').distinct().all()
    else:
        try:
            post = Post.objects.get(uuid=end_id)
        except Post.DoesNotExist as e:
            print(e)
            return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

        posts = Post.objects.filter(
            (Q(user__ffollow__user=user) | Q(user=user))
            & Q(created__range=(post_before, post_last))
            & Q(pk__lt=post.pk)
        ).exclude().order_by('-created').distinct().all()

    result = []
    post_index = 0
    for item in posts:
        post_index += 1
        # if post_index is step - 1:
        #     break
        result.append({"is_list": False, "con": get_serialized_post(item.uuid, user)})

    if posts.count() == 0:
        result.append({"is_list": True, "date": "empty", "con": []})

    recent_last = timezone.now()
    recent_before = timezone.now() - timezone.timedelta(hours=6)
    # end_date = datetime.date(2005, 3, 31)
    recent_logs = UserUniqueLog.objects.filter(
        Q(updated__range=(recent_before, recent_last)) & Q(user__ffollow__user=user)).exclude(
        Q(user=user)).order_by('-updated').distinct()[:step]

    quarter_day_last = timezone.now() - timezone.timedelta(hours=6)
    quarter_day_before = timezone.now() - timezone.timedelta(hours=24)
    quarter_day_logs = UserUniqueLog.objects.filter(
        Q(updated__range=(quarter_day_before, quarter_day_last)) & Q(user__ffollow__user=user)).exclude(
        Q(user=user)).order_by(
        '-updated').distinct()

    day_logs = UserUniqueLog.objects.filter(Q(user__ffollow__user=user)).exclude(
        Q(updated__range=(quarter_day_before, recent_last)) | Q(user=user)).order_by(
        '-updated').distinct()

    all_logs = UserUniqueLog.objects.filter().exclude(
        Q(user__ffollow__user=user)
        | Q(user=user)).order_by(
        '-updated').distinct()

    result.append({"is_list": True, "date": "RECENT", "con": get_user_list_from_log_list(recent_logs, user)})
    result.append({"is_list": True, "date": "6h", "con": get_user_list_from_log_list(quarter_day_logs, user)})
    result.append({"is_list": True, "date": "24h", "con": get_user_list_from_log_list(day_logs, user)})
    result.append(
        {"is_list": True, "date": "How about this user?", "con": get_user_list_from_log_list(all_logs, user)})

    if posts.count() < step:
        """
        posts are loaded fully
        """
        # recent_last = timezone.now()
        # recent_before = timezone.now() - timezone.timedelta(hours=6)
        # # end_date = datetime.date(2005, 3, 31)
        # recent_logs = UserUniqueLog.objects.filter(
        #     Q(updated__range=(recent_before, recent_last)) & Q(user__ffollow__user=user)).exclude(
        #     Q(user=user)).order_by('-updated').distinct()[:step]
        #
        # quarter_day_last = timezone.now() - timezone.timedelta(hours=6)
        # quarter_day_before = timezone.now() - timezone.timedelta(hours=24)
        # quarter_day_logs = UserUniqueLog.objects.filter(
        #     Q(updated__range=(quarter_day_before, quarter_day_last)) & Q(user__ffollow__user=user)).exclude(
        #     Q(user=user)).order_by(
        #     '-updated').distinct()
        #
        # day_logs = UserUniqueLog.objects.filter(Q(user__ffollow__user=user)).exclude(
        #     Q(updated__range=(quarter_day_before, recent_last)) | Q(user=user)).order_by(
        #     '-updated').distinct()
        #
        # all_logs = UserUniqueLog.objects.filter().exclude(
        #     Q(user__ffollow__user=user)
        #     | Q(user=user)).order_by(
        #     '-updated').distinct()
        #
        # result.append({"is_list": True, "date": "RECENT", "con": get_user_list_from_log_list(recent_logs, user)})
        # result.append({"is_list": True, "date": "6h", "con": get_user_list_from_log_list(quarter_day_logs, user)})
        # result.append({"is_list": True, "date": "24h", "con": get_user_list_from_log_list(day_logs, user)})
        # result.append(
        #     {"is_list": True, "date": "How about this user?", "con": get_user_list_from_log_list(all_logs, user)})

        # 추천리스트 추가해주자. result.append({"is_list": True, "date": "24h", "con": get_user_list_from_log_list(day_logs, user)})

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def get_received_feed(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)
    step = 10
    print(str(end_id))

    posts = None
    post_last = timezone.now()
    post_before = timezone.now() - timezone.timedelta(minutes=30)
    if end_id is None:
        posts = Post.objects.filter(
            Q(created__range=(post_before, post_last))
        ).exclude(
            Q(user__ffollow__user=user)
            | Q(user=user)
        ).order_by('-created').distinct()[:step]
    else:
        try:
            post = Post.objects.get(uuid=end_id)
        except Post.DoesNotExist as e:
            print(e)
            return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
        posts = Post.objects.filter(
            Q(created__range=(post_before, post_last))
            & Q(pk__lt=post.pk)
        ).exclude(
            Q(user__ffollow__user=user)
            | Q(user=user)
        ).order_by('-created').distinct()[:step]

    result = []
    post_index = 0
    for item in posts:
        post_index += 1
        # if post_index is step - 1:
        #     break
        result.append({"is_list": False, "con": get_serialized_post(item.uuid, user)})
    if posts.count() == 0:
        result.append({"is_list": True, "date": "empty", "con": []})

    if posts.count() < step:
        """
        posts are loaded fully
        """
        result.append({"is_list": True, "date": "no more pings...", "con": []})

    print(str(result))

    recent_last = timezone.now()
    day_before = timezone.now() - timezone.timedelta(hours=144)
    random_day_log = UserUniqueLog.objects.filter(
        Q(updated__range=(day_before, recent_last))).exclude(Q(user__ffollow__user=user) |
                                                             Q(user=user)).order_by('?').distinct()[:step]

    result.append(
        {"is_list": True, "date": "other users?", "con": get_user_list_from_log_list(random_day_log, user)})

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)


@csrf_exempt
def send_instant_ping(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    ping_id = request.POST.get('ping_id', None)
    if ping_id is None:
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    post_create = Post.objects.create(user=user, ping_id=ping_id)

    result = []

    print(str(get_serialized_post(post_create.uuid, user)))

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': {"opt": DEFAULT_PING,
                                                             "is_list": False,
                                                             "con": get_serialized_post(post_create.uuid, user)}},
                        safe=False)


@csrf_exempt
def refresh_ping_search_result(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
    if token_authenticate(request) is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    search_word = request.POST.get('search_word', None)
    content_list = []

    from re import search
    for item in DEFAULT_PINGS:
        if search_word in item.ping_text:
            content_list.append(item.ping_id)

        # if search(search_word, item.ping_text):
        #     content_list.append(item.ping_id)
    print(str(content_list))

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': content_list}, safe=False)


@csrf_exempt
def refresh_search_content_pings(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
    # if token_authenticate(request) is not None:
    #     user = token_authenticate(request)
    if True:

        opts = random.sample(OPTS, 2)

        opts_patch = OPTS_PATCH

        content_list = []
        for opt_item in opts:
            for patch_item in opts_patch:
                if patch_item["opt"] == opt_item:
                    sample_num = len(patch_item["pings"]) if len(patch_item["pings"]) < 10 else 10
                    # sample_num = 2
                    patch_list = random.sample(patch_item["pings"], sample_num)
                    content_element = {"opt": opt_item, "pings": patch_list}
                    content_list.append(content_element)

        print(content_list)

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': content_list}, safe=False)

    else:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        # failed to login


@csrf_exempt
def refresh_recommend_pings(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
    if token_authenticate(request) is not None:
        user = token_authenticate(request)

        pings = random.sample(DEFAULT_PINGS, 5)

        ping_ids = []
        for item in pings:
            ping_ids.append(item.ping_id)

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': {'ping_ids': ping_ids}}, safe=False)

    else:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        # failed to login


@csrf_exempt
def refresh_for_you_pings(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
    if token_authenticate(request) is not None:
        user = token_authenticate(request)

        pings = random.sample(DEFAULT_PINGS, 5)

        ping_ids = []
        for item in pings:
            ping_ids.append(item.ping_id)

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': {'ping_ids': ping_ids}}, safe=False)

    else:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        # failed to login


@csrf_exempt
def log_in(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    account = request.POST.get('account', None)
    password = request.POST.get('password', None)

    success, user = get_user_token(account, password)

    print(user)
    if success:
        content_result = {'token': user.usertoken.token,
                          'profile_username': user.userusername.username,
                          'profile_user_id': user.username,
                          'profile_photo': user.userphoto.file_300_url(),
                          'profile_full_name': user.userfullname.full_name,
                          'profile_email': user.userprimaryemail.email}
        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': content_result}, safe=False)
    else:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': False}}, safe=False)


@csrf_exempt
def sign_up(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    full_name = request.POST.get('full_name', None)
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)

    # 풀네임, 이메일 트림 후 ''인지 체크.

    # validating email and password

    if UserPrimaryEmail.objects.filter(email=email).exists():
        print("user primary mail code")
        return JsonResponse({'rc': FAIL, 'content': {'code': USER_EMAIL_EXIST_PROBLEM}}, safe=False)

    email_success, email_code = user_primary_email_validate(email)
    if not email_success:
        print("email code")
        return JsonResponse({'rc': FAIL, 'content': {'code': email_code}}, safe=False)

    full_name_success, full_name_code = user_full_name_validate(full_name)
    if not full_name_success:
        print("full name success code")
        return JsonResponse({'rc': FAIL, 'content': {'code': full_name_code}}, safe=False)

    # password 조건
    # username 작성시에 password 랑 같지 않게 짜져야 할 것이다.
    password_success, password_code = password_validate(password)
    if not password_success:
        print("password code")
        return JsonResponse({'rc': FAIL, 'content': {'code': password_code}}, safe=False)

    # Then, go to is_valid below
    user_create_success, user = user_create(full_name, email, password)
    if not user_create_success:
        print("user create code")
        return JsonResponse({'rc': FAIL, 'content': {'code': USER_CREATE_FAILED}}, safe=False)

    print("usertoken" + user.usertoken.token)

    content_result = {'token': user.usertoken.token,
                      'profile_username': user.userusername.username,
                      'profile_user_id': user.username,
                      'profile_photo': user.userphoto.file_300_url(),
                      'profile_full_name': user.userfullname.full_name,
                      'profile_email': user.userprimaryemail.email,
                      'code': USER_CREATED}

    return JsonResponse({'rc': 1, 'content': content_result}, safe=False)


@csrf_exempt
def react(request):
    if token_authenticate(request) is not None:

        user = token_authenticate(request)

        if user is None:
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        post_id = request.POST.get('post_id', None)

        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist as e:
            print(post_id)
            print(e)
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        result = None

        if PostReact.objects.filter(user=user, post=post).exists():
            PostReact.objects.filter(user=user, post=post).delete()
            result = False
        else:
            post_react_create = PostReact.objects.create(user=user, post=post)
            result = True

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)

    else:
        # failed to login
        return JsonResponse({'rc': 0})


@csrf_exempt
def react_boolean(request):
    if token_authenticate(request) is not None:

        user = token_authenticate(request)

        if user is None:
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        post_id = request.POST.get('post_id', None)
        boolean = request.POST.get('boolean', None)
        print(boolean)
        print(post_id)

        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist as e:
            print(post_id)
            print(e)
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        created = None

        if boolean == "true":
            created = True
            try:
                PostReact.objects.create(user=user, post=post)
            except Exception as e:
                print(e)
        else:
            created = False
            try:
                PostReact.objects.filter(user=user, post=post).delete()
            except Exception as e:
                print(e)

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': created}, safe=False)

    else:
        # failed to login
        return JsonResponse({'rc': 0})


@csrf_exempt
def follow_boolean(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    user_id = request.POST.get('user_id', None)

    boolean = request.POST.get('boolean', None)
    # import dateutil.parser
    # date = dateutil.parser.parse(request.POST.get('created', None))

    # print("parse date;" + dateparse.parse_date(str(request.POST.get('created', None))))

    user_find = User.objects.get(username=user_id)
    if user_find is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    if user == user_find:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    created = None
    if boolean == "true":
        created = True
        try:
            create_follow = Follow.objects.create(user=user, follow=user_find)
        except Exception as e:
            print(e)

    else:
        created = False
        try:
            Follow.objects.filter(user=user, follow=user_find).delete()
        except Exception as e:
            print(e)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': created}, safe=False)


@csrf_exempt
def add_comment(request):
    if token_authenticate(request) is not None:

        user = token_authenticate(request)

        if user is None:
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        post_id = request.POST.get('post_id', None)

        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist as e:
            print(post_id)
            print(e)
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        comment_text = request.POST.get('comment_text', None)
        comment_text = comment_text.strip()
        if comment_text is None or comment_text == "":
            comment_text = None

        print(str(post_id) + "is post id")

        comment_create = PostComment.objects.create(user=user, post=post, text=comment_text)

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': get_serialized_comment(comment_create, user)},
                            safe=False)

    else:
        # failed to login
        return JsonResponse({'rc': 0})


@csrf_exempt
def add_post(request):
    if token_authenticate(request) is not None:

        user = token_authenticate(request)

        if user is None:
            return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

        ping_id = request.POST.get('ping_id', None)
        ping_text = request.POST.get("ping_text", None)

        post_text = request.POST.get('post_text', None)
        # print("ping_id: "+str(ping_id))
        # print("ping_text: "+str(ping_text))
        print("post_text: " + str(post_text))

        if post_text is None:
            post_text = None
        elif post_text is "":
            post_text = None
        else:
            post_text = post_text.strip()

        post_create = Post.objects.create(user=user, ping_id=ping_id, text=post_text, ping_text=ping_text)
        result = {"is_list": False, "con": get_serialized_post(post_create.uuid, user)}

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)

    else:
        # failed to login
        return JsonResponse({'rc': 0})


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)

        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        return JsonResponse({'resCode': 1})


@csrf_exempt
def test_token(request):
    if token_authenticate(request) is not None:
        user, token = token_authenticate(request)

        print(user)
        print(token)

        return JsonResponse([{'user': user.username, 'token': token}], safe=False)

    else:
        print("No")
    return JsonResponse({'resCode': 1})


@csrf_exempt
def test_post(request):
    if request.method == 'POST':

        master_username = "897096891123671504"
        master_user = User.objects.get(username=master_username)

        target_username = "897294952827569634"

        target_user = User.objects.get(username=target_username)

        a_usersb = User.objects.filter(ffollow__user=master_user).filter(ffollow__user=target_user).all()
        # 마스터 유저가 팔로우 하는 사람 중 타겟 유저도 팔로우 하는 사람을 보여줌.

        b_users = User.objects.filter(fuser__follow=target_user, ffollow__user=master_user).all()
        # 마스터 유저가 팔로우 하는 사람 중 타겟 유저를 팔로우 하는 사람을 보여줌.

        print(a_usersb)
        print(b_users)
        for item in a_usersb:
            print("a_users: " + item.username)

        for item_b in b_users:
            print("b_users: " + item_b.username)

        return JsonResponse({"test": "code"}, safe=False)


@csrf_exempt
def test_json(request):
    if request.method == 'POST':
        name = request.POST.get('name', None)

        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        print("request: " + str(request.POST.get('description', 'null')))
        print("request: " + str(request.POST.get('second', 'null')))

        if email is None:
            return JsonResponse(
                [{'resCode': 1, 'resaCode': 2}, {'resCode': 'string', 'hello': 'my_friend', 'resaCodeaa': 2},
                 {'resCode': 3, 'resaCode': 4}], safe=False)

        print("request: " + str(request))
        print("request: " + str(request.FILES['uploaded_file']))
        print("request: " + str(request.POST))
        print("request: " + str(request.POST['description']))
        print("request: " + str(request.POST.get('description', 'null')))

        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os
        import magic
        #
        # DJANGO_TYPE = request.FILES['uploaded_file'].content_type
        # import magic
        # import tempfile
        # tmp = tempfile.NamedTemporaryFile(delete=False)
        # try:
        #     for chunk in request.FILES['uploaded_file'].chunks():
        #         tmp.write(chunk)
        #     print(magic.from_buffer(tmp.name, mime=True))
        # finally:
        #     os.unlink(tmp.name)
        #     tmp.close()
        mime = magic.Magic(mime=True)
        file_loc = BytesIO(request.FILES['uploaded_file'].read())
        print(mime.from_buffer(file_loc.read()))

        # print(DJANGO_TYPE)
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'

        # if DJANGO_TYPE == 'image/jpeg':
        #     PIL_TYPE = 'jpeg'
        #     FILE_EXTENSION = 'jpg'
        # elif DJANGO_TYPE == 'image/png':
        #     PIL_TYPE = 'png'
        #     FILE_EXTENSION = 'png'
        #     # DJANGO_TYPE == 'image/gif
        # else:
        #     return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})
        #
        test_photo = TestPhoto.objects.create()
        image = Image.open(file_loc)

        # Save the thumbnail
        temp_handle = BytesIO()
        image.save(temp_handle, PIL_TYPE, quality=90)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into ImageField
        print(os.path.split(request.FILES['file'].name)[-1])
        suf = SimpleUploadedFile(os.path.split(request.FILES['uploaded_file'].name)[-1],
                                 temp_handle.read(), content_type='image/jpeg')
        # Save SimpleUploadedFile into image field
        test_photo.file_300.save(
            '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf, save=True)

        temp_handle.close()

        print(test_photo.file_300.url)

        return JsonResponse([{'resCode': 1, 'resaCode': 2}, {'resCode': 3, 'resaCode': 4}], safe=False)


@csrf_exempt
def test_json_dic(request):
    if request.method == 'POST':
        print("request: " + str(request.POST.get('title', 'null')))
        print("request: " + str(request.POST.get('description', 'null')))

        return JsonResponse(
            [{'resCode': 1, 'resaCode': 2}, {'resCode': 'string', 'hello': 'my_friend', 'resaCodeaa': 2},
             {'resCode': 3, 'resaCode': 4}], safe=False)


@csrf_exempt
def test_pic(request):
    if request.method == "POST":
        test_photo = TestPhoto.objects.create()

        DJANGO_TYPE = request.FILES['file'].content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'
            # DJANGO_TYPE == 'image/gif
        else:
            return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os
        x = float(request.POST['x'])
        y = float(request.POST['y'])
        width = float(request.POST['width'])
        height = float(request.POST['height'])
        rotate = float(request.POST['rotate'])
        # Open original photo which we want to thumbnail using PIL's Image
        try:
            with transaction.atomic():

                image = Image.open(BytesIO(request.FILES['file'].read()))
                image_modified = image.rotate(-1 * rotate, expand=True).crop((x, y, x + width, y + height))
                # use our PIL Image object to create the thumbnail, which already
                image = image_modified.resize((300, 300), Image.ANTIALIAS)

                # Save the thumbnail
                temp_handle = BytesIO()
                image.save(temp_handle, PIL_TYPE, quality=90)
                temp_handle.seek(0)

                # Save image to a SimpleUploadedFile which can be saved into ImageField
                # print(os.path.split(request.FILES['file'].name)[-1])
                suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                         temp_handle.read(), content_type=DJANGO_TYPE)
                # Save SimpleUploadedFile into image field
                user_photo.file_300.save(
                    '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                    suf, save=True)

                # request.FILES['file'].seek(0)
                # image = Image.open(BytesIO(request.FILES['file'].read()))

                # use our PIL Image object to create the thumbnail, which already
                image = image_modified.resize((50, 50), Image.ANTIALIAS)

                # Save the thumbnail
                temp_handle = BytesIO()
                image.save(temp_handle, PIL_TYPE, quality=90)
                temp_handle.seek(0)

                # Save image to a SimpleUploadedFile which can be saved into ImageField
                # print(os.path.split(request.FILES['file'].name)[-1])
                suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                         temp_handle.read(), content_type=DJANGO_TYPE)
                # Save SimpleUploadedFile into image field
                # print(os.path.splitext(suf.name)[0])
                # user_photo.file_50.save(
                #     '50_%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                #     suf, save=True)
                user_photo.file_50.save(
                    '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                    suf, save=True)
                return JsonResponse({'res': 1, 'url': user_photo.file_300.url})
        except Exception as e:
            print(e)
            return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})
