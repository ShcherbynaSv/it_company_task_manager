from django.urls import path

from tasks.views import (
    index,
    PositionListView,
    PositionCreateView,
    PositionUpdateView,
    PositionDeleteView,
    TeamListView,
    TaskTypeListView,
    TagListView,
    ProjectListView,
    ProjectDetailView,
    WorkerListView,
    WorkerDetailView,
    TaskListView,
    TaskDetailView
)

urlpatterns = [
    path("", index, name="index"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path(
        "positions/create/",
        PositionCreateView.as_view(),
        name="position-create"
    ),
    path(
        "positions/<int:pk>/update/",
        PositionUpdateView.as_view(),
        name="position-update"
    ),
    path(
        "positions/<int:pk>/delete/",
        PositionDeleteView.as_view(),
        name="position-delete"
    ),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("task-types/", TaskTypeListView.as_view(), name="task-type-list"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path(
        "projects/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail"
    ),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail"
    ),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]

app_name = "tasks"
