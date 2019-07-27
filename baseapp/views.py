from django.shortcuts import render, redirect, reverse
from relation.models import *
from object.models import *
from object.numbers import *
from notice.models import *
from django.db.models import Q
from django.db import transaction
import uuid

from django.utils.timezone import now, timedelta

# Create your views here.


def b_admin(request):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin.html')

        return render(request, '404.html', )


def b_admin_solo(request):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin_solo.html')

        return render(request, '404.html', )


def b_admin_group(request):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin_group.html')

        return render(request, '404.html', )

def b_admin_group_edit(request, uuid):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin_group_edit.html', {'id': uuid})

        return render(request, '404.html', )


def b_admin_solo_edit(request, uuid):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin_solo_edit.html', {'id': uuid})

        return render(request, '404.html', )


def b_admin_member(request):
    if request.method == "GET":
        if request.user.is_superuser:
            return render(request, 'baseapp/b_admin_member.html')

        return render(request, '404.html', )


from django.urls import reverse
from django.shortcuts import render
from paypal.standard.forms import PayPalPaymentsForm

from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt


def pay_charge(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            q = request.GET.get('q', None)
            if not q.isdigit():
                return render(request, '404.html')
            business = settings.BUSINESS
            # What you want the button to do.
            user_id = request.user.username # 이거 데이터베이스에서 중복값 없도록 해야 한다. 여기 수정해야함.
            paypal_dict = {
                "business": business, # 판매자 계정 잘 써야 한다.
                "amount": int(q),
                "item_name": "galaboard charge",
                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                "return": request.build_absolute_uri(reverse('baseapp:pay_return')),
                "cancel_return": request.build_absolute_uri(reverse('baseapp:pay_cancel_return')),
                "custom": request.user.username,  # Custom command to correlate to some function later (optional)
            }
            # Create the instance.
            form = PayPalPaymentsForm(initial=paypal_dict)
            context = {"form": form, 'charge': q}
            return render(request, "baseapp/pay_charge.html", context)
# 여기서 paypal - profile - my selling tools - Instant payment notifications


@csrf_exempt
def pay_return(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, "baseapp/pay_return.html")


@csrf_exempt
def pay_cancel_return(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, "baseapp/pay_cancel_return.html")


@csrf_exempt
def pay_start(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            from django.utils import timezone
            print(timezone.now())

            return render(request, "baseapp/pay_start.html")


def create_new(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))
        return render(request, 'baseapp/create_new.html')


def create_solo_post(request, uuid):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))
        return render(request, 'baseapp/create_obj_post.html', {'id': uuid, 'obj_type': 'solo'})


def create_group_post(request, uuid):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))
        return render(request, 'baseapp/create_obj_post.html', {'id': uuid, 'obj_type': 'group'})


def update_solo_post(request, uuid):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))

        try:
            post = Post.objects.get(uuid=uuid, user=request.user)
        except Exception as e:
            return redirect(reverse('baseapp:main_create_log_in'))

        return render(request, 'baseapp/update_obj_post.html', {'id': uuid, 'obj_type': 'solo'})


def update_group_post(request, uuid):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(reverse('baseapp:main_create_log_in'))

        try:
            post = Post.objects.get(uuid=uuid, user=request.user)
        except Exception as e:
            return redirect(reverse('baseapp:main_create_log_in'))

        return render(request, 'baseapp/update_obj_post.html', {'id': uuid, 'obj_type': 'group'})


def user_profile(request, user_username):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = None
            try:
                chosen_user = User.objects.get(userusername__username=user_username)
            except:
                return render(request, '404.html')
            if chosen_user is not None:
                following = None
                if Follow.objects.filter(user=request.user, follow=chosen_user).exists():
                    following = True

                return render(request, 'baseapp/user_profile.html', {'chosen_user': chosen_user, 'following': following})
        else:
            user = None
            try:
                chosen_user = User.objects.get(userusername__username=user_username)
            except:
                return render(request, '404.html')
            if chosen_user is not None:
                following = None
                return render(request, 'baseapp/user_profile.html',
                              {'chosen_user': chosen_user, 'following': following})


