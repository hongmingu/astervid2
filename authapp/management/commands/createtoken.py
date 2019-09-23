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

from authapp.models import UserPhoto, UserFullName, UserUsername, UserPrimaryEmail, UserToken
from authapp.utils import make_id
from notice.models import NoticeCount
from relation.models import FollowerCount, FollowingCount

class Command(BaseCommand):
    help = 'Create Super User Custom'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            user_token = UserToken.objects.get_or_create(user=user)

