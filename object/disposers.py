
import uuid
import os


def get_file_path_solo_celeb_photo_50(instance, filename):
    ext = filename.split('.')[-1]
    id = instance.solo.uuid
    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "50_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/solo/%s' % id, filename)


def get_file_path_solo_celeb_photo_300(instance, filename):
    ext = filename.split('.')[-1]
    id = instance.solo.uuid
    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "300_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/solo/%s' % id, filename)


def get_file_path_group_celeb_photo_50(instance, filename):
    ext = filename.split('.')[-1]
    id = instance.group.uuid
    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "50_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/group/%s' % id, filename)


def get_file_path_group_celeb_photo_300(instance, filename):
    ext = filename.split('.')[-1]
    id = instance.group.uuid
    from django.utils.timezone import now
    now = now()
    now_date = now.strftime('%Y-%m-%d-%H-%M-%S')
    filename = "300_%s_%s.%s" % (now_date, uuid.uuid4(), ext)

    return os.path.join('photo/group/%s' % id, filename)