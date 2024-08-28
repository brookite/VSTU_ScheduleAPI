import json
import os

from django.core.management.base import BaseCommand

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

"""
Этот скрипт не адаптирован для больших наборов данных.
Он предназначен только для простого тестирования и демонстрации возможностей

Кроме того, он требует введения всех данных об объекте, что осложняет обновление

Если у вас есть желание, вы можете улучшить скрипт, адаптировать его под bulk-добавление/обновление данных,
при которых минимизируется количество запросов к базе данных.
"""


class Command(BaseCommand):
    help = "Загружает тестовые данные в базу данных"

    def fill_data(self, data):
        # Загрузка Subjects
        for item in data.get("subjects", []):
            Subject.objects.update_or_create(id=item["id"], defaults={"name": item["name"]})

        # Загрузка EventKinds
        for item in data.get("event_kinds", []):
            EventKind.objects.update_or_create(id=item["id"], defaults={"name": item["name"]})

        # Загрузка TimeSlots
        for item in data.get("time_slots", []):
            TimeSlot.objects.update_or_create(
                id=item["id"],
                defaults={"start_time": item["start_time"], "end_time": item["end_time"]},
            )

        # Загрузка EventPlaces
        for item in data.get("event_places", []):
            EventPlace.objects.update_or_create(
                id=item["id"], defaults={"building": item["building"], "room": item["room"]}
            )

        # Загрузка EventParticipants
        for item in data.get("event_participants", []):
            EventParticipant.objects.update_or_create(
                id=item["id"], defaults={"name": item["name"], "role": item["role"]}
            )

        # Загрузка Schedules
        for item in data.get("schedules", []):
            schedule = Schedule.objects.update_or_create(
                id=item["id"],
                defaults={
                    "faculty": item["faculty"],
                    "scope": item["scope"],
                    "course": item["course"],
                    "semester": item["semester"],
                    "years": item["years"],
                },
            )[0]
            schedule.save()

        # Загрузка Events
        for item in data.get("events", []):
            event = Event.objects.update_or_create(
                id=item["id"],
                defaults={
                    "subject_id": item["subject_id"],
                    "kind_id": item["kind_id"],
                    "schedule_id": item["schedule_id"],
                },
            )[0]
            event.participants.set(item["participants"])
            event.save()

        # Загрузка EventHoldings
        for item in data.get("event_holdings", []):
            EventHolding.objects.update_or_create(
                id=item["id"],
                defaults={
                    "event_id": item["event_id"],
                    "place_id": item["place_id"],
                    "date": item["date"],
                    "time_slot_id": item["slot_id"],
                },
            )

    def handle(self, *args, **kwargs):
        datadir = os.path.abspath("testdata")
        for file in os.listdir(datadir):
            if file.endswith(".json"):
                with open(os.path.join(datadir, file), "r", encoding="utf-8") as fd:
                    data = json.load(fd)
                    self.stdout.write(f"Заполнение данных из файла {file}")
                    self.fill_data(data)
        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены в базу данных"))
