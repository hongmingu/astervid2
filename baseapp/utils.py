import time
import datetime
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction, IntegrityError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authapp.texts import *
from baseapp.token import account_activation_token
from .constants import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


from authapp.models import *
from relation.models import *
from notice.models import *


START_DATETIME = "14/04/2016"
STANDARD_TIME = time.mktime(datetime.datetime.strptime(START_DATETIME, "%d/%m/%Y").timetuple())


def make_id():

    random_time = int(time.time()*1000 - STANDARD_TIME*1000)
    random_bit = random.SystemRandom().getrandbits(23)
    id_number = (random_time << 23) | random_bit
    return str(id_number)


def get_random_time(id_number):
    return id_number >> 23


def get_random_bit(id_number):
    return id_number & 0x7fffff


def get_or_none(queryset, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return None


def user_username_validate(username):
    import re
    if not (re.match('^([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)$', username)):
        return False, USER_USERNAME_VALIDATE_REGEX_PROBLEM
    if not (USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH):
        return False, USER_USERNAME_VALIDATE_LENGTH_PROBLEM
    if (USERNAME_DIGIT_MIN_LENGTH <= len(username)) and username.isdigit():
        return False, USER_USERNAME_VALIDATE_DIGIT_PROBLEM

    # banned username and password
    from authapp import banned
    match_ban = [name for name in banned.BANNED_USERNAME_LIST if name in username]
    if match_ban:
        return False, USER_USERNAME_VALIDATE_BANNED_PROBLEM

    # succeed username validation
    return True, VALIDATE_OK


def user_full_name_validate(full_name):
    if not (USER_FULL_NAME_MIN_LENGTH <= len(full_name) <= USER_FULL_NAME_MAX_LENGTH):
        return False, USER_FULL_NAME_VALIDATE_LENGTH_PROBLEM
    return True, VALIDATE_OK


def user_primary_email_validate(email):
    import re
    if not (re.match('[^@]+@[^@]+\.[^@]+', email)):
        return False, USER_EMAIL_VALIDATE_REGEX_PROBLEM
    if len(email) > USER_EMAIL_MAX_LENGTH:
        return False, USER_EMAIL_VALIDATE_LENGTH_PROBLEM

    return True, VALIDATE_OK


def password_username_validate(username, password):
    if not (USER_PASSWORD_MIN_LENGTH <= len(password) <= USER_PASSWORD_MAX_LENGTH):
        return False, USER_PASSWORD_VALIDATE_LENGTH_PROBLEM
    if username == password:
        return False, USER_PASSWORD_VALIDATE_USERNAME_EQUAL_PROBLEM

    from authapp import banned
    if password in banned.BANNED_PASSWORD_LIST:
        return False, USER_PASSWORD_VALIDATE_BANNED_PROBLEM

    return True, VALIDATE_OK


def password_validate(password):
    if not (USER_PASSWORD_MIN_LENGTH <= len(password) <= USER_PASSWORD_MAX_LENGTH):
        return False, USER_PASSWORD_VALIDATE_LENGTH_PROBLEM
    from authapp import banned
    if password in banned.BANNED_PASSWORD_LIST:
        return False, USER_PASSWORD_VALIDATE_BANNED_PROBLEM

    return True, VALIDATE_OK

def render_with_clue_loginform_createform_log_in(request, template, clue_message, log_in_form, create_form):
    from django.shortcuts import render
    if clue_message is not None:
        clue = {'message': clue_message}
        return render(request, template, {'create_form': create_form, 'log_in_form': log_in_form, 'clue_log_in': clue})
    else:
        return render(request, template, {'create_form': create_form, 'log_in_form': log_in_form})


def render_with_clue_loginform_createform(request, template, clue_message, log_in_form, create_form):
    from django.shortcuts import render
    if clue_message is not None:
        clue = {'message': clue_message}
        return render(request, template, {'create_form': create_form, 'log_in_form': log_in_form, 'clue': clue})
    else:
        return render(request, template, {'create_form': create_form, 'log_in_form': log_in_form})


def render_with_clue_one_form(request, template, clue_message, form):
    from django.shortcuts import render
    form = form
    if clue_message is not None:
        clue = {'message': clue_message}
        return render(request, template, {'form': form, 'clue': clue})
    else:
        return render(request, template, {'form': form})


def clue_json_response(clue_success, clue_message):
    from django.http import JsonResponse
    clue = None
    clue['success'] = clue_success
    clue['message'] = clue_message
    return JsonResponse(clue)


def asterisk_total(x):
    def asterisk_part(x):
        text = ''
        for i in range(len(x)):
            if i % 2:
                text = text + '*'
            else:
                text = text + x[i]
        return text

    a = x.split('@')[0]
    b = x.split('@')[1].split('.')[0]
    c = x.split('@')[1].split('.')[-1]
    return asterisk_part(a) + '@' + asterisk_part(b) + '.' + asterisk_part(c)

def get_react_count(post, user):
    return 6

def get_comment_count(post, user):
    return 6

def get_is_reacted(post, user):
    return False

def get_comment_display_user_list(user):
    return []


def get_react_display_user_list(user):
    return []


def get_serialized_post(post_id, user_who_read):
    post = Post.objects.get(uuid=post_id)
    if post is None:
        return None
    user = post.user
    serialized_post = {
        'post_id': post.uuid,
        'post_text': post.text,
        'ping_id': post.ping_id,
        'user': get_serialized_user(user, user_who_read, False),
        'comment_display_user_list': get_comment_display_user_list(user_who_read),
        'comment_count': get_comment_count(post, user_who_read),
        'react_display_user_list': get_react_display_user_list(user_who_read),
        'react_count': get_react_count(post, user_who_read),
        'is_reacted': get_is_reacted(post, user_who_read),
        'created': post.created
    }
    return serialized_post

def get_serialized_comment(comment):
    if comment is None:
        return None
    user = comment.user
    serialized_post = {
        'comment_id': comment.uuid,
        'comment_text': comment.text,
        'user_id': user.username,
        'username': user.userusername.username,
        'user_photo': user.userphoto.file_300_url(),
        'full_name': user.userfullname.full_name,
        'created': comment.created
    }
    return serialized_post


def get_serialized_user(user, user_who_read, follow_update):

    if user is None or user_who_read is None:
        return None

    if follow_update:
        related_follower_list = get_related_follower_list(user, user_who_read)
        related_following_list = get_related_follower_list(user, user_who_read)
    else:
        related_follower_list = []
        related_following_list = []

    serialized = {
        'user_id': user.username,
        'username': user.userusername.username,
        'full_name': user.userfullname.full_name,
        'user_photo': user.userphoto.file_300_url(),
        'follow_update': follow_update,
        'related_follower_list': related_follower_list,
        'related_following_list': related_following_list,
        'is_followed': get_is_followed(user, user_who_read)
    }
    return serialized


def get_related_follower_list(user, user_who_read):

    users = User.objects.filter(fuser__follow=user, ffollow__user=user_who_read).all()
    # 마스터 유저가 팔로우 하는 사람 중 타겟 유저를 팔로우 하는 사람을 보여줌.
    # user_who_read = master user

    result = []
    for item in users:
        result.append(get_serialized_user(item, user_who_read, False))
    return result


def get_related_following_list(user, user_who_read):
    users = User.objects.filter(ffollow__user=user_who_read).filter(ffollow__user=user).all()
    # 마스터 유저가 팔로우 하는 사람 중 타겟 유저도 팔로우 하는 사람을 보여줌.
    # user_who_read = master user
    return []


def get_is_followed(user, user_who_read):

    return Follow.objects.filter(user=user_who_read, follow=user).exists()


def switch_profile_celeb_template_by_lang(lang):
    return {
        'ara': 'celebrity/profile/celeb_profile_ara.html',
        'chi': 'celebrity/profile/celeb_profile_chi.html',
        'eng': 'celebrity/profile/celeb_profile_eng.html',
        'por': 'celebrity/profile/celeb_profile_por.html',
        'spa': 'celebrity/profile/celeb_profile_spa.html',
    }.get(lang, 'celebrity/profile/celeb_profile_eng.html')


def get_serialized_notice(notice, user_who_read):

    user = None
    notice_kind = None
    comment_text = None
    if notice.kind == FOLLOW:
        user = notice.noticefollow.follow.user
        notice_kind = "follow"
        # follow
    elif notice.kind == POST_COMMENT:
        user = notice.noticepostcomment.post_comment.user
        notice_kind = "post_comment"
        comment_text = notice.noticepostcomment.post_comment.text

    elif notice.kind == POST_REACT:
        user = notice.noticepostreact.post_react.user
        notice_kind = "post_react"

    serialized = {
        'user': get_serialized_user(user, user_who_read, False),
        'related_follower_list': get_related_follower_list(user, user_who_read),
        'is_followed': get_is_followed(user, user_who_read),
        'notice_id': notice.uuid,
        'notice_kind': notice.kind,
        'created': notice.created,
        'comment_text': comment_text

    }
    return serialized


def get_post_by_id(post_id):
    try:
        post = Post.objects.get(uuid=post_id)
    except Post.DoesNotExist as e:
        print(e)
        return None
    return post


def get_serialized_comment(item, user_who_read):

    user = item.user

    serialized = {
        'user': get_serialized_user(user, user_who_read, False),
        'related_follower_list': get_related_follower_list(user, user_who_read),
        'is_followed': get_is_followed(user, user_who_read),
        'comment_id': item.uuid,
        'created': item.created,
        'comment_text': item.text

    }
    return serialized


def get_serialized_react(item, user_who_read):

    user = item.user

    serialized = {
        'user': get_serialized_user(user, user_who_read, False),
        'related_follower_list': get_related_follower_list(user, user_who_read),
        'is_followed': get_is_followed(user, user_who_read),
        'created': item.created,
    }
    return serialized


def get_user_by_id(user_id):
    try:
        user = User.objects.get(username=user_id)
    except User.DoesNotExist as e:
        print(e)
        return None
    return user

# HTTP_HEADER_ENCODING = 'iso-8859-1'
# def get_authorization_header(request):
#     """
#     Return request's 'Authorization:' header, as a bytestring.
#     Hide some test client ickyness where the header can be unicode.
#     """
#     HTTP_HEADER_ENCODING = 'iso-8859-1'
#     auth = request.META.get('HTTP_AUTHORIZATION', b'')
#     if isinstance(auth, str):
#         # Work around django test client oddness
#         auth = auth.encode(HTTP_HEADER_ENCODING)
#     return auth
#
#
# class TokenAuthentication(BaseAuthentication):
#     """
#     Simple token based authentication.
#     Clients should authenticate by passing the token key in the "Authorization"
#     HTTP header, prepended with the string "Token ".  For example:
#         Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
#     """
#
#     keyword = 'Token'
#     model = None
#
#     def get_model(self):
#         if self.model is not None:
#             return self.model
#         from authapp.models import UserToken
#         return UserToken
#
#     """
#     A custom token model may be used, but must have the following properties.
#     * key -- The string identifying the token
#     * user -- The user to which the token belongs
#     """
#
#     def authenticate(self, request):
#         auth = get_authorization_header(request).split()
#
#         if not auth or auth[0].lower() != self.keyword.lower().encode():
#             return None
#
#         if len(auth) == 1:
#             msg = _('Invalid token header. No credentials provided.')
#             raise exceptions.AuthenticationFailed(msg)
#         elif len(auth) > 2:
#             msg = _('Invalid token header. Token string should not contain spaces.')
#             raise exceptions.AuthenticationFailed(msg)
#
#         try:
#             token = auth[1].decode()
#         except UnicodeError:
#             msg = _('Invalid token header. Token string should not contain invalid characters.')
#             raise exceptions.AuthenticationFailed(msg)
#
#         return self.authenticate_credentials(token)
#
#     def authenticate_credentials(self, key):
#         model = self.get_model()
#         try:
#             token = model.objects.select_related('user').get(key=key)
#         except model.DoesNotExist:
#             raise exceptions.AuthenticationFailed(_('Invalid token.'))
#
#         if not token.user.is_active:
#             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
#         return (token.user, token)
#
#     def authenticate_header(self, request):
#         return self.keyword

def get_user_token(account=None, password=None):
    user = None
    if '@' in account:
        try:
            user_object = UserPrimaryEmail.objects.get(email=account)
        except UserPrimaryEmail.DoesNotExist:
            return False, AUTH_EMAIL_NOT_EXIST
        user = user_object.user
        # user = User.objects.get(email=username)
        # kwargs = {'email': username}
    else:
        account = account.lower()
        try:
            user_object = UserUsername.objects.get(username=account)
        except UserUsername.DoesNotExist:
            return False, AUTH_USERNAME_NOT_EXIST
        user = user_object.user
        # kwargs = {'username': username}
    if user is not None:

        try:
            # user = User.objects.get(**kwargs)
            if user.check_password(password):
                return True, user
        except User.DoesNotExist:
            return False, AUTH_USER_NOT_EXIST
    else:
        return False, AUTH_USER_NOT_EXIST


def token_authenticate(request):

    HTTP_HEADER_ENCODING = 'iso-8859-1'
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if not isinstance(auth, str):
        return None
        # Work around django test client oddness
    auth = auth.encode(HTTP_HEADER_ENCODING)
    auth = auth.split()
    keyword = 'Token'

    if not auth or auth[0].lower() != keyword.lower().encode():
        return None

    if len(auth) == 1:
        msg = _('Invalid token header. No credentials provided.')
        # raise exceptions.AuthenticationFailed(msg)
        return None
    elif len(auth) > 2:
        msg = _('Invalid token header. Token string should not contain spaces.')
        # raise exceptions.AuthenticationFailed(msg)
        return None

    try:
        token = auth[1].decode()
    except UnicodeError:
        msg = _('Invalid token header. Token string should not contain invalid characters.')
        # raise exceptions.AuthenticationFailed(msg)
        return None

    try:
        user_token = UserToken.objects.get(token=token)
    except UserToken.DoesNotExist:
        return None

    if not user_token.user.is_active:
        # 여기 좀더 세밀한 조정 필요.
        return None
        # raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
    return user_token.user




def send_email(user, user_full_name, user_email, user_primary_email_token):

    subject = '[' + SITE_NAME + ']' + EMAIL_CONFIRMATION_SUBJECT

    message = render_to_string('authapp/_account_activation_email.html', {
        'username': user.username,
        'name': user_full_name.full_name,
        'email': user_email.email,
        'domain': SITE_DOMAIN,
        'site_name': SITE_NAME,
        'uid': user_primary_email_token.uid,
        'token': user_primary_email_token.token,
    })

    new_user_email_list = [user_email.email]

    send_mail(
        subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=new_user_email_list
    )
    return True, EMAIL_SENT


def user_create(full_name, email, password):

    new_user_token = None
    try:
        with transaction.atomic():
            new_user_create = None

            checker_username_result = 0
            counter_username = 0
            while checker_username_result is 0:
                if counter_username <= 9:
                    try:
                        id_number = make_id()
                        new_user_create = User.objects.create_user(
                            username=id_number,
                            password=password,
                            is_active=True,
                        )

                    except IntegrityError as e:
                        if 'UNIQUE constraint' in str(e.args):
                            counter_username = counter_username + 1
                        else:
                            return False, ERROR_UNIQUE_CONSTRAINT_USERNAME
                else:
                    return False, ERROR_OVER_WHILE
                checker_username_result = 1

            new_user_primary_email_create = UserPrimaryEmail.objects.create(
                user=new_user_create,
                email=email,
                is_permitted=False,
            )

            new_user_full_name = UserFullName.objects.create(
                user=new_user_create,
                full_name=full_name
            )

            new_user_photo = UserPhoto.objects.create(
                user=new_user_create,
            )

            new_user_username = UserUsername.objects.create(
                user=new_user_create,
                username=random.choice(USERNAME_PREFIX_LIST) + uuid.uuid4().hex[:24],
            )
            # 여기 기본적인 릴레이션 모델
            new_user_token, created = UserToken.objects.get_or_create(
                user=new_user_create
            )

            new_following_count = FollowingCount.objects.create(user=new_user_create)
            new_follower_count = FollowerCount.objects.create(user=new_user_create)
            new_notice_count = NoticeCount.objects.create(user=new_user_create)

    except Exception as e:
        print(e)
        return False, ERROR_UNEXPECTED

    checker_while_loop = 0
    counter_if_loop = 0
    uid = urlsafe_base64_encode(force_bytes(new_user_create.pk)).decode()
    token = account_activation_token.make_token(new_user_create)
    user_primary_email_token = None
    while checker_while_loop is 0:
        if counter_if_loop <= 9:
            try:
                user_primary_email_token = UserPrimaryEmailAuthToken.objects.create(
                    user_primary_email=new_user_primary_email_create,
                    uid=uid,
                    token=token,
                    email=email,
                )
            except IntegrityError as e:
                if 'UNIQUE constraint' in str(e.args):
                    counter_if_loop = counter_if_loop + 1
                else:
                    return False, ERROR_UNIQUE_CONSTRAINT_MAIL_TOKEN
        checker_while_loop = 1

    # send_email(new_user_create, new_user_full_name, new_user_primary_email_create, user_primary_email_token)

    return True, new_user_create


