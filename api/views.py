from django.shortcuts import redirect
from api.filters import EventFilter, ScheduleFilter
from api.models import Event, EventKind, EventParticipant, EventPlace, Schedule, Subject
from api.serializers import (
    EventParticipantSerializer,
    EventPlaceSerializer,
    EventSerializer,
    ScheduleSerializer,
    SubjectSerializer,
)
from rest_framework import generics, filters, status, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.routers import APIRootView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend


class SchedulesAPIRootView(APIRootView):
    """
    Данное API предназначен для получения, изменения обновления информации о расписаниях ВолгГТУ
    API предоставляет базовое управления сущностями, представляющими элементы расписания

    # Общая информация
    API позволяет управлять следующими сущностями:<br>
    - [Расписание](/api/schedules)<br>
    - [Занятие](/api/events)<br>
    - [Место проведения](/api/lessonrooms)<br>
    - [Тип события](/api/events/kind)<br>
    - [Группы](/api/groups) и [преподаватели](/api/teachers)<br>


    Каждая сущность имеет вариативность действия в зависимости от метода запроса.
    Так, GET возвращает список всех сущностей, POST - добавляет новую.

    Большинство списков сущностей поддерживают опциональный аргумент `search` в URL,
    который позволяет искать записи по ключевым полям

    Более того, можно просматривать элемент каждой сущности по id. Пример URL: `/api/events/1`,
    он также поддерживает методы PUT, UPDATE, DELETE для модификации значений.


    > Возможности создания, удаления, обновления записей поддерживаются,
    > только если пользователь авторизован как администратор

    Администраторам доступны дополнительные (отладочные поля)
    в ответе для каждой записи, которые могут отсутствовать, если они равны `null`: <br>

    - `datecreated` - дата создания записи (нельзя изменить) <br>
    - `datemodified` - дата изменения записи (нельзя изменить) <br>
    - `dateaccessed` - дата последнего доступа к записи (нельзя изменить) <br>
    - `idnumber` - уникальный строковый идентификатор для отладочных целей <br>
    - `author` - автор записи (может быть программным компонентом, т.е. сервисным аккаунтом) <br>
    - `note` - комментарий для записи (максимальная длина - 1024 символа) <br>

    ## Внутренние коды ошибок
    `0` - неизвестная ошибка. Более подробную информацию нужно брать из сообщения об ошибке и кода ошибки HTTP<br>
    `1` - ошибка проверки данных. Одно из переданных значений не является валидным<br>
    `2` - ошибка доступа. Возможно, требуется авторизация или особая роль<br>
    `3` - ошибка выполнения аутентификации<br>
    `4` - нереализованная на данный момент возможность API<br>

    Если вы являетесь администратором, то можете [перейти в панель администратора](/admin),
    в которой доступно более детальное управление базой данных расписаний
    """

    def get_view_name(self):
        return "API Расписаний ВолгГТУ"


class EventKindListView(generics.ListAPIView):
    """
    # GET
    - Возвращает: список строк - известных типов событий <br>

    > Типы событий нельзя изменить из API, их можно только просмотреть все
    """

    queryset = EventKind.objects.all()

    def get(self, request, *args, **kwargs):
        event_kinds = EventKind.objects.values("name")
        return Response(event_kinds)

    def get_view_name(self):
        return "Типы событий"


class CommonViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = []

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class SubjectViewSet(CommonViewSet):
    """
    # GET
    - Поддерживается поиск по списку <br>
    - Возвращает список объектов - предметов <br>
    Пример формата:
    ```json
    {
        "name": "Subject", // название предмета
        "id": 3
    }
    ```
    # Аргументы, доступные для изменения <br>
    - `name` - имя (строка)
    """

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ["name"]

    def get_view_name(self):
        return "Предмет"


class LessonRoomViewSet(CommonViewSet):
    """
    # GET
    - Поддерживается поиск по списку <br>
    - Возвращает список объектов - местах проведения <br>
    Пример формата:
    ```json
    {
        "building": "ГУК",
        "room": "303",
        "id": 30
    }
    ```

    # Аргументы, доступные для изменения:
    - `room` - аудитория (строка) <br>
    - `building` - корпус (строка) <br>
    """

    queryset = EventPlace.objects.all()
    serializer_class = EventPlaceSerializer
    search_fields = ["building", "room"]

    def get_view_name(self):
        return "Место проведения"


class GroupViewSet(CommonViewSet):
    """
    # GET
    - Поддерживается поиск по списку <br>
    - Возвращает список объектов - участников занятия в роли студентов (групп) <br>
    Пример формата:
    ```json
    {
        "id": 4,
        "name": "ПрИн-367"
        "role": "student",
    }
    ```

    # Аргументы, доступные для изменения: <br>
    - `name` - название группы (строка) <br>
    - `role` - значение всегда "student" <br>
    """

    queryset = EventParticipant.objects.filter(role=EventParticipant.Role.STUDENT).all()
    serializer_class = EventParticipantSerializer
    search_fields = ["name"]

    def get_view_name(self):
        return "Группа"


