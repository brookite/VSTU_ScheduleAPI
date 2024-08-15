from typing import Self
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from api.service_accounts import service_account


class CommonModel(models.Model):
    class Meta:
        abstract = True

    idnumber = models.CharField(null=False, blank=False, max_length=260, verbose_name="Уникальный строковый идентификатор")
    datecreated = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    datemodified = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения записи")
    dateaccessed = models.DateTimeField(null=True, blank=True, verbose_name="Дата доступа к записи")
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    @classmethod
    def last_modified_record(cls) -> Self:
        return cls.objects.order_by('-datemodified').first()


class Subject(CommonModel):
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
    
    name = models.CharField(max_length=256, null=False, blank=False)


class TimeSlot(CommonModel):
    class Meta:
        verbose_name = "Время проведения события"
        verbose_name_plural = "Времена проведения события"

    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("Время проведения не корректно")


class EventPlace(CommonModel):
    class Meta:
        verbose_name = "Место проведения события"
        verbose_name_plural = "Места проведения события"

    building = models.CharField(max_length=128)
    room = models.CharField(max_length=64)


class EventParticipant(CommonModel):
    class Meta:
        verbose_name = "Участник события"
        verbose_name_plural = "Участники события"

    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Преподаватель"
        ASSISTANT = "assistant", "Ассистент"

    name = models.CharField(max_length=255)
    role = models.CharField(choices=Role, max_length=48, null=False)


class Event(CommonModel):
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    class Kind(models.TextChoices):
        LECTURE = "LEC", "Лекционное занятие"
        LABWORK = "LAB", "Лабораторная работа"
        PRACTICE = "PRA", "Практическое занятие"
        ON_MANUFACTURE = "MAN", "На производстве"

    kind = models.CharField(max_length=3, choices=Kind, null=False, blank=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    participants = models.ManyToManyField(EventParticipant)


class EventHolding(CommonModel):
    class Meta:
        verbose_name = "Информация о проведении события"
        verbose_name_plural = verbose_name

    place = models.ForeignKey(EventPlace, null=True, on_delete=models.SET_NULL)
    date = models.DateField(blank=False)
    slot = models.ForeignKey(TimeSlot, null=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)


class Schedule(CommonModel):
    class Scope(models.TextChoices):
        BACHELOR = "BACHELOR", "Бакалавриат"
        MASTER = "MASTER", "Магистрант"
        POSTGRADUATE = "POSTGRADUATE", "Аспирантура"
        CONSULTATION = "CONSULTATION", "Консультация"
    
    faculty = models.CharField(max_length=32)
    scope = models.CharField(choices=Scope, max_length=32)
    # TODO: Возможно сделать такой формат названия (проверка правильности по regex): ФЭВТ,2024-2025,бак,2курс,1с
    name = models.CharField(max_length=128, verbose_name="Название расписания")
    events = models.ManyToManyField(Event)