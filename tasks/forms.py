from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from tasks.models import Worker


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
