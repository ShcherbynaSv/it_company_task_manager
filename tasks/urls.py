from django.urls import path

from tasks.views import (
    index,
    PositionListView,
    TeamListView,
    TaskTypeListView,
    TagListView,
    ProjectListView,
    WorkerListView,
    TaskListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("task-types/", TaskTypeListView.as_view(), name="task-type-list"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("tasks", TaskListView.as_view(), name="task-list"),
]

app_name = "tasks"
