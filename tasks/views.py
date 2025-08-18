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
        self.position = None
        position_id = self.request.GET.get("position")
        if position_id:
            queryset = queryset.filter(position_id=position_id)
            try:
                self.position = Position.objects.get(id=position_id)
            except Position.DoesNotExist:
                self.position = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_position"] = self.position
        return context


class WorkerDetailView(generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.get_object()

        context["completed_tasks"] = worker.tasks.filter(is_completed=True)
        context["tasks_in_progress"] = worker.tasks.filter(is_completed=False)

        return context


class TaskListView(generic.ListView):
    model = Task

    def get_queryset(self):
        queryset = super().get_queryset()
        self.tag = None
        self.task_type = None

        tag_id = self.request.GET.get("tags")
        task_type_id = self.request.GET.get("task_type")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
            try:
                self.tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                self.tag = None
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)
            try:
                self.task_type = TaskType.objects.get(id=task_type_id)
            except TaskType.DoesNotExist:
                self.task_type = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_tag"] = self.tag
        context["selected_task_type"] = self.task_type
        return context


class TaskDetailView(generic.DetailView):
    model = Task
