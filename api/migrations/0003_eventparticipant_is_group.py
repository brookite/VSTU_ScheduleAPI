# Generated by Django 5.1 on 2024-10-25 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_event_author_alter_event_idnumber_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventparticipant',
            name='is_group',
            field=models.BooleanField(default=False, verbose_name='Является группой'),
        ),
    ]
