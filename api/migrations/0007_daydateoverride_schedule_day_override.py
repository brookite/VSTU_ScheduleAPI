# Generated by Django 5.2.dev20241016095222 on 2025-02-21 08:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_event_participants_override'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DayDateOverride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idnumber', models.CharField(blank=True, max_length=260, null=True, unique=True, verbose_name='Уникальный строковый идентификатор')),
                ('datecreated', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('datemodified', models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения записи')),
                ('dateaccessed', models.DateTimeField(blank=True, null=True, verbose_name='Дата доступа к записи')),
                ('note', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Комментарий для этой записи')),
                ('day_source', models.DateField(verbose_name='Перенести дату из')),
                ('day_destination', models.DateField(verbose_name='Перенести дату в')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Автор записи')),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.organization', verbose_name='Организация')),
            ],
            options={
                'verbose_name': 'Перенос дня на другую дату',
                'verbose_name_plural': 'Переносы дней на другие даты',
            },
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_override',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.daydateoverride', verbose_name='Перенос дня'),
        ),
    ]
