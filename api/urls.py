from django.urls import path
from api.views import (
    EventKindListView,
    EventViewSet,
    GroupViewSet,
    LessonRoomViewSet,
    ScheduleViewSet,
    SchedulesAPIRootView,
    SubjectViewSet,
    TeacherViewSet,
    import_db,
    import_json,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=True)
router.APIRootView = SchedulesAPIRootView
router.register(r"subjects", SubjectViewSet, basename="subjects")
router.register(r"events", EventViewSet, basename="events")
router.register(r"lessonrooms", LessonRoomViewSet, basename="lessonrooms")
router.register(r"groups", GroupViewSet, basename="groups")
router.register(r"teachers", TeacherViewSet, basename="teachers")
router.register(r"schedules", ScheduleViewSet, basename="schedules")


urlpatterns = [
    path("events/kind/", EventKindListView.as_view(), name="event-kind-list"),
    path("import/db/", import_db, name="import-db"),
    path("import/json/", import_json, name="import-json"),
]

urlpatterns += router.urls
