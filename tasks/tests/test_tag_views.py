from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Tag


class TagListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:tag-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/tag_list.html")
        self.assertIn("tag_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Tag.objects.create(name="blocked")
        Tag.objects.create(name="urgent")

        response = self.client.get(self.url)
        tags = Tag.objects.all()
        self.assertEqual(
            list(response.context["tag_list"]),
            list(tags)
        )

    def test_queryset_with_filter_returns_matching(self):
        Tag.objects.create(name="blocked")
        Tag.objects.create(name="urgent")

        response = self.client.get(self.url, {"name": "loc"})
        tags = Tag.objects.filter(name__icontains="loc")
        self.assertEqual(
            list(response.context["tag_list"]),
            list(tags)
        )

    def test_queryset_with_filter_no_match(self):
        Tag.objects.create(name="blocked")

        response = self.client.get(self.url, {"name": "gen"})
        self.assertEqual(list(response.context["tag_list"]), [])

    def test_pagination_first_page(self):
        Tag.objects.bulk_create(
            [Tag(name=f"Tag {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["tag_list"]), 10)

    def test_pagination_second_page(self):
        Tag.objects.bulk_create(
            [Tag(name=f"Position {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["tag_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["tag_list"]), [])


class PublicTagCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:tag-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTagCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("tasks:tag-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/tag_form.html")
        self.assertIn("form", response.context)

    def test_create_tag_valid_post(self):
        data = {"name": "blocked"}
        response = self.client.post(self.url, data)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.first().name, "blocked")
        self.assertRedirects(response, reverse("tasks:tag-list"))

    def test_create_tag_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(Tag.objects.count(), 0)


class PublicTagUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.position = Tag.objects.create(name="blocked")
        self.url = reverse(
            "tasks:position-update",
            args=[self.position.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTagUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.tag = Tag.objects.create(name="blocked")
        self.url = reverse(
            "tasks:tag-update",
            args=[self.tag.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/tag_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "blocked")

    def test_update_tag_valid_post(self):
        response = self.client.post(self.url, {"name": "urgent"})
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "urgent")
        self.assertRedirects(response, reverse("tasks:tag-list"))

    def test_update_tag_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "blocked")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:tag-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTagDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.tag = Tag.objects.create(name="blocked")
        self.url = reverse(
            "tasks:tag-delete",
            args=[self.tag.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTagDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.tag = Tag.objects.create(name="blocked")
        self.url = reverse(
            "tasks:tag-delete",
            args=[self.tag.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "tasks/confirm_delete_tag.html"
        )
        self.assertEqual(response.context["object"], self.tag)

    def test_delete_tag_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tasks:tag-list"))
        self.assertFalse(
            Tag.objects.filter(id=self.tag.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(Tag.objects.filter(id=self.tag.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("tasks:tag-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
