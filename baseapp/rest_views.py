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

    success, result = get_user_token(account, password)

    print(result)
    if success:
        return JsonResponse({'rc': SUCCEED_RESPONSE, 'content': {'token': result}}, safe=False)
    else:
        return JsonResponse({'rc': FAILED_RESPONSE, 'content': {'code': result}}, safe=False)


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
    user_create_success, return_value = user_create(full_name, email, password)
    if not user_create_success:
        return JsonResponse({'rc': 1, 'content': {'code': USER_CREATE_FAILED}}, safe=False)

    return JsonResponse({'rc': 1, 'content': {'code': USER_CREATED, 'token': return_value.token}}, safe=False)


@csrf_exempt
def add_post(request):
    if token_authenticate(request) is not None:
        user, token = token_authenticate(request)

        ping_num = request.POST.get('ping_num', None)
        text = request.POST.get('text', None)

        post_create = Post.objects.create(user=user, ping_num=ping_num)

        if text is not None:
            post_text = PostText.objects.create(post=post_create, text=text)

        return JsonResponse({'rc': 1, 'content': [{'user': user.username, 'token': token}]}, safe=False)

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
        # print(os.path.split(request.FILES['file'].name)[-1])
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