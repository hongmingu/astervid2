# Generated by Django 2.0.10 on 2019-11-28 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('object', '0005_auto_20191101_2157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='ping_id',
            field=models.CharField(default=None, max_length=34, null=True),
        ),
    ]
