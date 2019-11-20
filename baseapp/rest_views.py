import json
import urllib
from urllib.parse import urlparse

import random
from PIL import Image
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

# Create your models here.
# 좋아요 비공개 할 수 있게
# 챗스톡, 페이지픽, 임플린, 챗카부 순으로 만들자.

# ---------------------------------------------------------------------------------------------------------------------------

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

    step = 50

    notices = Notice.objects.filter().exclude().order_by('-created').distinct()[:step]

    result = []

    for item in notices:
        result.append(get_serialized_notice(item, user))
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)





@csrf_exempt
def get_notice(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)

    user = token_authenticate(request)

    if user is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    end_id = request.POST.get('end_id', None)

    step = 50

    notices = Notice.objects.filter().exclude().order_by('-created').distinct()[:step]

    result = []

    for item in notices:
        result.append(get_serialized_notice(item, user))
    print(result)

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)





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

    if firebase_id.instance_id != registration_id:
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
        result.append(get_serialized_user(item, user))

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

    step = 50

    posts = Post.objects.filter().exclude().order_by('-created').distinct()[:step]

    result = []

    post_index = 0
    for item in posts:
        post_index += 1
        if post_index % 10 == 0:
            # 0, 10, 20, 30... 일 때
            pass
        result.append({"opt": DEFAULT_PING, "con": get_serialized_post(item.uuid, user)})
    print(result)

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

    return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': post_create.ping_id}, safe=False)


@csrf_exempt
def refresh_ping_search_result(request):
    if not request.method == "POST":
        return JsonResponse({'rc': 1, 'content': {'code': UNEXPECTED_METHOD}}, safe=False)
    if token_authenticate(request) is None:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': INVALID_TOKEN}}, safe=False)

    search_word = request.POST.get('search_word', None)
    content_list = []

    from re import search
    for item in PINGS:
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

        pings = random.sample(PINGS, 5)

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

        pings = random.sample(PINGS, 5)

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

    content_result = {'token': user.usertoken.token,
                      'profile_username': user.userusername.username,
                      'profile_user_id': user.username,
                      'profile_photo': user.userphoto.file_300_url(),
                      'profile_full_name': user.userfullname.full_name,
                      'profile_email': user.userprimaryemail.email}
    if success:
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
        return JsonResponse({'rc': 1, 'content': {'code': USER_EMAIL_EXIST_PROBLEM}}, safe=False)

    email_success, email_code = user_primary_email_validate(email)
    if not email_success:
        return JsonResponse({'rc': 1, 'content': {'code': email_code}}, safe=False)

    full_name_success, full_name_code = user_full_name_validate(full_name)
    if not full_name_success:
        return JsonResponse({'rc': 1, 'content': {'code': full_name_code}}, safe=False)

    # password 조건
    # username 작성시에 password 랑 같지 않게 짜져야 할 것이다.
    password_success, password_code = password_validate(password)
    if not password_success:
        return JsonResponse({'rc': 1, 'content': {'code': password_code}}, safe=False)

    # Then, go to is_valid below
    user_create_success, user = user_create(full_name, email, password)
    if not user_create_success:
        return JsonResponse({'rc': 1, 'content': {'code': USER_CREATE_FAILED}}, safe=False)

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

        comment_create = PostComment.objects.create(user=user, post=post, text=comment_text)

        result = {"opt": DEFAULT_PING, "con": get_serialized_comment(comment_create)}

        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': result}, safe=False)

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
        print("post_text: "+str(post_text))

        post_text = post_text.strip()
        if post_text is None or post_text == "":
            post_text = None

        post_create = Post.objects.create(user=user, ping_id=ping_id, text=post_text, ping_text=ping_text)
        result = {"opt": DEFAULT_PING, "con": get_serialized_post(post_create.uuid, user)}

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
