# Generated by Django 2.0.10 on 2019-10-26 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object', '0002_auto_20190930_1716'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posttext',
            name='post',
        ),
        migrations.AddField(
            model_name='post',
            name='comment_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='ping_text',
            field=models.TextField(default=None, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='post_text',
            field=models.TextField(default=None, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='react_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='PostText',
        ),
    ]
