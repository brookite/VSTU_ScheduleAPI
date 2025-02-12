from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.utils import timezone

from api.models import (
    AbstractEvent,
    AbstractDay,
    AbstractSchedule,
    Department,
    Organization,
    Event,
    EventKind,
    EventParticipant,
    EventPlace,
    Schedule,
    Subject,
    TimeSlot,
)

from rest_framework.authtoken.admin import TokenAdmin


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ("dateaccessed", "datemodified", "datecreated")

    def save_model(self, request, obj, form, change):
        if not obj.id:  # Если это новая запись
            obj.datecreated = timezone.now()
        obj.datemodified = timezone.now()
        obj.save()


@admin.register(Subject)
class SubjectAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(EventParticipant)
class EventParticipantAdmin(BaseAdmin):
    list_display = ("name", "role")
    search_fields = ("name", "role")
    list_filter = ("role",)


@admin.register(EventPlace)
class EventPlaceAdmin(BaseAdmin):
    list_display = ("building", "room")
    search_fields = ("building", "room")
    list_filter = ("building",)


@admin.register(EventKind)
class EventKindAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Schedule)
class ScheduleAdmin(BaseAdmin):
    list_display = ("faculty", "course", "semester", "years")
    search_fields = ("faculty", "scope")
    list_filter = ("faculty", "course", "semester", "years")


@admin.register(Event)
class EventAdmin(BaseAdmin):
    list_display = ("abstract_event__subject", "abstract_event__kind")
    search_fields = ("abstract_event__subject__name", "abstract_event__kind__name")
    list_filter = ("abstract_event__kind__name",)


@admin.register(AbstractEvent)
class AbstractEventAdmin(BaseAdmin):
    list_display = ("subject", "kind")
    search_fields = ("subject__name", "kind__name")
    list_filter = ("kind__name",)


@admin.register(AbstractDay)
class AbstractDayAdmin(BaseAdmin):
    list_display = ("name", "day_number")
    search_fields = ("name", "day_number")


@admin.register(AbstractSchedule)
class AbstractScheduleAdmin(BaseAdmin):
    list_display = ("repetition_period", "department__name", "aligned_by_week_day")
    search_fields = ("repetition_period", "department__name", "aligned_by_week_day")


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ("name", "organization__name")
    search_fields = ("name", "organization__name")
    list_filter = ("name", "organization__name")


@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(TimeSlot)
class TimeSlotAdmin(BaseAdmin):
    list_display = ("alt_name", "start_time", "end_time")
    search_fields = ("alt_name", "start_time", "end_time")
    list_filter = ("alt_name",)


TokenAdmin.raw_id_fields = ["user"]