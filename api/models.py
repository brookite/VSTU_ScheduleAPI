from typing import Optional, Self

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class CommonModel(models.Model):
    class Meta:
        abstract = True

    idnumber = models.CharField(
        unique=True,
        blank=True,
        null=True,
        max_length=260,
        verbose_name="Уникальный строковый идентификатор",
    )
    datecreated = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    datemodified = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения записи")
    dateaccessed = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата доступа к записи"
    )
    author = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Автор записи"
    )
    note = models.TextField(
        null=True, blank=True, verbose_name="Комментарий для этой записи", max_length=1024
    )

    @classmethod
    def last_modified_record(cls) -> Optional[Self]:
        return cls.objects.order_by("-datemodified").first()

    def __str__(self):
        return self.__repr__()


class Subject(CommonModel):
    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    name = models.CharField(max_length=256, verbose_name="Название")

    def __repr__(self):
        return "{} [{}]".format(str(self.name), self.pk)


class TimeSlot(CommonModel):
    class Meta:
        verbose_name = "Время проведения события"
        verbose_name_plural = "Времена проведения события"

    alt_name = models.TextField(null=True, verbose_name="Академ. часы пары")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(null=True, verbose_name="Время окончания")

    def clean(self):
        if self.end_time and self.end_time <= self.start_time:
            raise ValidationError("Время проведения не корректно")

    def __repr__(self):
        res = self.start_time.strftime("%H:%M")
        if self.end_time:
            res += "- {}".format(self.end_time.strftime("%H:%M"))
        return res


class EventPlace(CommonModel):
    class Meta:
        verbose_name = "Место проведения события"
        verbose_name_plural = "Места проведения события"

    building = models.CharField(max_length=128, verbose_name="Корпус")
    room = models.CharField(max_length=64, verbose_name="Аудитория")

    def __repr__(self):
        return str(self.room)


class EventKind(CommonModel):
    class Meta:
        verbose_name = "Тип события"
        verbose_name_plural = "Типы событий"

    name = models.CharField(verbose_name="Название типа", max_length=64)

    def __repr__(self):
        return "{} [{}]".format(str(self.name), self.pk)


class AbstractDay(CommonModel):
    class Meta:
        verbose_name = "Абстрактный день"
        verbose_name_plural = "Абстрактные дни"

    day_number = models.IntegerField(verbose_name="Смещение от начала повторяющгося фрагмента (пн. первой недели)")
    name = models.CharField(verbose_name="Имя дня в рамках шаблона", max_length=64)


class Organization(CommonModel):
    class Meta:
        verbose_name = "Учреждение"
        verbose_name_plural = "Учреждения"

    name = models.CharField(verbose_name="Имя учреждения", max_length=64)


class Department(CommonModel):
    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    name = models.CharField(verbose_name="Имя подразделения", max_length=64)
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родительское подразделение"
        )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Учреждение")


class AbstractSchedule(CommonModel):
    class Meta:
        verbose_name = "Абстрактное расписание"
        verbose_name_plural = "Абстрактные расписания"

    repetition_period = models.IntegerField(verbose_name="Период повторения")
    repeatable = models.BooleanField(verbose_name="Повторяется ли")
    aligned_by_week_day = models.IntegerField(verbose_name="Выравнивание относительно дня недели (null=0, пн=1, ...)")
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, verbose_name="Подразделение")


class Schedule(CommonModel):
    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    class Scope(models.TextChoices):
        BACHELOR = "bachelor", "Бакалавриат"
        MASTER = "master", "Магистратура"
        POSTGRADUATE = "postgraduate", "Аспирантура"
        CONSULTATION = "consultation", "Консультация"

    class Status(models.IntegerChoices):
        ACTIVE = 0, "Активно"
        DISABLED = 1, "Отключено"
        FUTURE = 2, "Будущее"
        ARCHIVE = 3, "Архивное"

    status = models.IntegerField(choices=Status, default=0, verbose_name="Текущий статус")
    faculty = models.CharField(max_length=32, verbose_name="Факультет")
    scope = models.CharField(choices=Scope, max_length=32, verbose_name="Обучение")
    course = models.IntegerField(verbose_name="Курс")
    semester = models.IntegerField(verbose_name="Семестр")
    years = models.CharField(max_length=16, verbose_name="Учебный год")
    start_date = models.DateField(null=True, verbose_name="День начала семестра (вкл.)")
    end_date = models.DateField(null=True, verbose_name="День окончания семестра (вкл.)")
    starting_day_number = models.ForeignKey(AbstractDay, null=True, on_delete=models.PROTECT, verbose_name="Номер дня начала (двухнедельного) цикла")
    abstract_schedule = models.ForeignKey(AbstractSchedule, null=True, on_delete=models.PROTECT, verbose_name="Абстрактное расписание")

    def first_event(self):
        events = self.events.all()

        return events.annotate(min_date=models.Min("holdings__date")).order_by("min_date").first()

    def last_event(self):
        events = self.events.all()

        return events.annotate(max_date=models.Max("holdings__date")).order_by("-max_date").first()

    def __repr__(self):
        return f"{self.faculty},{self.years},{self.scope},{self.course}к,{self.semester}сем"


class EventParticipant(CommonModel):
    class Meta:
        verbose_name = "Участник события"
        verbose_name_plural = "Участники события"

    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Преподаватель"
        ASSISTANT = "assistant", "Ассистент"

    name = models.CharField(max_length=255, verbose_name="Имя")
    role = models.CharField(choices=Role, max_length=48, null=False, verbose_name="Роль")
    is_group = models.BooleanField(verbose_name="Является группой", default=False)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, verbose_name="Подразделение")

    def __repr__(self):
        return f"{self.name} ({self.role})"


class AbstractEvent(CommonModel):
    class Meta:
        verbose_name = "Абстрактное событие"
        verbose_name_plural = "Абстрактные события"

    kind = models.ForeignKey(EventKind, on_delete=models.PROTECT, verbose_name="Тип")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name="Предмет")
    participants = models.ManyToManyField(EventParticipant, verbose_name="Участники")
    place = models.ForeignKey(EventPlace, on_delete=models.PROTECT, verbose_name="Место")
    abstract_day = models.ForeignKey(AbstractDay, on_delete=models.PROTECT, verbose_name="Абстрактный день")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, verbose_name="Временной интервал")


class Event(CommonModel):
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    date = models.DateField(null=True, blank=False, verbose_name="Дата")
    kind_override = models.ForeignKey(EventKind, null=True, on_delete=models.PROTECT, verbose_name="Тип")
    subject_override = models.ForeignKey(Subject, null=True, on_delete=models.PROTECT, verbose_name="Предмет")
    participants_override = models.ManyToManyField(EventParticipant, verbose_name="Участники")
    place_override = models.ForeignKey(EventPlace, null=True, on_delete=models.PROTECT, verbose_name="Место")
    time_slot_override = models.ForeignKey(TimeSlot, null=True, on_delete=models.PROTECT, verbose_name="Временной интервал")
    abstract_event = models.ForeignKey(AbstractEvent, null=True, on_delete=models.PROTECT, verbose_name="Абстрактное событие")
    schedule = models.ForeignKey(
        Schedule,
        related_name="events",
        verbose_name="Расписание",
        on_delete=models.CASCADE
    )

    def __repr__(self):
        return f"Занятие по {self.abstract_event.subject.name} [{self.pk}]"