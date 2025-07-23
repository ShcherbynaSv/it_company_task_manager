from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from .models import Tag, Task, TaskType, Team, Project, Position, Worker


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "tags": Tag.objects.all().count(),
        "tasks": Task.objects.all().count(),
        "task_types": TaskType.objects.all().count(),
        "teams": Team.objects.all().count(),
        "projects": Project.objects.all().count(),
        "positions": Position.objects.all().count(),
        "workers": Worker.objects.all().count()
    }
    return render(request, "tasks/index.html", context=context)


class PositionListView(generic.ListView):
    model = Position


class TeamListView(generic.ListView):
    model = Team


class TaskTypeListView(generic.ListView):
    model = TaskType
    template_name = "tasks/task_type_list.html"
    context_object_name = "task_type_list"


class TagListView(generic.ListView):
    model = Tag


class ProjectListView(generic.ListView):
    model = Project


class WorkerListView(generic.ListView):
    model = Worker

    def get_queryset(self):
        queryset = super().get_queryset()
        position_id = self.request.GET.get("position")
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        return queryset


class TaskListView(generic.ListView):
    model = Task

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_id = self.request.GET.get("tags")
        task_type_id = self.request.GET.get("task_type")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)
        return queryset