def solo_profile(request, uuid):
    if request.method == "GET":
        if request.user.is_authenticated:
            solo = None
            try:
                solo = Solo.objects.get(uuid=uuid)
            except Exception as e:
                return render(request, '404.html')
            if solo is not None:
                following = None
                if SoloFollow.objects.filter(user=request.user, solo=solo).exists():
                    following = True

                return render(request, 'baseapp/solo_profile.html',
                              {'solo': solo, 'following': following})
        else:
            solo = None
            try:
                solo = Solo.objects.get(uuid=uuid)
            except Exception as e:
                return render(request, '404.html')
            if solo is not None:
                following = None
                return render(request, 'baseapp/solo_profile.html',
                              {'solo': solo, 'following': following})


def group_profile(request, uuid):
    if request.method == "GET":
        if request.user.is_authenticated:
            group = None
            try:
                group = Group.objects.get(uuid=uuid)
            except Exception as e:
                return render(request, '404.html')
            if group is not None:
                following = None
                if GroupFollow.objects.filter(user=request.user, group=group).exists():
                    following = True

                return render(request, 'baseapp/group_profile.html',
                              {'group': group, 'following': following})
        else:
            group = None
            try:
                group = Group.objects.get(uuid=uuid)
            except Exception as e:
                return render(request, '404.html')
            if group is not None:
                following = None
                return render(request, 'baseapp/group_profile.html',
                              {'group': group, 'following': following})


def solo_posts(request, uuid):
    if request.method == "GET":
        solo = None
        try:
            solo = Solo.objects.get(uuid=uuid)
        except Exception as e:
            return render(request, '404.html')
        if solo is not None:
            return render(request, 'baseapp/obj_posts.html',
                          {'obj': solo, 'obj_type': 'solo', 'id': uuid})


def group_posts(request, uuid):
    if request.method == "GET":
        group = None
        try:
            group = Group.objects.get(uuid=uuid)
        except Exception as e:
            return render(request, '404.html')
        if group is not None:
            return render(request, 'baseapp/obj_posts.html',
                          {'obj': group, 'obj_type': 'group', 'id': uuid})


def home(request):
    if request.method == "GET":

        from django.utils.timezone import localdate
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta

        d = request.GET.get('d', None)
        if d is None:
            if not request.get_full_path() == '/':
                return redirect(reverse('baseapp:home'))

            today_str = str(localdate())
            today_obj = datetime(int(today_str.split('-')[0]),
                                 int(today_str.split('-')[1]),
                                 int(today_str.split('-')[2]))

            yesterday_obj = today_obj - timedelta(days=1)
            yesterday_str = str(yesterday_obj).split(' ')[0]

            return render(request, 'baseapp/home.html', {'day': today_str,
                                                         'yesterday': yesterday_str,
                                                         'today': today_str,
                                                         'tomorrow': ''})
        else:
            date = parse_date(d)
            if date is None:
                return redirect(reverse('baseapp:home'))
            else:
                today_str = str(localdate())
                day_str = str(date)
                if today_str == day_str:
                    return redirect(reverse('baseapp:home'))

                # first_post_created = Post.objects.first().created
                # origin_str = str(first_post_created).split(' ')[0]
                origin_str = '2018-11-10'

                date_1 = None
                date_2 = None
                date_3 = None

                try:
                    date_1 = datetime.strptime(origin_str, '%Y-%m-%d')
                    date_2 = datetime.strptime(day_str, '%Y-%m-%d')
                    date_3 = datetime.strptime(today_str, '%Y-%m-%d')
                except Exception as e:
                    return redirect(reverse('baseapp:home'))

                if not date_1 <= date_2 <= date_3:
                    return redirect(reverse('baseapp:home'))

                day_obj = datetime(int(day_str.split('-')[0]),
                                   int(day_str.split('-')[1]),
                                   int(day_str.split('-')[2]))

                yesterday_obj = day_obj - timedelta(days=1)
                yesterday_str = str(yesterday_obj).split(' ')[0]

                tomorrow_obj = day_obj + timedelta(days=1)
                tomorrow_str = str(tomorrow_obj).split(' ')[0]

                return render(request, 'baseapp/home.html', {'day': day_str,
                                                             'yesterday': yesterday_str,
                                                             'today': today_str,
                                                             'tomorrow': tomorrow_str})


