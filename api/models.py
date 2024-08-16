from typing import Self
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CommonModel(models.Model):
    class Meta:
        abstract = True

    idnumber = models.CharField(null=False, blank=False, max_length=260, verbose_name="Уникальный строковый идентификатор")
    datecreated = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    datemodified = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения записи")
    dateaccessed = models.DateTimeField(null=True, blank=True, verbose_name="Дата доступа к записи")
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    note = models.TextField(null=True, blank=True, verbose_name="Комментарий для этой записи", max_length=1024)

    @classmethod
    def last_modified_record(cls) -> Self:
        return cls.objects.order_by('-datemodified').first()


class Subject(CommonModel):
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
    
    name = models.CharField(max_length=256)


class TimeSlot(CommonModel):
    class Meta:
        verbose_name = "Время проведения события"
        verbose_name_plural = "Времена проведения события"

    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(null=True, verbose_name="Время окончания")

    def clean(self):
        if self.end_time and self.end_time <= self.start_time:
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


class EventKind(CommonModel):
    class Meta:
        verbose_name = "Тип события"
        verbose_name_plural = "Типы событий"

    name = models.CharField(verbose_name="Название типа", max_length=64)


class Event(CommonModel):
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    kind = models.ForeignKey(EventKind, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    participants = models.ManyToManyField(EventParticipant)


class EventHolding(CommonModel):
    class Meta:
        verbose_name = "Информация о проведении события"
        verbose_name_plural = verbose_name

    place = models.ForeignKey(EventPlace, null=True, on_delete=models.PROTECT)
    date = models.DateField(blank=False)
    slot = models.ForeignKey(TimeSlot, null=True, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)


class Schedule(CommonModel):
    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    class Scope(models.TextChoices):
        BACHELOR = "bachelor", "Бакалавриат"
        MASTER = "master", "Магистратура"
        POSTGRADUATE = "postgraduate", "Аспирантура"
        CONSULTATION = "consultation", "Консультация"
    
    faculty = models.CharField(max_length=32, verbose_name="Факультет")
    scope = models.CharField(choices=Scope, max_length=32, verbose_name="Обучение")
    course = models.IntegerField(verbose_name="Курс")
    semester = models.IntegerField(verbose_name="Семестр")
    course_start = models.DateField(verbose_name="Начало учебного года")
    course_finish = models.DateField(verbose_name="Окончание учебного года")
    events = models.ManyToManyField(Event, verbose_name="Занятия")