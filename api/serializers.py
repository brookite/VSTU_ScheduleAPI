from api.models import (
    Event,
    EventHolding,
    EventParticipant,
    EventPlace,
    Schedule,
    Subject,
    TimeSlot,
)
from rest_framework import serializers

from api.serializer_fields.time import TimeArrayField, TimestampField


class CommonModelSerializer(serializers.ModelSerializer):
    admin_readonly_fields = {
        "datecreated": TimestampField(),
        "datemodified": TimestampField(),
        "dateaccessed": TimestampField(allow_null=True),
    }
    admin_fields = {
        "idnumber": serializers.CharField(allow_null=True),
        "note": serializers.CharField(allow_blank=True, allow_null=True, max_length=1024),
        "author": serializers.CharField(allow_null=True),
    }
    visible_nullable = []  # nullable поля, которые нужно обязательно выводить всегда, даже если они равны null

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if request and request.user.is_staff:
            for field in self.admin_readonly_fields:
                value = getattr(instance, field)
                if value is None:
                    representation[field] = None
                else:
                    representation[field] = self.admin_readonly_fields[field].to_representation(
                        value
                    )
            for field in self.admin_fields:
                value = getattr(instance, field)
                if value is None:
                    representation[field] = None
                else:
                    representation[field] = self.admin_fields[field].to_representation(value)

        # убираем из вывода ненужные null поля
        return {
            key: value
            for key, value in representation.items()
            if value is not None or value in self.visible_nullable
        }

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and request.user.is_staff:
            for field in self.admin_fields:
                if field in validated_data and field in self.admin_fields:
                    validated_data[field] = self.admin_fields[field].to_internal_value(
                        validated_data[field]
                    )
                    setattr(instance, field, validated_data[field])

        return super().update(instance, validated_data)


class SubjectSerializer(CommonModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class TimeSlotSerializer(CommonModelSerializer):
    start = TimeArrayField(source="start_time")
    end = TimeArrayField(source="end_time", required=False, allow_null=True)

    class Meta:
        model = TimeSlot
        fields = ["start", "end"]


class EventParticipantSerializer(CommonModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ["id", "name", "role"]


class EventPlaceSerializer(CommonModelSerializer):
    class Meta:
        model = EventPlace
        fields = ["id", "building", "room"]


class EventHoldingSerializer(CommonModelSerializer):
    place = EventPlaceSerializer()
    time_slot = TimeSlotSerializer()
    date = serializers.DateField(format="iso-8601")

    class Meta:
        model = EventHolding
        fields = ["place", "date", "time_slot"]


class EventSerializer(CommonModelSerializer):
    participants = EventParticipantSerializer(many=True, help_text="Участники")
    subject = SubjectSerializer(help_text="Предмет")
    kind = serializers.CharField(source="kind.name", help_text="Тип события")
    holding_info = EventHoldingSerializer(
        source="holdings", many=True, help_text="Информация о проведении"
    )
    schedule_id = serializers.PrimaryKeyRelatedField(
        source="schedule", read_only=True, help_text="Расписание"
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "kind",
            "participants",
            "subject",
            "holding_info",
            "schedule_id",
        ]


class ScheduleSerializer(CommonModelSerializer):
    start_date = serializers.SerializerMethodField()
    finish_date = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = [
            "id",
            "faculty",
            "scope",
            "course",
            "years",
            "semester",
            "start_date",
            "finish_date",
        ]

    def get_start_date(self, instance):
        return instance.first_event().min_date

    def get_finish_date(self, instance):
        return instance.last_event().max_date
