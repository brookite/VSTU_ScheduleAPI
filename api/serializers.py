from rest_framework import serializers

from api.models import (
    Event,
    EventHolding,
    EventKind,
    EventParticipant,
    EventPlace,
    Schedule,
    Subject,
    TimeSlot,
)
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
    visible_nullable = []  # nullable поля, которые нужно обязательно выводить всегда, даже если они равны

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

    def _detect_record_update(self, instance, validated_data):
        request = self.context.get("request")

        if request and request.user.is_staff:
            for field in self.admin_fields:
                if field in validated_data and field in self.admin_fields:
                    validated_data[field] = self.admin_fields[field].to_internal_value(
                        validated_data[field]
                    )
                    setattr(instance, field, validated_data[field])

    def update(self, instance, validated_data):
        self._detect_record_update(instance, validated_data)
        return super().update(instance, validated_data)


class CommonModelListSerializer(serializers.ListSerializer):
    # Класс, нужный для множественного сохранения данных во вложенные сериализаторы
    def update(self, instance, validated_data):
        instance = instance.all()
        participant_mapping = {item.id: item for item in instance}
        ret = []

        for participant_data in validated_data:
            participant = participant_mapping.get(participant_data.get("id"), None)
            if participant:
                ret.append(self.child.update(participant, participant_data))
            else:
                ret.append(self.child.create(participant_data))

        return ret


class SubjectSerializer(CommonModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]
        list_serializer_class = CommonModelListSerializer


class TimeSlotSerializer(CommonModelSerializer):
    start_time = TimeArrayField(label="Время начала")
    end_time = TimeArrayField(required=False, allow_null=True, label="Время окончания")

    class Meta:
        model = TimeSlot
        fields = ["start_time", "end_time"]
        list_serializer_class = CommonModelListSerializer


class EventParticipantSerializer(CommonModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ["id", "name", "role"]
        list_serializer_class = CommonModelListSerializer


class EventPlaceSerializer(CommonModelSerializer):
    class Meta:
        model = EventPlace
        fields = ["id", "building", "room"]
        list_serializer_class = CommonModelListSerializer


class EventHoldingSerializer(CommonModelSerializer):
    place = EventPlaceSerializer(label="Место")
    time_slot = TimeSlotSerializer(label="Временной интервал")
    date = serializers.DateField(format="iso-8601", label="Дата")

    class Meta:
        model = EventHolding
        fields = ["place", "date", "time_slot"]
        list_serializer_class = CommonModelListSerializer

    # DRF возлагает создание и обновление объектов из вложенных сериализаторов на разработчика!
    def create(self, validated_data):
        place_data = validated_data.pop("place")
        time_slot_data = validated_data.pop("time_slot")

        # Используем вложенные сериализаторы для создания объектов
        # DRF возлагает создание объектов из вложенных сериализаторов на разработчика!
        place_serializer = EventPlaceSerializer(data=place_data)
        place_serializer.is_valid(raise_exception=True)
        place = place_serializer.save()

        time_slot_serializer = TimeSlotSerializer(data=time_slot_data)
        time_slot_serializer.is_valid(raise_exception=True)
        time_slot = time_slot_serializer.save()

        event_holding = EventHolding.objects.create(
            place=place, time_slot=time_slot, **validated_data
        )

        return event_holding

    def update(self, instance, validated_data):
        place_data = validated_data.pop("place", None)
        time_slot_data = validated_data.pop("time_slot", None)

        if place_data:
            place_serializer = EventPlaceSerializer(
                instance.place,
                data=place_data,
            )
            place_serializer.is_valid(raise_exception=True)
            place_serializer.save()

        if time_slot_data:
            time_slot_serializer = TimeSlotSerializer(instance.time_slot, data=time_slot_data)
            time_slot_serializer.is_valid(raise_exception=True)
            time_slot_serializer.save()

        instance.date = validated_data.get("date", instance.date)
        self._detect_record_update(instance, validated_data)
        instance.save()

        return instance


class EventSerializer(CommonModelSerializer):
    participants = EventParticipantSerializer(many=True, label="Участники")
    subject = SubjectSerializer(label="Предмет")
    kind = serializers.CharField(source="kind.name", label="Тип события")
    holding_info = EventHoldingSerializer(
        source="holdings", many=True, label="Информация о проведении"
    )
    schedule_id = serializers.PrimaryKeyRelatedField(
        source="schedule", label="Расписание", queryset=Schedule.objects.all()
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

    # DRF возлагает создание и обновление объектов из вложенных сериализаторов на разработчика!
    def create(self, validated_data):
        participants_data = validated_data.pop("participants")
        subject_data = validated_data.pop("subject")
        holding_info_data = validated_data.pop("holdings")
        kind = validated_data.pop("kind")

        participants_serializer = EventParticipantSerializer(data=participants_data, many=True)
        participants_serializer.is_valid(raise_exception=True)
        participants = participants_serializer.save()

        subject_serializer = SubjectSerializer(data=subject_data)
        subject_serializer.is_valid(raise_exception=True)
        subject = subject_serializer.save()

        holding_info_serializer = EventHoldingSerializer(data=holding_info_data, many=True)
        holding_info_serializer.is_valid(raise_exception=True)
        holding_info = holding_info_serializer.save()

        kind_model = EventKind.objects.get_or_create(name=kind.get("name"))[0]

        event = Event.objects.create(
            kind=kind_model,
            subject=subject,
            **validated_data,
        )

        event.participants.set(participants)
        event.holdings.set(holding_info)

        return event

    def update(self, instance, validated_data):
        participants_data = validated_data.pop("participants", None)
        subject_data = validated_data.pop("subject", None)
        holding_info_data = validated_data.pop("holdings", None)
        kind_data = validated_data.pop("kind", None)

        if participants_data:
            participants_serializer = EventParticipantSerializer(
                instance.participants, data=participants_data, many=True
            )
            participants_serializer.is_valid(raise_exception=True)
            participants = participants_serializer.save()
            instance.participants.set(participants)

        if subject_data:
            subject_serializer = SubjectSerializer(instance.subject, data=subject_data)
            subject_serializer.is_valid(raise_exception=True)
            instance.subject = subject_serializer.save()

        if holding_info_data:
            holding_info_serializer = EventHoldingSerializer(
                instance.holdings, data=holding_info_data, many=True
            )
            holding_info_serializer.is_valid(raise_exception=True)
            holding_info = holding_info_serializer.save()
            instance.holdings.set(holding_info)

        if kind_data:
            kind_model, _ = EventKind.objects.get_or_create(name=kind_data.get("name"))
            instance.kind = kind_model

        self._detect_record_update(instance, validated_data)
        instance.save()

        return instance


class ScheduleSerializer(CommonModelSerializer):
    start_date = serializers.SerializerMethodField(label="Дата начала занятий")
    finish_date = serializers.SerializerMethodField(label="Дата окончания занятий")

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
