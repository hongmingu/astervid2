# Generated by Django 2.0.10 on 2019-10-26 06:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('object', '0003_auto_20191026_1506'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='post_text',
            new_name='text',
        ),
    ]
