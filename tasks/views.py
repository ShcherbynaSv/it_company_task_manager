from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
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
    paginate_by = 10


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = "__all__"
    template_name = "tasks/position_form.html"
    success_url = reverse_lazy("tasks:position-list")


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = "__all__"
    template_name = "tasks/position_form.html"
    success_url = reverse_lazy("tasks:position-list")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("tasks:position-list")
    template_name = "tasks/confirm_delete_position.html"


class TeamListView(generic.ListView):
    model = Team
    paginate_by = 10


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    fields = "__all__"
    template_name = "tasks/team_form.html"
    success_url = reverse_lazy("tasks:team-list")


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    fields = "__all__"
    template_name = "tasks/team_form.html"
    success_url = reverse_lazy("tasks:team-list")


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    template_name = "tasks/confirm_delete_team.html"
    success_url = reverse_lazy("tasks:team-list")


class TaskTypeListView(generic.ListView):
    model = TaskType
    template_name = "tasks/task_type_list.html"
    context_object_name = "task_type_list"
    paginate_by = 10


class TagListView(generic.ListView):
    model = Tag
    paginate_by = 10


class ProjectListView(generic.ListView):
    model = Project
    paginate_by = 10


class ProjectDetailView(generic.DetailView):
    model = Project

    def get_queryset(self):
        return super().get_queryset().select_related("team")


class WorkerListView(generic.ListView):
    model = Worker
    paginate_by = 10

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

        self.team = None
        team_id = self.request.GET.get("team")
        if team_id:
            queryset = queryset.filter(team_id=team_id)
            try:
                self.team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                self.team = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_position"] = self.position
        context["selected_team"] = self.team
        return context


class WorkerDetailView(generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.object

        all_tasks = list(worker.tasks.all())
        context["completed_tasks"] = [task for task in all_tasks
                                      if task.is_completed]
        context["tasks_in_progress"] = [task for task in all_tasks
                                        if not task.is_completed]

        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("position", "team")
            .prefetch_related("tasks")
        )


class TaskListView(generic.ListView):
    model = Task
    paginate_by = 10

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

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("task_type", "project")
            .prefetch_related("assignees", "tags")
        )
