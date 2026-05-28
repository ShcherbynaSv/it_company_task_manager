from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import (
    WorkerCreationForm,
    WorkerUpdateForm,
    TaskForm,
    TagSearchForm,
    PositionSearchForm,
    TeamSearchForm,
    TaskTypeSearchForm,
    ProjectSearchForm,
    WorkerSearchForm,
    TaskSearchForm
)
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
    return render(request, "tasks/about_us.html", context=context)
    # return render(request, "tasks/index.html", context=context)


class PositionListView(generic.ListView):
    model = Position
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PositionListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = PositionSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Position.objects.all()
        form = PositionSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TeamSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Team.objects.all()
        form = TeamSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskTypeListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskTypeSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = TaskType.objects.all()
        form = TaskTypeSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    template_name = "tasks/task_type_form.html"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    template_name = "tasks/task_type_form.html"
    success_url = reverse_lazy("tasks:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    template_name = "tasks/confirm_delete_task_type.html"
    success_url = reverse_lazy("tasks:task-type-list")


class TagListView(generic.ListView):
    model = Tag
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TagSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Tag.objects.all()
        form = TagSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tag
    fields = "__all__"
    template_name = "tasks/tag_form.html"
    success_url = reverse_lazy("tasks:tag-list")


class TagUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Tag
    fields = "__all__"
    template_name = "tasks/tag_form.html"
    success_url = reverse_lazy("tasks:tag-list")


class TagDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tag
    template_name = "tasks/confirm_delete_tag.html"
    success_url = reverse_lazy("tasks:tag-list")


class ProjectListView(generic.ListView):
    model = Project
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = ProjectSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Project.objects.all()
        form = ProjectSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = "__all__"
    template_name = "tasks/project_form.html"
    success_url = reverse_lazy("tasks:project-list")


class ProjectDetailView(generic.DetailView):
    model = Project

    def get_queryset(self):
        return super().get_queryset().select_related("team")


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    fields = "__all__"
    template_name = "tasks/project_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "tasks:project-detail",
            kwargs={"pk": self.object.pk}
        )


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "tasks/confirm_delete_project.html"
    success_url = reverse_lazy("tasks:project-list")


class WorkerListView(generic.ListView):
    model = Worker
    paginate_by = 10

    def get_queryset(self):
        queryset = Worker.objects.select_related("position", "team").all()

        position_id = self.request.GET.get("position")
        self.position = Position.objects.filter(id=position_id).first()\
            if position_id else None
        if self.position:
            queryset = queryset.filter(position=self.position)

        team_id = self.request.GET.get("team")
        self.team = Team.objects.filter(id=team_id).first()\
            if team_id else None
        if self.team:
            queryset = queryset.filter(team=self.team)

        full_name = self.request.GET.get("full_name")
        self.search_form = WorkerSearchForm(
            self.request.GET or None,
            initial={"full_name": full_name}
        )
        if self.search_form.is_valid():
            query = self.search_form.cleaned_data.get("full_name")
            if query:
                parts = query.strip().split()
                if len(parts) == 2:
                    first, second = parts
                    queryset = (
                        queryset.filter(
                            first_name__icontains=first,
                            last_name__icontains=second
                        )
                        | queryset.filter(
                            first_name__icontains=second,
                            last_name__icontains=first
                        )
                    )
                else:
                    queryset = (
                        queryset.filter(first_name__icontains=query)
                        | queryset.filter(last_name__icontains=query)
                    )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkerListView, self).get_context_data(**kwargs)
        context.update({
            "selected_position": self.position,
            "selected_team": self.team,
            "search_form": self.search_form,
        })

        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm
    template_name = "tasks/worker_form.html"
    success_url = reverse_lazy("tasks:worker-list")


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


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerUpdateForm
    template_name = template_name = "tasks/worker_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "tasks:worker-detail",
            kwargs={"pk": self.object.pk}
        )


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    template_name = "tasks/confirm_delete_worker.html"
    success_url = reverse_lazy("tasks:worker-list")


class TaskListView(generic.ListView):
    model = Task
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (queryset.select_related("task_type")
                    .prefetch_related("tags"))

        tag_id = self.request.GET.get("tags")
        self.tag = Tag.objects.filter(id=tag_id).first() if tag_id else None
        if self.tag:
            queryset = queryset.filter(tags=self.tag)

        task_type_id = self.request.GET.get("task_type")
        self.task_type = TaskType.objects.filter(id=task_type_id).first()\
            if task_type_id else None
        if self.task_type:
            queryset = queryset.filter(task_type=self.task_type)

        self.search_form = TaskSearchForm(
            self.request.GET or None,
            initial={"name": self.request.GET.get("name", "")}
        )
        if self.search_form.is_valid():
            query = self.search_form.cleaned_data.get("name")
            if query:
                queryset = queryset.filter(name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "selected_tag": self.tag,
            "selected_task_type": self.task_type,
            "search_form": self.search_form,
        })
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:task-list")


class TaskDetailView(generic.DetailView):
    model = Task

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("task_type", "project")
            .prefetch_related("assignees", "tags")
        )


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "tasks:task-detail",
            kwargs={"pk": self.object.pk}
        )


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "tasks/confirm_delete_task.html"
    success_url = reverse_lazy("tasks:task-list")