class TeacherViewSet(CommonViewSet):
    """
    # GET
    - Поддерживается поиск по списку <br>
    - Возвращает список объектов - участников занятия в роли студентов (групп) <br>
    Пример формата:
    ```json
    {
        "id": 7,
        "name": "Иванов Иван Иванович"
        "role": "teacher"
    }
    ```

    # Аргументы, доступные для изменения: <br>
    - `name` - название группы (строка) <br>
    - `role` - значение всегда "teacher" или "assistant" <br>
    """

    queryset = EventParticipant.objects.filter(
        role__in=[EventParticipant.Role.ASSISTANT, EventParticipant.Role.TEACHER]
    )
    serializer_class = EventParticipantSerializer
    search_fields = ["name"]

    def get_view_name(self):
        return "Преподаватель"


class EventViewSet(CommonViewSet):
    """
    # GET
    - Возвращает список объектов - занятий (событий), привязанных к расписанию <br>
    Пример формата:
    ```json
    {
        "id": 7,
        "subject": {
            "name": "Программирование",
            "id": 782
        },
        "kind": "Семинар",
        "participants": [
            {
                "name": "ПрИн-266",
                "role": "student"
            }
        ],
        "holding_info": [
            {
                "place": {
                    "building": "ГУК",
                    "room": "303",
                    "id": 30
                },
                "date": "2024-10-01"
                "time_slot": {
                    "start": [10, 10],
                    "end": [11, 40]
                }
            }
        ]
    }
    ```

    ## Аргументы GET-запроса для фильтрации списка: <br>
    - `schedule` - целое число, вывод занятий, принадлежащих заданному расписанию <br>
    - `date_from`, `date_to` - искать занятия среди дат (от и до включительно), строка даты в формате ISO-8601 <br>
    - `time_from`, `time_to` - искать занятия, проходящие в это время. Рассматривается отдельно от даты, строка времени в формате ISO-8601 <br>
    - `participants` - список ID возможных участников. Работает как фильтр, а не точный поиск по наличию всех заданных участников <br>
    - `can_have_kind` - список строк - возможных типов события.  Работает как фильтр, а не точный поиск по наличию всех заданных типов <br>
    - `possible_rooms` - список ID возможных аудиторий. Работает как фильтр, а не точный поиск по наличию всех заданных участников <br>

    # Аргументы, доступные для изменения: <br>
    - `subject` - предмет (объект, [см. предметы](/api/subjects)) <br>
    - `kind` - [тип события](/api/events/kind) <br>
    - `participants` - список участников (см. [группу](/api/groups) или [преподавателей](/api/teachers)) <br>
    - `holding_info` - объект с полями: <br>
        - `place` - [см. места проведения](/api/lessonrooms) <br>
        - `date` - дата (без времени) в формате ISO-8601 <br>
        - `time_slot` - временной интервал с временем начала и окончания. <br>
        Время представляется как массив [часы, минуты]

    """

    filterset_class = EventFilter
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_view_name(self):
        return "Занятие"


class ScheduleViewSet(CommonViewSet):
    """
    # GET
    - Поддерживается поиск по списку <br>
    - Возвращает список объектов - информацию о расписаниях <br>
    Пример формата:
    ```json
    {
        "faculty": "ФЭВТ",
        "scope": "bachelor",
        "course": 3,
        "semester": 1,
        "years": "2024-2025",
        "id": 5,
        "start_date": "2024-09-02", // дата первого занятия в расписании
        "end_date": "2024-12-29" // дата последнего занятия в расписании
    }
    ```

    ## Аргументы GET-запроса для фильтрации списка: <br>
    - `faculty` - строка, показать расписания принадлежащие факультету <br>
    - `scope` - строка, показать расписания соответствующие данному типу обучения (см. аргументы объекта ниже) <br>
    - `course` - целое число, номер курса <br>
    - `semester` - целое число, семестр курса <br>
    - `has_events` - список ID занятий, которые должны содержаться в найденных расписаниях (не обязательно в одном расписании). <br>


    # Аргументы доступные для изменения: <br>
    - `faculty` - факультет (строка) <br>
    - `scope` - приндлежность расписания к обучению, одно из значений: "bachelor", "master", "postgraduate", "consultation" <br>
    - `course` - целое число, номер курса <br>
    - `semester` - целое число, номер семестра <br>
    - `years` - учебный год обучения (строка, пример: 2024-2025) <br>
    """

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    search_fields = ["faculty", "years"]
    filterset_class = ScheduleFilter

    def get_view_name(self):
        return "Расписание"


@api_view(["GET"])
@permission_classes([IsAdminUser])
def import_db(request):
    # Заглушка для импорта базы данных
    return Response(
        {"type": "error", "message": "Not implemented", "error_code": 4},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def import_json(request):
    # Заглушка для импорта JSON
    return Response(
        {"type": "error", "message": "Not implemented", "error_code": 4},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )

def index(request):
    return redirect("/api", False)
