from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import Position, Team, TaskType, Tag, Project, Worker, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "description", "team"]
    list_filter = ["name", "created_at", "team"]
    search_fields = ["name"]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position", "team")
    list_filter = UserAdmin.list_filter + ("position", "team")
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("position", "team")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": ("first_name", "last_name", "position", "team")}
        ),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_at",
        "deadline",
        "project",
        "is_completed",
        "priority",
        "task_type"
    ]


admin.site.register(Position)
admin.site.register(Team)
admin.site.register(TaskType)
admin.site.register(Tag)
