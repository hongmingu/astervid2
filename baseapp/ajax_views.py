import json
import urllib
from urllib.parse import urlparse

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
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from authapp import options
from authapp import texts
from object.models import *
from .forms import BAdminGroupPhotoForm, BAdminSoloPhotoForm
from relation.models import *
from notice.models import *
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.utils.html import escape, _js_escapes, normalize_newlines
from object.numbers import *
from decimal import Decimal

from django.db.models import F
from django.utils.timezone import localdate

# Create your models here.
# 좋아요 비공개 할 수 있게
# 챗스톡, 페이지픽, 임플린, 챗카부 순으로 만들자.



# ---------------------------------------------------------------------------------------------------------------------------


@ensure_csrf_cookie
def re_group_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                name = request.POST.get('name', None)
                desc = request.POST.get('desc', None)
                try:
                    with transaction.atomic():
                        group = Group.objects.create(name=name, description=desc, uuid=uuid.uuid4().hex)
                        group_name = GroupName.objects.create(name=name, group=group)
                        group_main_name = GroupMainName.objects.create(group_name=group_name, group=group)
                        group_main_photo = GroupMainPhoto.objects.create(group=group)
                        group_follower_count = GroupFollowerCount.objects.create(group=group)

                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_group_list(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:

                last_pk = request.POST.get('last_pk', None)
                groups = None
                if last_pk == '':
                    groups = Group.objects.all().order_by('-pk').distinct()[:30]
                else:
                    groups = Group.objects.filter(pk__lt=last_pk).order_by('-pk').distinct()[:30]
                output = []
                count = 0
                pk = None
                for group in groups:
                    count = count + 1
                    pk = group.pk
                    sub_output = {
                        'name': group.name,
                        'desc': group.description,
                        'id': group.uuid,
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1,
                                     'output': output,
                                     'last_pk': pk})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_solo_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                name = request.POST.get('name', None)
                desc = request.POST.get('desc', None)
                try:
                    with transaction.atomic():
                        solo = Solo.objects.create(name=name, description=desc, uuid=uuid.uuid4().hex)
                        solo_name = SoloName.objects.create(name=name, solo=solo)
                        solo_main_name = SoloMainName.objects.create(solo_name=solo_name, solo=solo)
                        solo_main_photo = SoloMainPhoto.objects.create(solo=solo)
                        solo_follower_count = SoloFollowerCount.objects.create(solo=solo)

                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_solo_list(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:

                last_pk = request.POST.get('last_pk', None)
                groups = None
                if last_pk == '':
                    solos = Solo.objects.all().order_by('-pk').distinct()[:30]
                else:
                    solos = Solo.objects.filter(pk__lt=last_pk).order_by('-pk').distinct()[:30]
                output = []
                count = 0
                pk = None
                for solo in solos:
                    count = count + 1
                    pk = solo.pk
                    sub_output = {
                        'name': solo.name,
                        'desc': solo.description,
                        'id': solo.uuid,
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1,
                                     'output': output,
                                     'last_pk': pk})

        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_member_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                solo_id = request.POST.get('solo_id', None)
                group_id = request.POST.get('group_id', None)
                solo = None
                try:
                    solo = Solo.objects.get(uuid=solo_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                group = None
                try:
                    group = Group.objects.get(uuid=group_id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                member = None
                try:
                    member = Member.objects.get(group=group, solo=solo)
                except Exception as e:
                    pass
                result = ''
                if member is not None:
                    member.delete()
                    result = 'delete'
                else:
                    member = Member.objects.create(group=group, solo=solo)
                    result = 'create'

                return JsonResponse({'res': 1, 'result': result})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_group_edit(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                if id == '':
                    return JsonResponse({'res': 0})
                group = None
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                main_name = None
                try:
                    main_name = GroupMainName.objects.get(group=group)
                except Exception as e:
                    print(e)

                name_output = []
                names = None
                try:
                    names = GroupName.objects.filter(group=group).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                for name in names:
                    sub_output = {
                        'name': name.name
                    }
                    name_output.append(sub_output)

                main_photo = None

                try:
                    main_photo = group.groupmainphoto.file_300_url()
                except Exception as e:
                    pass

                photos = None
                try:
                    photos = GroupPhoto.objects.filter(group=group).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                photo_ouput = []
                for photo in photos:
                    sub_output = {
                        'photo': photo.file_300_url(),
                        'id': photo.uuid
                    }
                    photo_ouput.append(sub_output)

                member_solos = None
                try:
                    member_solos = Member.objects.filter(group=group).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                member_solo_output = []
                for member_solo in member_solos:
                    sub_output = {
                        'name': member_solo.solo.name,
                        'id': member_solo.solo.uuid,
                        'desc': member_solo.solo.description
                    }
                    member_solo_output.append(sub_output)
                return JsonResponse({'res': 1,
                                     'main_name': main_name.group_name.name,
                                     'name_output': name_output,
                                     'default_name': group.name,
                                     'default_desc': group.description,
                                     'main_photo': main_photo,
                                     'photo_output': photo_ouput,
                                     'member_solo_output': member_solo_output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_group_edit_main_name(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                main_name = request.POST.get('main_name', None)
                main_name = main_name.strip()
                id = request.POST.get('id', None)
                if id == '':
                    return JsonResponse({'res': 0})
                group = None
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                group_main_name = group.groupmainname

                group_name, created = GroupName.objects.get_or_create(name=main_name, group=group)
                group_main_name.group_name = group_name
                group_main_name.save()

                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_group_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                group.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_b_admin_group_upload_photo(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.is_ajax():
                try:
                    group = Group.objects.get(uuid=request.POST['id'])
                except:
                    return JsonResponse({'res': 0})
                try:
                    group_photo = GroupPhoto.objects.create(group=group, uuid=uuid.uuid4().hex)
                except:
                    return JsonResponse({'res': 0})
                form = BAdminGroupPhotoForm(request.POST, request.FILES, instance=group_photo)
                if form.is_valid():

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
                            image.save(temp_handle, PIL_TYPE, quality=95)
                            temp_handle.seek(0)

                            # Save image to a SimpleUploadedFile which can be saved into ImageField
                            # print(os.path.split(request.FILES['file'].name)[-1])
                            suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                                     temp_handle.read(), content_type=DJANGO_TYPE)
                            # Save SimpleUploadedFile into image field
                            group_photo.file_300.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)

                            # request.FILES['file'].seek(0)
                            # image = Image.open(BytesIO(request.FILES['file'].read()))

                            # use our PIL Image object to create the thumbnail, which already
                            image = image_modified.resize((50, 50), Image.ANTIALIAS)

                            # Save the thumbnail
                            temp_handle = BytesIO()
                            image.save(temp_handle, PIL_TYPE, quality=95)
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
                            group_photo.file_50.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)

                            if not group.groupmainphoto.group_photo:
                                group_main_photo = group.groupmainphoto
                                group_main_photo.uuid = group_photo.uuid
                                group_main_photo.group_photo = group_photo
                                group_main_photo.save()

                            return JsonResponse({'res': 1, 'url': group_photo.file_300_url()})
                    except Exception:
                        return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

            return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})


@ensure_csrf_cookie
def re_b_admin_group_edit_main_photo_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                photo_id = request.POST.get('photo_id', None)
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                group_photo = None
                try:
                    group_photo = GroupPhoto.objects.get(uuid=photo_id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                group_main_photo = group.groupmainphoto
                group_main_photo.uuid = group_photo.uuid
                group_main_photo.group_photo = group_photo
                group_main_photo.save()

                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_b_admin_group_edit_photo_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                photo_id = request.POST.get('photo_id', None)
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                group_photo = None
                try:
                    group_photo = GroupPhoto.objects.get(uuid=photo_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                group_main_photo = group.groupmainphoto
                if group_main_photo.uuid == group_photo.uuid or group_main_photo.group_photo == group_photo:
                    return JsonResponse({'res': 0})
                group_photo.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_b_admin_group_edit_name_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                group_name = None
                try:
                    group_name = GroupName.objects.get(name=name, group=group)
                except Exception as e:
                    return JsonResponse({'res': 0})

                group_main_name = group.groupmainname
                if group_main_name.group_name == group_name:
                    return JsonResponse({'res': 0})
                group_name.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_group_edit_name_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                group_name = None
                try:
                    group_name = GroupName.objects.create(name=name, group=group)
                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_group_edit_default_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                desc = request.POST.get('desc', None)
                desc = desc.strip()
                try:
                    group = Group.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                try:
                    group.name = name
                    group.description = desc
                    group.save()
                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})
# -----------------------------------------------------------------------------


@ensure_csrf_cookie
def re_b_admin_solo_edit(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                if id == '':
                    return JsonResponse({'res': 0})
                solo = None
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                main_name = None
                try:
                    main_name = SoloMainName.objects.get(solo=solo)
                except Exception as e:
                    print(e)

                name_output = []
                names = None
                try:
                    names = SoloName.objects.filter(solo=solo).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                for name in names:
                    sub_output = {
                        'name': name.name
                    }
                    name_output.append(sub_output)

                main_photo = None

                try:
                    main_photo = solo.solomainphoto.file_300_url()
                except Exception as e:
                    pass

                photos = None
                try:
                    photos = SoloPhoto.objects.filter(solo=solo).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                photo_ouput = []
                for photo in photos:
                    sub_output = {
                        'photo': photo.file_300_url(),
                        'id': photo.uuid
                    }
                    photo_ouput.append(sub_output)

                member_groups = None
                try:
                    member_groups = Member.objects.filter(solo=solo).order_by('-created')
                except Exception as e:
                    return JsonResponse({'res': 0})

                member_group_output = []
                for member_group in member_groups:
                    sub_output = {
                        'name': member_group.group.name,
                        'id': member_group.group.uuid,
                        'desc': member_group.group.description
                    }
                    member_group_output.append(sub_output)
                return JsonResponse({'res': 1,
                                     'main_name': main_name.solo_name.name,
                                     'name_output': name_output,
                                     'default_name': solo.name,
                                     'default_desc': solo.description,
                                     'main_photo': main_photo,
                                     'photo_output': photo_ouput,
                                     'member_group_output': member_group_output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_solo_edit_main_name(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                main_name = request.POST.get('main_name', None)
                main_name = main_name.strip()
                id = request.POST.get('id', None)
                if id == '':
                    return JsonResponse({'res': 0})
                solo = None
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_main_name = solo.solomainname

                solo_name, created = SoloName.objects.get_or_create(name=main_name, solo=solo)
                solo_main_name.solo_name = solo_name
                solo_main_name.save()

                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_solo_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                solo.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_b_admin_solo_upload_photo(request):
    if request.method == "POST":
        if request.user.is_authenticated:

            if request.is_ajax():
                try:
                    solo = Solo.objects.get(uuid=request.POST['id'])
                except:
                    return JsonResponse({'res': 0})
                try:
                    solo_photo = SoloPhoto.objects.create(solo=solo, uuid=uuid.uuid4().hex)
                except:
                    return JsonResponse({'res': 0})
                form = BAdminSoloPhotoForm(request.POST, request.FILES, instance=solo_photo)
                if form.is_valid():

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
                            image.save(temp_handle, PIL_TYPE, quality=95)
                            temp_handle.seek(0)

                            # Save image to a SimpleUploadedFile which can be saved into ImageField
                            # print(os.path.split(request.FILES['file'].name)[-1])
                            suf = SimpleUploadedFile(os.path.split(request.FILES['file'].name)[-1],
                                                     temp_handle.read(), content_type=DJANGO_TYPE)
                            # Save SimpleUploadedFile into image field
                            solo_photo.file_300.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)

                            # request.FILES['file'].seek(0)
                            # image = Image.open(BytesIO(request.FILES['file'].read()))

                            # use our PIL Image object to create the thumbnail, which already
                            image = image_modified.resize((50, 50), Image.ANTIALIAS)

                            # Save the thumbnail
                            temp_handle = BytesIO()
                            image.save(temp_handle, PIL_TYPE, quality=95)
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
                            solo_photo.file_50.save(
                                '%s.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
                                suf, save=True)

                            if not solo.solomainphoto.solo_photo:
                                solo_main_photo = solo.solomainphoto
                                solo_main_photo.uuid = solo_photo.uuid
                                solo_main_photo.solo_photo = solo_photo
                                solo_main_photo.save()

                            return JsonResponse({'res': 1, 'url': solo_photo.file_300_url()})
                    except Exception:
                        return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

            return JsonResponse({'res': 0, 'message': texts.UNEXPECTED_ERROR})

@ensure_csrf_cookie
def re_b_admin_solo_edit_main_photo_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                photo_id = request.POST.get('photo_id', None)
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_photo = None
                try:
                    solo_photo = SoloPhoto.objects.get(uuid=photo_id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_main_photo = solo.solomainphoto
                solo_main_photo.uuid = solo_photo.uuid
                solo_main_photo.solo_photo = solo_photo
                solo_main_photo.save()

                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_b_admin_solo_edit_photo_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                photo_id = request.POST.get('photo_id', None)
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_photo = None
                try:
                    solo_photo = SoloPhoto.objects.get(uuid=photo_id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_main_photo = solo.solomainphoto
                if solo_main_photo.uuid == solo_photo.uuid or solo_main_photo.solo_photo == solo_photo:
                    return JsonResponse({'res': 0})
                solo_photo.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_b_admin_solo_edit_name_delete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_name = None
                try:
                    solo_name = SoloName.objects.get(name=name, solo=solo)
                except Exception as e:
                    return JsonResponse({'res': 0})

                solo_main_name = solo.solomainname
                if solo_main_name.solo_name == solo_name:
                    return JsonResponse({'res': 0})
                solo_name.delete()
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_solo_edit_name_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                solo_name = None
                try:
                    solo_name = SoloName.objects.create(name=name, solo=solo)
                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_b_admin_solo_edit_default_register(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_superuser:
                id = request.POST.get('id', None)
                name = request.POST.get('name', None)
                name = name.strip()
                desc = request.POST.get('desc', None)
                desc = desc.strip()
                try:
                    solo = Solo.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                try:
                    solo.name = name
                    solo.description = desc
                    solo.save()
                except Exception as e:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_create_search(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                keyword = request.POST.get('keyword', None)
                group_id = request.POST.get('group_id', None)
                solo_id = request.POST.get('solo_id', None)
                group_end = request.POST.get('group_end', None)
                solo_end = request.POST.get('solo_end', None)
                qs1 = None
                qs2 = None
                from django.db.models.functions import Length

                if solo_end == 'false':
                    if solo_id == '':
                        qs1 = Solo.objects.filter(
                            soloname__name__icontains=keyword).distinct().order_by(Length('name').asc())[:10]
                    else:
                        solo = None
                        try:
                            solo = Solo.objects.get(uuid=solo_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        qs1 = Solo.objects.filter(soloname__name__icontains=keyword,
                                                  pk__gt=solo.pk).distinct().order_by(Length('name').asc())[:10]

                elif solo_end == 'true':
                    qs1 = Solo.objects.none()

                if group_end == 'false':
                    if group_id == '':
                        qs2 = Group.objects.filter(
                            groupname__name__icontains=keyword).distinct().order_by(Length('name').asc())[:10]
                    else:
                        group = None
                        try:
                            group = Group.objects.get(uuid=group_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        qs2 = Group.objects.filter(groupname__name__icontains=keyword,
                                                   pk__gt=group.pk).distinct().order_by(Length('name').asc())[:10]

                elif group_end == 'true':
                    qs2 = Group.objects.none()
                # qs2 = Group.objects.filter(groupname__name__contains=keyword).order_by('created')[:10]
                from itertools import chain
                from operator import attrgetter
                # ascending oreder
                result_list = sorted(
                    chain(qs1, qs2),
                    key=attrgetter('created'))

                # descending order
                # result_list = sorted(
                #     chain(queryset1, queryset2),
                #     key=attrgetter('date_created'),
                #     reverse=True)

                solo_id = ''
                group_id = ''
                solo_end = 'true'
                group_end = 'true'
                output = []
                for item in result_list:
                    kind = ''
                    main_name = None
                    main_photo = None
                    member_list = []
                    if str(item).startswith('group'):
                        kind = 'group'
                        main_name = item.groupmainname.group_name.name
                        main_photo = item.groupmainphoto.file_50_url()
                        group_id = item.uuid
                        group_end = 'false'
                        members = Member.objects.filter(group=item)
                        for i in members:
                            member_list.append(i.solo.solomainname.solo_name.name)
                    elif str(item).startswith('solo'):
                        kind = 'solo'
                        main_name = item.solomainname.solo_name.name
                        main_photo = item.solomainphoto.file_50_url()
                        solo_id = item.uuid
                        solo_end = 'false'
                        members = Member.objects.filter(solo=item)
                        for i in members:
                            member_list.append(i.group.groupmainname.group_name.name)

                    sub_output = {
                        'kind': kind,
                        'main_name': main_name,
                        'main_photo': main_photo,
                        'id': item.uuid,
                        'member': member_list

                    }
                    output.append(sub_output)

                return JsonResponse({'res': 1,
                                     'output': output,
                                     'group_id': group_id,
                                     'solo_id': solo_id,
                                     'group_end': group_end,
                                     'solo_end': solo_end})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_check_server_time(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                from django.utils.timezone import localtime
                time = localtime()
                return JsonResponse({'res': 1, 'time': time})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_group_post(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                group_id = request.POST.get('obj_id', None)
                group = None
                try:
                    group = Group.objects.get(uuid=group_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                output = {
                    'main_name': group.groupmainname.group_name.name,
                    'main_photo': group.groupmainphoto.file_300_url(),
                    'wallet': request.user.wallet.gross,
                }

                return JsonResponse({'res': 1, 'output': output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_group_post_complete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                group_id = request.POST.get('obj_id', None)
                gross = request.POST.get('gross', None)
                text = request.POST.get('text', None)
                gross = Decimal(gross)
                group = None
                try:
                    group = Group.objects.get(uuid=group_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                wallet = None

                try:
                    wallet = Wallet.objects.get(user=request.user)
                except Exception as e:

                    print(e)
                    return JsonResponse({'res': 0})

                if wallet.gross < gross:
                    return JsonResponse({'res': 0})

                text = text.strip()
                if text == '':
                    text = None
                id = uuid.uuid4().hex

                try:
                    with transaction.atomic():
                        post = Post.objects.create(gross=gross, user=request.user, uuid=id)
                        post_text = PostText.objects.create(post=post, text=text)

                        local_date = localdate()

                        group_date, created = GroupDate.objects.get_or_create(group=group, date=local_date)
                        group_post = GroupPost.objects.create(post=post, group=group, group_date=group_date)

                        group_date.gross = F('gross') + gross
                        group_date.save()

                        pay_log = PayLog.objects.create(post=post,
                                                        kind='post_group',
                                                        gross=gross,
                                                        uuid=uuid.uuid4().hex,
                                                        wallet=wallet,
                                                        post_uuid=post.uuid,
                                                        user_id=request.user.username,
                                                        username=request.user.userusername.username)

                        wallet.gross = F('gross') - gross
                        wallet.save()
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'id': id})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_solo_post(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                solo_id = request.POST.get('obj_id', None)
                solo = None
                try:
                    solo = Solo.objects.get(uuid=solo_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                output = {
                    'main_name': solo.solomainname.solo_name.name,
                    'main_photo': solo.solomainphoto.file_300_url(),
                    'wallet': request.user.wallet.gross,
                }

                return JsonResponse({'res': 1, 'output': output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_create_solo_post_complete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                solo_id = request.POST.get('obj_id', None)
                gross = request.POST.get('gross', None)
                text = request.POST.get('text', None)
                gross = Decimal(gross)
                solo = None
                try:
                    solo = Solo.objects.get(uuid=solo_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                wallet = None

                try:
                    wallet = Wallet.objects.get(user=request.user)
                except Exception as e:

                    print(e)
                    return JsonResponse({'res': 0})

                if wallet.gross < gross:
                    return JsonResponse({'res': 0})

                text = text.strip()
                if text == '':
                    text = None
                id = uuid.uuid4().hex
                try:
                    with transaction.atomic():
                        post = Post.objects.create(gross=gross, user=request.user, uuid=id)
                        post_text = PostText.objects.create(post=post, text=text)
                        local_date = localdate()
                        solo_date, created = SoloDate.objects.get_or_create(solo=solo, date=local_date)

                        solo_date.gross = F('gross') + gross
                        solo_date.save()
                        solo_post = SoloPost.objects.create(post=post, solo=solo, solo_date=solo_date)
                        pay_log = PayLog.objects.create(post=post,
                                                        kind='post_solo',
                                                        gross=gross,
                                                        uuid=uuid.uuid4().hex,
                                                        wallet=wallet,
                                                        post_uuid=post.uuid,
                                                        user_id=request.user.username,
                                                        username=request.user.userusername.username)
                        wallet.gross = F('gross') - gross
                        wallet.save()

                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'id': id})
        return JsonResponse({'res': 2})

# update start

@ensure_csrf_cookie
def re_update_group_post(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                id = request.POST.get('id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                post_text = None
                try:
                    post_text = PostText.objects.filter(post=post).last()
                except Exception as e:
                    return JsonResponse({'res': 0})

                output = {
                    'main_name': post.grouppost.group.groupmainname.group_name.name,
                    'main_photo': post.grouppost.group.groupmainphoto.file_300_url(),
                    'gross': post.gross,
                    'date': post.grouppost.group_date.date,
                    'text': post_text.text
                }

                return JsonResponse({'res': 1, 'output': output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_update_group_post_complete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                id = request.POST.get('id', None)
                text = request.POST.get('text', None)
                post = None
                try:
                    post = Post.objects.get(uuid=id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                text = text.strip()
                if text == '':
                    text = None
                if post.posttext_set.last().text == text:
                    pass
                else:
                    post_text = PostText.objects.create(post=post, text=text)
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_update_solo_post(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                id = request.POST.get('id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                post_text = None
                try:
                    post_text = PostText.objects.filter(post=post).last()
                except Exception as e:
                    return JsonResponse({'res': 0})

                output = {
                    'main_name': post.solopost.solo.solomainname.solo_name.name,
                    'main_photo': post.solopost.solo.solomainphoto.file_300_url(),
                    'gross': post.gross,
                    'date': post.solopost.solo_date.date,
                    'text': post_text.text
                }

                return JsonResponse({'res': 1, 'output': output})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_update_solo_post_complete(request):
    if request.method == "POST":
        if request.is_ajax():
            if request.user.is_authenticated:
                id = request.POST.get('id', None)
                text = request.POST.get('text', None)
                post = None
                try:
                    post = Post.objects.get(uuid=id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                text = text.strip()
                if text == '':
                    text = None
                if post.posttext_set.last().text == text:
                    pass
                else:
                    post_text = PostText.objects.create(post=post, text=text)
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_profile_post(request):
    if request.method == "POST":
        if request.is_ajax():
            chosen_user_id = request.POST.get('chosen_user_id', None)
            last_id = request.POST.get('last_post_id', None)
            user = None
            step = 20
            try:
                user = User.objects.get(username=chosen_user_id)
            except User.DoesNotExist:
                return JsonResponse({'res': 0})
            posts = None

            if last_id == '':
                posts = Post.objects.filter(Q(user=user)).order_by('-created').distinct()[:step]
            else:
                last_post = None
                try:
                    last_post = Post.objects.get(uuid=last_id)
                except Exception as e:
                    return JsonResponse({'res': 0})
                if last_post is not None:
                    posts = Post.objects.filter(
                        Q(user=user) & Q(pk_lt=last_post.pk)).order_by('-created').distinct()[:step]

            output = []
            count = 0
            last = None
            sub_output = None
            obj_type = None
            for post in posts:
                count = count + 1
                if count == step:
                    last = post.uuid

                obj_type = 'solo'
                try:
                    type_check = post.solopost
                except Exception as e:
                    obj_type = 'group'

                sub_output = {
                    'id': post.uuid,
                    'obj_type': obj_type
                }

                output.append(sub_output)

            return JsonResponse({'res': 1, 'output': output, 'last': last})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_post_populate(request):
    if request.method == "POST":
        if request.is_ajax():
            post_id = request.POST.get('post_id', None)
            obj_type = request.POST.get('obj_type', None)
            post = None
            try:
                post = Post.objects.get(uuid=post_id)
            except Exception as e:
                print(e)
                return JsonResponse({'res': 0})
            ################################
            obj_id = None
            date = None
            obj_name = None
            if obj_type == 'solo':
                obj_id = post.solopost.solo.uuid
                date = post.solopost.solo_date.date
                obj_name = post.solopost.solo.solomainname.solo_name.name
            else:
                obj_id = post.grouppost.group.uuid
                date = post.grouppost.group_date.date
                obj_name = post.grouppost.group.groupmainname.group_name.name

            comment_output = []
            comments = PostComment.objects.filter(post=post).order_by('created')[:3]
            for comment in comments:
                sub_output = {
                    'comment_username': comment.user.userusername.username,
                    'comment_user_id': comment.user.username,
                    'comment_text': escape(comment.text),
                    'comment_id': comment.uuid,
                    'comment_created': comment.created
                }
                comment_output.append(sub_output)

            like = 'false'
            if request.user.is_authenticated:
                if PostLike.objects.filter(post=post, user=request.user).exists():
                    like = 'true'

            output = {
                'user_id': post.user.username,
                'username': post.user.userusername.username,
                'text': escape(post.posttext_set.last().text),
                'gross': post.gross,
                'created': post.created,
                'date': date,
                'like_count': post.postlikecount.count,
                'like': like,
                'obj_id': obj_id,
                'obj_name': obj_name,
                'comment_count': post.postcommentcount.count,
                'comment_output': comment_output,
            }

            return JsonResponse({'res': 1, 'output': output})

        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_comment_add(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                text = request.POST.get('text', None)
                text = text.strip()
                try:
                    post = Post.objects.get(uuid=post_id)
                    # post = Post.objects.last()
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                try:
                    with transaction.atomic():
                        post_comment = PostComment.objects.create(post=post, user=request.user, uuid=uuid.uuid4().hex,
                                                                  text=text)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'comment_id': post_comment.uuid, 'comment_text': escape(post_comment.text)})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_comment_delete(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                comment_id = request.POST.get('comment_id', None)
                post_id = request.POST.get('post_id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                comment = None
                try:
                    comment = PostComment.objects.get(uuid=comment_id, post=post, user=request.user)
                except Exception as e:
                    try:
                        comment = PostComment.objects.get(uuid=comment_id, post=post, post__user=request.user)
                    except Exception as e:
                        return JsonResponse({'res': 0})

                try:
                    with transaction.atomic():
                        comment.delete()
                except Exception:
                    return JsonResponse({'res': 0})
                return JsonResponse({'res': 1})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_comment_more_load(request):
    if request.method == "POST":
        # comment more load 에선 로그인이 필요없게 하였다.
        if request.is_ajax():
            post_id = request.POST.get('post_id', None)
            last_comment_id = request.POST.get('last_comment_id', None)
            post = None
            step = 20
            try:
                post = Post.objects.get(uuid=post_id)
            except Exception as e:
                return JsonResponse({'res': 0})

            post_comment_last = None
            try:
                post_comment_last = PostComment.objects.get(uuid=last_comment_id)
            except Exception as e:
                return JsonResponse({'res': 0})

            post_comments = PostComment.objects.filter(post=post, pk__gt=post_comment_last.pk).order_by('created')[:step]
            output = []
            last = None
            count = 0

            for comment in post_comments:
                count = count + 1
                if count == step:
                    last = comment.uuid
                sub_output = {
                    'comment_username': comment.user.userusername.username,
                    'comment_user_id': comment.user.username,
                    'comment_text': escape(comment.text),
                    'comment_id': comment.uuid,
                    'comment_created': comment.created
                }
                output.append(sub_output)

            return JsonResponse({'res': 1, 'output': output, 'last': last})
        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_like(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)

                post = None
                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception as e:
                    return JsonResponse({'res': 0})

                post_like = None
                try:
                    post_like = PostLike.objects.get(post=post, user=request.user)
                except Exception as e:
                    pass

                liked = None
                if post_like is not None:
                    try:
                        with transaction.atomic():
                            post_like.delete()
                            liked = 'false'
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                else:
                    try:
                        with transaction.atomic():
                            post_like = PostLike.objects.create(post=post, user=request.user)
                            liked = 'true'
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'liked': liked})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_post_like_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                next_id = request.POST.get('next_id', None)
                post = None
                step = 31
                try:
                    post = Post.objects.get(uuid=post_id)
                except Exception as e:
                    return JsonResponse({'res': 1})

                next = None
                output = []
                if post is not None:
                    if next_id == '':
                        likes = PostLike.objects.filter(post=post).order_by('created')[:step]
                    else:
                        try:
                            last_like = PostLike.objects.get(post=post, user__username=next_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        likes = PostLike.objects.filter(Q(post=post) & Q(pk__gte=last_like.pk)).order_by('created')[:step]

                    count = 0
                    for like in likes:
                        count = count+1
                        if count == step:
                            next = like.user.username
                            break
                        sub_output = {
                            'username': like.user.userusername.username,
                            'photo': like.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'next': next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_follow_add(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                chosen_user_id = request.POST.get('user_id', None)
                chosen_user = None
                try:
                    chosen_user = User.objects.get(username=chosen_user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                if chosen_user is not None:
                    # 어이없는 스스로 팔로우 방지
                    if chosen_user == request.user:
                        return JsonResponse({'res': 0})
                    follow = None
                    try:
                        follow = Follow.objects.get(follow=chosen_user, user=request.user)
                    except Follow.DoesNotExist:
                        pass
                    result = None
                    if follow is not None:
                        try:
                            with transaction.atomic():
                                follow.delete()

                                result = False

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                follow = Follow.objects.create(follow=chosen_user, user=request.user)
                                result = True

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception:
                            return JsonResponse({'res': 0})
                    return JsonResponse({'res': 1, 'result': result})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_following_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_user_id', None)
                user = None
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})


                next = None
                output = []
                step = 31
                if user is not None:
                    if next_id == '':
                        followings = Follow.objects.filter(user=user).order_by('created')[:step]
                    else:
                        try:
                            last_following = Follow.objects.get(follow__username=next_id, user=user)
                        except:
                            return JsonResponse({'res': 0})
                        followings = Follow.objects.filter(Q(user=user) & Q(pk__gte=last_following.pk)).order_by('created')[:step]
                    count = 0
                    for follow in followings:
                        count = count+1
                        if count == 31:
                            next = follow.follow.username
                            break
                        sub_output = {
                            'username': follow.follow.userusername.username,
                            'photo': follow.follow.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'next':next})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_follower_list(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                user_id = request.POST.get('user_id', None)
                next_id = request.POST.get('next_user_id', None)
                user = None
                step = 31
                try:
                    user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                next = None
                output = []
                if user is not None:
                    if next_id == '':
                        followers = Follow.objects.filter(follow=user).order_by('created')[:step]
                    else:
                        try:
                            last_follower = Follow.objects.get(follow=user, user__username=next_id)
                        except Exception as e:
                            return JsonResponse({'res': 0})
                        followers = Follow.objects.filter(Q(follow=user) & Q(pk__gte=last_follower.pk)).order_by('created')[:step]
                    count = 0
                    for follow in followers:
                        count = count+1
                        if count == 31:
                            next = follow.user.username
                            break
                        sub_output = {
                            'username': follow.user.userusername.username,
                            'photo': follow.user.userphoto.file_50_url(),
                        }
                        output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'next': next})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_solo_follow(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                solo_id = request.POST.get('obj_id', None)
                solo = None
                try:
                    solo = Solo.objects.get(uuid=solo_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                if solo is not None:
                    follow = None
                    try:
                        follow = SoloFollow.objects.get(solo=solo, user=request.user)
                    except Exception as e:
                        pass
                    result = None
                    if follow is not None:
                        try:
                            with transaction.atomic():
                                follow.delete()

                                result = 'cancel'

                        except Exception as e:
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                follow = SoloFollow.objects.create(solo=solo, user=request.user)
                                result = 'follow'

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception as e:
                            return JsonResponse({'res': 0})
                    return JsonResponse({'res': 1, 'result': result})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_group_follow(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                group_id = request.POST.get('obj_id', None)
                group = None
                try:
                    group = Group.objects.get(uuid=group_id)
                except User.DoesNotExist:
                    return JsonResponse({'res': 0})

                if group is not None:
                    follow = None
                    try:
                        follow = GroupFollow.objects.get(group=group, user=request.user)
                    except Exception as e:
                        pass
                    result = None
                    if follow is not None:
                        try:
                            with transaction.atomic():
                                follow.delete()

                                result = 'cancel'

                        except Exception as e:
                            return JsonResponse({'res': 0})
                    else:
                        try:
                            with transaction.atomic():
                                follow = GroupFollow.objects.create(group=group, user=request.user)
                                result = 'follow'

                                # customers = Customer.objects.filter(scoops_ordered__gt=F('store_visits'))
                        except Exception as e:
                            return JsonResponse({'res': 0})
                    return JsonResponse({'res': 1, 'result': result})

                return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_profile_post_delete(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                post_id = request.POST.get('post_id', None)
                post = None
                try:
                    post = Post.objects.get(uuid=post_id, user=request.user)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})
                if post is not None:
                    post.delete()

                return JsonResponse({'res': 1})

        return JsonResponse({'res': 2})





@ensure_csrf_cookie
def re_home_rank(request):
    if request.method == "POST":
        if request.is_ajax():
            day = request.POST.get('day', None)

            qs1 = SoloDate.objects.filter(date=day).order_by('-gross')[:3]
            qs2 = GroupDate.objects.filter(date=day).order_by('-gross')[:3]
            # qs2 = Group.objects.filter(groupname__name__contains=keyword).order_by('created')[:10]
            from itertools import chain
            from operator import attrgetter
            # ascending oreder
            # result_list = sorted(
            #     chain(qs1, qs2),
            #     key=attrgetter('gross'),
            #     reverse=True
            # )

            result_list = sorted(
                chain(qs1, qs2),
                key=lambda x: (x.gross, -x.updated.timestamp(), -x.created.timestamp()),
                reverse=True
            )
            result_list = result_list[:3]
            # descending order
            # result_list = sorted(
            #     chain(queryset1, queryset2),
            #     key=attrgetter('date_created'),
            #     reverse=True)

            all_output = []
            for item in result_list:
                obj_type = ''
                main_name = None
                main_photo = None
                obj_id = None
                posts = []
                if str(item).startswith('group'):
                    obj_type = 'group'
                    main_name = item.group.groupmainname.group_name.name
                    main_photo = item.group.groupmainphoto.file_50_url()
                    obj_id = item.group.uuid
                    group_posts = GroupPost.objects.filter(group_date=item).order_by('-post__gross')[:3]
                    for s_item in group_posts:
                        ss_output ={
                            'username': s_item.post.user.userusername.username,
                            'gross': s_item.post.gross,
                            'text': s_item.post.posttext_set.last().text,
                            'post_id': s_item.post.uuid
                        }
                        posts.append(ss_output)
                elif str(item).startswith('solo'):
                    obj_type = 'solo'
                    main_name = item.solo.solomainname.solo_name.name
                    main_photo = item.solo.solomainphoto.file_50_url()
                    obj_id = item.solo.uuid
                    solo_posts = SoloPost.objects.filter(solo_date=item).order_by('-post__gross')[:3]
                    for s_item in solo_posts:
                        ss_output ={
                            'username': s_item.post.user.userusername.username,
                            'gross': s_item.post.gross,
                            'text': s_item.post.posttext_set.last().text,
                            'post_id': s_item.post.uuid
                        }
                        posts.append(ss_output)
                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'gross': item.gross,
                    'obj_id': obj_id,
                    'posts': posts,
                }
                all_output.append(sub_output)

            solo_output = []
            for item in qs1:
                posts = []
                solo_posts = SoloPost.objects.filter(solo_date=item).order_by('-post__gross')[:3]

                for s_item in solo_posts:
                    ss_output = {
                        'username': s_item.post.user.userusername.username,
                        'gross': s_item.post.gross,
                        'text': s_item.post.posttext_set.last().text,
                        'post_id': s_item.post.uuid
                    }
                    posts.append(ss_output)

                sub_output = {
                    'obj_type': 'solo',
                    'main_name': item.solo.solomainname.solo_name.name,
                    'main_photo': item.solo.solomainphoto.file_50_url(),
                    'gross': item.gross,
                    'obj_id': item.solo.uuid,
                    'posts': posts
                }
                solo_output.append(sub_output)

            group_output = []
            for item in qs2:
                posts = []
                group_posts = GroupPost.objects.filter(group_date=item).order_by('-post__gross')[:3]

                for s_item in group_posts:
                    ss_output = {
                        'username': s_item.post.user.userusername.username,
                        'gross': s_item.post.gross,
                        'text': s_item.post.posttext_set.last().text,
                        'post_id': s_item.post.uuid
                    }
                    posts.append(ss_output)

                sub_output = {
                    'obj_type': 'group',
                    'main_name': item.group.groupmainname.group_name.name,
                    'main_photo': item.group.groupmainphoto.file_50_url(),
                    'gross': item.gross,
                    'obj_id': item.group.uuid,
                    'posts': posts
                }
                group_output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'all_output': all_output,
                                 'group_output': group_output,
                                 'solo_output': solo_output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_all_rank(request):
    if request.method == "POST":
        if request.is_ajax():
            day = request.POST.get('day', None)
            step = 100

            qs1 = SoloDate.objects.filter(date=day).order_by('-gross')[:step]
            qs2 = GroupDate.objects.filter(date=day).order_by('-gross')[:step]
            # qs2 = Group.objects.filter(groupname__name__contains=keyword).order_by('created')[:10]
            from itertools import chain
            from operator import attrgetter
            # ascending oreder
            # result_list = sorted(
            #     chain(qs1, qs2),
            #     key=attrgetter('gross'),
            #     reverse=True
            # )

            result_list = sorted(
                chain(qs1, qs2),
                key=lambda x: (x.gross, -x.updated.timestamp(), -x.created.timestamp()),
                reverse=True
            )
            result_list = result_list[:step]
            # descending order
            # result_list = sorted(
            #     chain(queryset1, queryset2),
            #     key=attrgetter('date_created'),
            #     reverse=True)

            output = []
            for item in result_list:
                obj_type = ''
                main_name = None
                main_photo = None
                obj_id = None
                posts = []
                if str(item).startswith('group'):
                    obj_type = 'group'
                    main_name = item.group.groupmainname.group_name.name
                    main_photo = item.group.groupmainphoto.file_50_url()
                    obj_id = item.group.uuid
                    group_posts = GroupPost.objects.filter(group_date=item).order_by('-post__gross')[:3]
                    for s_item in group_posts:
                        ss_output ={
                            'username': s_item.post.user.userusername.username,
                            'gross': s_item.post.gross,
                            'text': s_item.post.posttext_set.last().text,
                            'post_id': s_item.post.uuid
                        }
                        posts.append(ss_output)
                elif str(item).startswith('solo'):
                    obj_type = 'solo'
                    main_name = item.solo.solomainname.solo_name.name
                    main_photo = item.solo.solomainphoto.file_50_url()
                    obj_id = item.solo.uuid
                    solo_posts = SoloPost.objects.filter(solo_date=item).order_by('-post__gross')[:3]
                    for s_item in solo_posts:
                        ss_output ={
                            'username': s_item.post.user.userusername.username,
                            'gross': s_item.post.gross,
                            'text': s_item.post.posttext_set.last().text,
                            'post_id': s_item.post.uuid
                        }
                        posts.append(ss_output)
                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'gross': item.gross,
                    'obj_id': obj_id,
                    'posts': posts,
                }
                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_solo_rank(request):
    if request.method == "POST":
        if request.is_ajax():
            day = request.POST.get('day', None)
            step = 100
            qs1 = SoloDate.objects.filter(date=day).order_by('-gross')[:step]

            output = []
            for item in qs1:
                posts = []
                solo_posts = SoloPost.objects.filter(solo_date=item).order_by('-post__gross')[:3]

                for s_item in solo_posts:
                    ss_output = {
                        'username': s_item.post.user.userusername.username,
                        'gross': s_item.post.gross,
                        'text': s_item.post.posttext_set.last().text,
                        'post_id': s_item.post.uuid
                    }
                    posts.append(ss_output)

                sub_output = {
                    'obj_type': 'solo',
                    'main_name': item.solo.solomainname.solo_name.name,
                    'main_photo': item.solo.solomainphoto.file_50_url(),
                    'gross': item.gross,
                    'obj_id': item.solo.uuid,
                    'posts': posts
                }
                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_group_rank(request):
    if request.method == "POST":
        if request.is_ajax():
            day = request.POST.get('day', None)
            step = 100
            qs2 = GroupDate.objects.filter(date=day).order_by('-gross')[:step]

            output = []
            for item in qs2:
                posts = []
                group_posts = GroupPost.objects.filter(group_date=item).order_by('-post__gross')[:3]

                for s_item in group_posts:
                    ss_output = {
                        'username': s_item.post.user.userusername.username,
                        'gross': s_item.post.gross,
                        'text': s_item.post.posttext_set.last().text,
                        'post_id': s_item.post.uuid
                    }
                    posts.append(ss_output)

                sub_output = {
                    'obj_type': 'group',
                    'main_name': item.group.groupmainname.group_name.name,
                    'main_photo': item.group.groupmainphoto.file_50_url(),
                    'gross': item.gross,
                    'obj_id': item.group.uuid,
                    'posts': posts
                }
                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output})

        return JsonResponse({'res': 2})

# home 이건 뭐건 rank 에서 그 object 누르면 /solo/post/uuid/ 여기로 가는 거 그리고 post 누르면 그 /post/uuid 로 가는거 구현


@ensure_csrf_cookie
def re_solo_posts(request):
    if request.method == "POST":
        if request.is_ajax():
            obj_id = request.POST.get('obj_id', None)
            end_id = request.POST.get('end_id', None)
            solo = None
            step = 30
            try:
                solo = Solo.objects.get(uuid=obj_id)
            except Exception as e:
                print(e)
                return JsonResponse({'res': 0})

            if solo is not None:

                if end_id == '':
                    posts = Post.objects.filter(solopost__solo=solo).order_by('-created')[:step]
                else:
                    try:
                        end_post = Post.objects.get(uuid=end_id)
                    except Exception as e:
                        return JsonResponse({'res': 0})
                    posts = Post.objects.filter(solopost__solo=solo, pk__lt=end_post.pk).order_by('-created')[:step]

                output = []
                count = 0
                end = None
                for post in posts:
                    count = count + 1
                    if count == 30:
                        end = post.uuid
                    output.append(post.uuid)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

            return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_group_posts(request):
    if request.method == "POST":
        if request.is_ajax():
            obj_id = request.POST.get('obj_id', None)
            end_id = request.POST.get('end_id', None)
            group = None
            step = 30
            try:
                group = Group.objects.get(uuid=obj_id)
            except Exception as e:
                print(e)
                return JsonResponse({'res': 0})
            if group is not None:

                if end_id == '':
                    posts = Post.objects.filter(grouppost__group=group).order_by('-created')[:step]
                else:
                    try:
                        end_post = Post.objects.get(uuid=end_id)
                    except Exception as e:
                        return JsonResponse({'res': 0})
                    posts = Post.objects.filter(grouppost__group=group, pk__lt=end_post.pk).order_by('-created')[:step]

                output = []
                count = 0
                end = None
                for post in posts:
                    count = count + 1
                    if count == 30:
                        end = post.uuid
                    output.append(post.uuid)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

            return JsonResponse({'res': 2})

        return JsonResponse({'res': 2})



@ensure_csrf_cookie
def re_search_all(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            user_step = 5
            users = User.objects.filter(Q(userusername__username__icontains=search_word)
                                        | Q(usertextname__name__icontains=search_word)).order_by(
                '-userusername__created').distinct()[:user_step]
            user_output = []
            for user in users:
                sub_output = {
                    'username': user.userusername.username,
                    'user_text_name': escape(user.usertextname.name),
                }

                user_output.append(sub_output)
            from django.db.models.functions import Length

            obj_step = 10
            solos = Solo.objects.filter(
                soloname__name__icontains=search_word).distinct().order_by(Length('name').asc(), 'pk')[:obj_step]
            solo_output = []

            for item in solos:
                member_list = []
                obj_type = 'solo'
                main_name = item.solomainname.solo_name.name
                main_photo = item.solomainphoto.file_50_url()
                members = Member.objects.filter(solo=item)
                for i in members:
                    member_list.append(i.group.groupmainname.group_name.name)

                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'id': item.uuid,
                    'member': member_list
                }
                solo_output.append(sub_output)

            groups = Group.objects.filter(
                groupname__name__icontains=search_word).distinct().order_by(Length('name').asc(), 'pk')[:obj_step]
            group_output = []

            for item in groups:
                member_list = []

                obj_type = 'group'
                main_name = item.groupmainname.group_name.name
                main_photo = item.groupmainphoto.file_50_url()
                members = Member.objects.filter(group=item)
                for i in members:
                    member_list.append(i.solo.solomainname.solo_name.name)

                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'id': item.uuid,
                    'member': member_list

                }
                group_output.append(sub_output)

            post_step = 5
            posts = Post.objects.filter(Q(user__userusername__username__icontains=search_word)
                                        | Q(posttext__text__icontains=search_word)
                                        | Q(solopost__solo__soloname__name__icontains=search_word)
                                        | Q(grouppost__group__groupname__name__icontains=search_word)
                                        | Q(user__usertextname__name__icontains=search_word)).order_by(
                'created').distinct()[:post_step]

            post_output = []
            for post in posts:
                sub_output = {
                    'id': post.uuid,
                    'obj_type': post.get_obj_type(),
                }

                post_output.append(sub_output)
            return JsonResponse({'res': 1,
                                 'user_output': user_output,
                                 'solo_output': solo_output,
                                 'group_output': group_output,
                                 'post_output': post_output})

        return JsonResponse({'res': 2})

# 로그인시 검색가능 아닌거 가능 그런거 찾아야한다.
@ensure_csrf_cookie
def re_search_user(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            end_id = request.POST.get('end_id', None)
            step = 20
            if end_id == '':
                users = User.objects.filter(Q(userusername__username__icontains=search_word)
                                            | Q(usertextname__name__icontains=search_word)).distinct().order_by(
                    '-userusername__created')[:step]
            else:
                end_user = None
                try:
                    end_user = User.objects.get(username=end_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                users = User.objects.filter((Q(userusername__username__icontains=search_word)
                                            | Q(usertextname__name__icontains=search_word))
                                            & Q(pk__lt=end_user.pk)).distinct().order_by(
                    '-userusername__created')[:step]
            output = []
            count = 0
            end = None
            for user in users:
                count = count + 1
                if count == step:
                    end = user.username
                sub_output = {
                    'username': user.userusername.username,
                    'user_photo': user.userphoto.file_50_url(),
                    'user_text_name': escape(user.usertextname.name),
                }

                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'end': end})

        return JsonResponse({'res': 2})

# from django.db.models import TextField
#
# TextField.register_lookup(Length)


from django.db.models.functions import Length


@ensure_csrf_cookie
def re_search_solo(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            order = request.POST.get('order', None)
            order = int(order)
            step = 10

            objs = Solo.objects.filter(Q(soloname__name__icontains=search_word)
                                       | Q(description__icontains=search_word)).distinct().order_by(
                Length('name').asc(), 'pk')[order:order+step]
            end = 'false'
            if objs.count() < step:
                end = 'true'

            output = []
            for item in objs:
                member_list = []
                obj_type = 'solo'
                main_name = item.solomainname.solo_name.name
                main_photo = item.solomainphoto.file_50_url()
                members = Member.objects.filter(solo=item)
                for i in members:
                    member_list.append(i.group.groupmainname.group_name.name)

                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'id': item.uuid,
                    'member': member_list
                }
                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'order': order+step,
                                 'end': end})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_search_group(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            order = request.POST.get('order', None)
            order = int(order)
            step = 10

            objs = Group.objects.filter(Q(groupname__name__icontains=search_word)
                                       | Q(description__icontains=search_word)).distinct().order_by(
                Length('name').asc(), 'pk')[order:order+step]
            end = 'false'
            if objs.count() < step:
                end = 'true'

            output = []
            for item in objs:
                member_list = []
                obj_type = 'group'
                main_name = item.groupmainname.group_name.name
                main_photo = item.groupmainphoto.file_50_url()
                members = Member.objects.filter(group=item)
                for i in members:
                    member_list.append(i.solo.solomainname.solo_name.name)

                sub_output = {
                    'obj_type': obj_type,
                    'main_name': main_name,
                    'main_photo': main_photo,
                    'id': item.uuid,
                    'member': member_list

                }
                output.append(sub_output)

            return JsonResponse({'res': 1,
                                 'output': output,
                                 'order': order+step,
                                 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_search_post(request):
    if request.method == "POST":
        if request.is_ajax():
            search_word = request.POST.get('search_word', None)
            end_id = request.POST.get('end_id', None)
            step = 10
            if end_id == '':
                posts = Post.objects.filter(Q(user__userusername__username__icontains=search_word)
                                            | Q(posttext__text__icontains=search_word)
                                            | Q(solopost__solo__soloname__name__icontains=search_word)
                                            | Q(grouppost__group__groupname__name__icontains=search_word)
                                            | Q(user__usertextname__name__icontains=search_word)).distinct().order_by(
                    '-created')[:step]
            else:
                end_post = None
                try:
                    end_post = Post.objects.get(uuid=end_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                posts = Post.objects.filter(((Q(user__userusername__username__icontains=search_word)
                                            | Q(posttext__text__icontains=search_word)
                                            | Q(user__usertextname__name__icontains=search_word)))
                                            & Q(pk__lt=end_post.pk)).distinct().order_by('-created')[:step]

            output = []
            count = 0
            end = None
            for post in posts:
                count = count + 1
                if count == step:
                    end = post.uuid
                sub_output = {
                    'obj_type': post.get_obj_type(),
                    'id': post.uuid,
                }

                output.append(sub_output)
            return JsonResponse({'res': 1,
                                 'output': output,
                                 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_note_all(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 30
                notices = None
                if end_id == '':
                    notices = Notice.objects.filter(Q(user=request.user)).distinct().order_by('-created')[:step]
                else:
                    end_notice = None
                    try:
                        end_notice = Notice.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    notices = Notice.objects.filter(Q(user=request.user) & Q(pk__lt=end_notice.pk)).distinct().order_by(
                        '-created')[:step]

                output = []
                count = 0
                end = None
                for notice in notices:
                    count = count + 1
                    if count == step:
                        end = notice.uuid
                    sub_output = {
                        'id': notice.uuid,
                        'created': notice.created,
                        'notice_kind': notice.kind,
                        'notice_value': notice.get_value(),
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_nav_badge_populate(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                try:
                    notice_count = request.user.noticecount.count
                except Exception as e:
                    print(e)
                    return JsonResponse({'res': 0})

                return JsonResponse({'res': 1, 'notice_count': notice_count})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_follow_feed(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 20
                posts = None
                if end_id == '':
                    posts = Post.objects.filter(Q(user__is_followed__user=request.user)
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
                    posts = Post.objects.filter((Q(user__is_followed__user=request.user)
                                                | Q(grouppost__group__is_group_followed__user=request.user)
                                                | Q(solopost__solo__is_solo_followed__user=request.user))
                                                & Q(pk__lt=end_post.pk)).exclude(
                        Q(user=request.user)).order_by('-created').distinct()[:step]

                output = []
                count = 0
                end = None
                for post in posts:
                    count = count + 1
                    if count == step:
                        end = post.uuid

                    sub_output = {
                        'obj_type': post.get_obj_type(),
                        'id': post.uuid,
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})


@ensure_csrf_cookie
def re_log_charge(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 20
                charge_logs = None
                wallet = None
                try:
                    wallet = request.user.wallet
                except Exception as e:
                    return JsonResponse({'res': 1})
                if end_id == '':
                    charge_logs = ChargeLog.objects.filter(Q(wallet=wallet)).order_by('-created').distinct()[:step]
                else:
                    end_charge_log = None
                    try:
                        end_charge_log = ChargeLog.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    charge_logs = ChargeLog.objects.filter(Q(wallet=wallet)
                                                           & Q(pk__lt=end_charge_log.pk)).order_by(
                        '-created').distinct()[:step]

                output = []
                count = 0
                end = None
                for item in charge_logs:
                    count = count + 1
                    if count == step:
                        end = item.uuid

                    sub_output = {
                        'obj_id': item.transaction_id,
                        'created': item.created,
                        'gross': item.gross
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})

@ensure_csrf_cookie
def re_log_pay(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if request.is_ajax():
                end_id = request.POST.get('end_id', None)
                step = 20
                pay_logs = None
                wallet = None
                try:
                    wallet = request.user.wallet
                except Exception as e:
                    return JsonResponse({'res': 1})
                if end_id == '':
                    pay_logs = PayLog.objects.filter(Q(wallet=wallet)).order_by('-created').distinct()[:step]
                else:
                    end_pay_log = None
                    try:
                        end_pay_log = PayLog.objects.get(uuid=end_id)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'res': 0})
                    pay_logs = PayLog.objects.filter(Q(wallet=wallet)
                                                     & Q(pk__lt=end_pay_log.pk)).order_by(
                        '-created').distinct()[:step]

                output = []
                count = 0
                end = None
                for item in pay_logs:
                    count = count + 1
                    if count == step:
                        end = item.uuid

                    sub_output = {
                        'obj_id': item.post_uuid,
                        'created': item.created,
                        'gross': item.gross
                    }

                    output.append(sub_output)

                return JsonResponse({'res': 1, 'output': output, 'end': end})

        return JsonResponse({'res': 2})

