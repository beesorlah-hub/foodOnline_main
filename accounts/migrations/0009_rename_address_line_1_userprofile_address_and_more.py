# Generated by Django 5.0.6 on 2024-06-25 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_rename_longitude_userprofile_longtitude'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='address_line_1',
            new_name='address',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='address_line_2',
        ),
    ]
