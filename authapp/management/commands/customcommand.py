"""
Management utility to create superusers.
"""
import getpass
import sys
import uuid

import random
from django.contrib.auth import get_user_model
from django.contrib.auth.management import get_default_username
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, IntegrityError, transaction
from django.utils.text import capfirst

from authapp.models import UserPhoto, UserFullName, UserUsername, UserPrimaryEmail
from authapp.utils import make_id
from notice.models import NoticeCount
from relation.models import FollowerCount, FollowingCount

class Command(BaseCommand):
    help = 'Create Super User Custom'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs=None, type=str)
        parser.add_argument('password', nargs=None, type=str)


    def handle(self, *args, **options):
        new_name = "master"
        new_username = options['username']
        new_password = options['username']
        new_email = options['username'] + "@" + options['username'] + ".com"
        new_username = new_username.lower()

        try:
            with transaction.atomic():
                checker_username_result = 0
                counter_username = 0
                while checker_username_result is 0:
                    if counter_username <= 9:
                        try:
                            id_number = make_id()
                            new_user_create = User.objects.create_superuser(
                                username=id_number,
                                password=new_password,
                                email="",
                                is_active=True,
                                is_superuser=True,
                            )

                        except IntegrityError as e:
                            if 'UNIQUE constraint' in str(e.args):
                                counter_username = counter_username + 1
                            else:
                                return
                    else:
                        return
                    checker_username_result = 1

                new_user_primary_email_create = UserPrimaryEmail.objects.create(
                    user=new_user_create,
                    email=new_email,
                    is_permitted=False,
                )

                new_user_username = UserUsername.objects.create(
                    user=new_user_create,
                    username=new_username,
                )
                new_user_text_name = UserFullName.objects.create(
                    user=new_user_create,
                    full_name=new_name
                )
                new_user_photo = UserPhoto.objects.create(
                    user=new_user_create,
                )

                #
                # birthday = str(1991) + '-' + str(2) + '-' + str(26)
                #
                # new_user_birthday = UserBirthday.objects.create(
                #     user=new_user_create,
                #     birthday=birthday
                # )
                # new_user_gender = UserGender.objects.create(
                #     user=new_user_create,
                #     gender=1
                # )

                # 여기 기본적인 릴레이션 모델
                new_following_count = FollowingCount.objects.create(user=new_user_create)
                new_follower_count = FollowerCount.objects.create(user=new_user_create)
                new_notice_count = NoticeCount.objects.create(user=new_user_create)



        except Exception as e:
            print(e)
            self.stdout.write(self.style.SUCCESS('Failed'))
            return

        self.stdout.write(self.style.SUCCESS('Successfully created'))
        self.stdout.write(new_user_create.username + " " + new_user_create.password + " " + new_user_username.username + " " + new_user_primary_email_create.email)
