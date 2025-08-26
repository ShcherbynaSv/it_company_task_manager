from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from tasks.models import Worker, Task


class WorkerCreationForm(UserCreationForm):
    class Meta:
        fields = (UserCreationForm.Meta.fields
                  + ("first_name", "last_name", "email", "position", "team"))
        model = Worker


class WorkerUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = Worker
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "position",
            "team"
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name", "description", "deadline", "is_completed",
            "priority", "task_type", "assignees", "project", "tags"
        ]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter task details...",
                    "class": "form-control"
                }
            ),
            "assignees": forms.CheckboxSelectMultiple(),
            "tags": forms.CheckboxSelectMultiple(),
        }
