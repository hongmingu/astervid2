# Generated by Django 2.0.10 on 2019-11-01 12:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0002_auto_20191031_2118'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userfirebaseinstanceid',
            old_name='uuid',
            new_name='instance_id',
        ),
    ]