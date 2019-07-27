import time
import datetime
import random
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import BaseAuthentication

from authapp.models import UserToken

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


def user_username_failure_validate(username):
    import re
    if not (re.match('^([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)$', username)):
        return 1
    if not (4 <= len(username) <= 30):
        return 2
    if (8 <= len(username)) and username.isdigit():
        return 3

    # banned username and password
    from authapp import banned
    match_ban = [name for name in banned.BANNED_USERNAME_LIST if name in username]
    if match_ban:
        return 4

    # succeed username validation
    return 0


def user_text_name_failure_validate(user_text_name):
    if not (1 <= len(user_text_name) <= 30):
        return 1
    if '/' in user_text_name:
        return 1
    if '<' in user_text_name:
        return 1
    if '$' in user_text_name:
        return 1
    return 0


def user_primary_email_failure_validate(email):
    import re
    if not (re.match('[^@]+@[^@]+\.[^@]+', email)):
        return 1
    if len(email) > 255:
        return 2

    return 0


def password_failure_validate(username, password, password_confirm):
    if not password == password_confirm:
        return 1
    if not (6 <= len(password) <= 128):
        return 2
    if username == password:
        return 3

    from authapp import banned
    if password in banned.BANNED_PASSWORD_LIST:
        return 4

    return 0


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


def token_authenticate(request):
    HTTP_HEADER_ENCODING = 'iso-8859-1'
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if not isinstance(auth, str):
        return
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
    return (user_token.user, token)

