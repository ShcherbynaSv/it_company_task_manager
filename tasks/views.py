from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

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