def solo_home(request):
    if request.method == "GET":

        from django.utils.timezone import localdate
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta


        d = request.GET.get('d', None)
        # print(request.get_full_path())
        if d is None:
            if not request.get_full_path() == '/solo/':
                return redirect(reverse('baseapp:solo_home'))

            today_str = str(localdate())
            today_obj = datetime(int(today_str.split('-')[0]),
                                 int(today_str.split('-')[1]),
                                 int(today_str.split('-')[2]))

            yesterday_obj = today_obj - timedelta(days=1)
            yesterday_str = str(yesterday_obj).split(' ')[0]

            return render(request, 'baseapp/solo_home.html', {'day': today_str,
                                                         'yesterday': yesterday_str,
                                                         'today': today_str,
                                                         'tomorrow': ''})
        else:
            date = parse_date(d)
            if date is None:
                return redirect(reverse('baseapp:solo_home'))
            else:
                today_str = str(localdate())
                day_str = str(date)
                if today_str == day_str:
                    return redirect(reverse('baseapp:solo_home'))

                # first_post_created = Post.objects.first().created
                # origin_str = str(first_post_created).split(' ')[0]
                origin_str = '2018-11-10'

                date_1 = None
                date_2 = None
                date_3 = None

                try:
                    date_1 = datetime.strptime(origin_str, '%Y-%m-%d')
                    date_2 = datetime.strptime(day_str, '%Y-%m-%d')
                    date_3 = datetime.strptime(today_str, '%Y-%m-%d')
                except Exception as e:
                    return redirect(reverse('baseapp:solo_home'))

                if not date_1 <= date_2 <= date_3:
                    return redirect(reverse('baseapp:solo_home'))

                day_obj = datetime(int(day_str.split('-')[0]),
                                   int(day_str.split('-')[1]),
                                   int(day_str.split('-')[2]))

                yesterday_obj = day_obj - timedelta(days=1)
                yesterday_str = str(yesterday_obj).split(' ')[0]

                tomorrow_obj = day_obj + timedelta(days=1)
                tomorrow_str = str(tomorrow_obj).split(' ')[0]

                return render(request, 'baseapp/solo_home.html', {'day': day_str,
                                                             'yesterday': yesterday_str,
                                                             'today': today_str,
                                                             'tomorrow': tomorrow_str})




def group_home(request):
    if request.method == "GET":

        from django.utils.timezone import localdate
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta


        d = request.GET.get('d', None)
        # print(request.get_full_path())
        if d is None:
            if not request.get_full_path() == '/group/':
                return redirect(reverse('baseapp:group_home'))

            today_str = str(localdate())
            today_obj = datetime(int(today_str.split('-')[0]),
                                 int(today_str.split('-')[1]),
                                 int(today_str.split('-')[2]))

            yesterday_obj = today_obj - timedelta(days=1)
            yesterday_str = str(yesterday_obj).split(' ')[0]

            return render(request, 'baseapp/group_home.html', {'day': today_str,
                                                         'yesterday': yesterday_str,
                                                         'today': today_str,
                                                         'tomorrow': ''})
        else:
            date = parse_date(d)
            if date is None:
                return redirect(reverse('baseapp:group_home'))
            else:
                today_str = str(localdate())
                day_str = str(date)
                if today_str == day_str:
                    return redirect(reverse('baseapp:group_home'))

                # first_post_created = Post.objects.first().created
                # origin_str = str(first_post_created).split(' ')[0]
                origin_str = '2018-11-10'

                date_1 = None
                date_2 = None
                date_3 = None

                try:
                    date_1 = datetime.strptime(origin_str, '%Y-%m-%d')
                    date_2 = datetime.strptime(day_str, '%Y-%m-%d')
                    date_3 = datetime.strptime(today_str, '%Y-%m-%d')
                except Exception as e:
                    return redirect(reverse('baseapp:group_home'))

                if not date_1 <= date_2 <= date_3:
                    return redirect(reverse('baseapp:group_home'))

                day_obj = datetime(int(day_str.split('-')[0]),
                                   int(day_str.split('-')[1]),
                                   int(day_str.split('-')[2]))

                yesterday_obj = day_obj - timedelta(days=1)
                yesterday_str = str(yesterday_obj).split(' ')[0]

                tomorrow_obj = day_obj + timedelta(days=1)
                tomorrow_str = str(tomorrow_obj).split(' ')[0]

                return render(request, 'baseapp/group_home.html', {'day': day_str,
                                                             'yesterday': yesterday_str,
                                                             'today': today_str,
                                                             'tomorrow': tomorrow_str})



def all_home(request):
    if request.method == "GET":

        from django.utils.timezone import localdate
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta


        d = request.GET.get('d', None)
        print(request.get_full_path())
        if d is None:
            if not request.get_full_path() == '/all/':
                return redirect(reverse('baseapp:all_home'))

            today_str = str(localdate())
            today_obj = datetime(int(today_str.split('-')[0]),
                                 int(today_str.split('-')[1]),
                                 int(today_str.split('-')[2]))

            yesterday_obj = today_obj - timedelta(days=1)
            yesterday_str = str(yesterday_obj).split(' ')[0]

            return render(request, 'baseapp/all_home.html', {'day': today_str,
                                                         'yesterday': yesterday_str,
                                                         'today': today_str,
                                                         'tomorrow': ''})
        else:
            date = parse_date(d)
            if date is None:
                return redirect(reverse('baseapp:all_home'))
            else:
                today_str = str(localdate())
                day_str = str(date)
                if today_str == day_str:
                    return redirect(reverse('baseapp:all_home'))

                # first_post_created = Post.objects.first().created
                # origin_str = str(first_post_created).split(' ')[0]
                origin_str = '2018-11-10'

                date_1 = None
                date_2 = None
                date_3 = None

                try:
                    date_1 = datetime.strptime(origin_str, '%Y-%m-%d')
                    date_2 = datetime.strptime(day_str, '%Y-%m-%d')
                    date_3 = datetime.strptime(today_str, '%Y-%m-%d')
                except Exception as e:
                    return redirect(reverse('baseapp:all_home'))

                if not date_1 <= date_2 <= date_3:
                    return redirect(reverse('baseapp:all_home'))

                day_obj = datetime(int(day_str.split('-')[0]),
                                   int(day_str.split('-')[1]),
                                   int(day_str.split('-')[2]))

                yesterday_obj = day_obj - timedelta(days=1)
                yesterday_str = str(yesterday_obj).split(' ')[0]

                tomorrow_obj = day_obj + timedelta(days=1)
                tomorrow_str = str(tomorrow_obj).split(' ')[0]

                return render(request, 'baseapp/all_home.html', {'day': day_str,
                                                             'yesterday': yesterday_str,
                                                             'today': today_str,
                                                             'tomorrow': tomorrow_str})


def post(request, uuid):
    if request.method == "GET":
        post = None
        try:
            post = Post.objects.get(uuid=uuid)
        except Exception as e:
            return render(request, '404.html')
        if post is not None:
            if str(post).startswith('solo'):
                obj_type = 'solo'
            else:
                obj_type = 'group'
            return render(request, 'baseapp/post.html', {'id': uuid, 'post': post, 'obj_type': obj_type})

        return render(request, 'baseapp/post.html', )



def search_all(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        q = q.strip()
        word = q
        return render(request, 'baseapp/search_all.html', {'word': word})

def search_user(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        q = q.strip()
        word = q
        return render(request, 'baseapp/search_user.html', {'word': word})

def search_solo(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        q = q.strip()
        word = q
        return render(request, 'baseapp/search_solo.html', {'word': word})

def search_group(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        q = q.strip()
        word = q
        return render(request, 'baseapp/search_group.html', {'word': word})

def search_post(request):
    if request.method == "GET":
        q = request.GET.get('q', None)
        if q is None:
            q = ''
        q = q.strip()
        word = q
        return render(request, 'baseapp/search_post.html', {'word': word})


def note_all(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                with transaction.atomic():
                    notices_update = Notice.objects.filter(Q(user=request.user) & Q(checked=False)).update(
                        checked=True)
                    notice_count = request.user.noticecount
                    notice_count.count = 0
                    notice_count.save()
            except Exception as e:
                print(e)
                pass
            return render(request, 'baseapp/note_all.html')
        else:
            return redirect(reverse('baseapp:main_create_log_in'))


def follow_feed(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, 'baseapp/follow_feed.html')
        else:
            return redirect(reverse('baseapp:main_create_log_in'))


def log_charge(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, 'baseapp/log.html', {'log_type': 'charge'})
        else:
            return redirect(reverse('baseapp:main_create_log_in'))


def log_pay(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, 'baseapp/log.html', {'log_type': 'pay'})
        else:
            return redirect(reverse('baseapp:main_create_log_in'))
