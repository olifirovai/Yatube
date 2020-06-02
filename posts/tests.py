import time

from django.test import TestCase
from django.urls import reverse

from .models import User, Post, Group
from django.core.cache import cache

class TestScriptsUserMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john",
                                             password="johnpassword")
        self.post = Post.objects.create(text="Yesterday", author=self.user)

    def test_profile_after_registration(self):
        data = {"username": "paul", "password1": "paulpassword",
                "password2": "paulpassword"}
        self.client.post(reverse("signup"), data, follow=True)
        user_profile = reverse("profile", kwargs={"username": "paul"})
        response = self.client.get(user_profile)
        self.assertEqual(response.status_code, 200,
                         msg="can't find new user's profile")

    def test_user_can_create_post(self):
        text = "All my troubles seemed so far away..."
        self.client.force_login(self.user)
        response = self.client.post(reverse("new_post"), {"text": text},
                                    follow=True)
        self.assertEqual(response.status_code, 200, msg="can't find new post")

    def test_anonymous_cant_create_post(self):
        create_post = reverse("new_post")
        response = self.client.get(create_post, follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/",
                             status_code=302, target_status_code=200)

    def test_user_can_edit_post(self):
        text = "Now it looks as though they are here to stay"
        self.client.force_login(self.user)
        page_edit = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        user_edit_post = self.client.post(page_edit, {"text": text},
                                          follow=True)
        self.assertEqual(user_edit_post.status_code, 200,
                         msg="user can't create new post")

    def test_user_can_delete_post(self):
        self.client.force_login(self.user)
        page_delete = reverse("post_delete",
                              kwargs={"username": self.user.username,
                                      "post_id": self.post.id})
        self.client.post(page_delete, follow=True)
        page_post = reverse("post", kwargs={"username": self.user.username,
                                            "post_id": self.post.id})
        response_post = self.client.get(page_post, follow=True)
        self.assertEqual(response_post.status_code, 404,
                         msg="if post was deleted, page shouldn't be found")


class TestScriptsPostMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="paul",
                                             password="paulpassword")
        self.post = Post.objects.create(text="Oh, I believe in yesterday",
                                        author=self.user)

    def test_new_post_is_on_index(self):
        cache.clear()
        text = "Suddenly"
        self.client.force_login(self.user)
        self.client.post(reverse("new_post"), {"text": text}, follow=True)
        time.sleep(21)
        response_index = self.client.get(reverse("index"))
        self.assertContains(response_index, text)

    def test_new_post_is_on_profile(self):
        text = "I am not half the man I used to be"
        self.client.force_login(self.user)
        self.client.post(reverse("new_post"), {"text": text}, follow=True)
        page_profile = reverse("profile",
                               kwargs={"username": self.user.username})
        response_profile = self.client.get(page_profile, follow=True)
        self.assertContains(response_profile, text)

    def test_new_post_is_on_post(self):
        text = "There is a shadow hanging over me"
        self.client.force_login(self.user)
        self.client.post(reverse("new_post"), {"text": text}, follow=True)
        new_post_id = Post.objects.get(text=text)
        page_post = reverse("post", kwargs={"username": self.user.username,
                                            "post_id": new_post_id.id})
        response_post = self.client.get(page_post, follow=True)
        self.assertContains(response_post, text)

    def test_edited_post_is_on_index(self):
        cache.clear()
        text = "Oh, yesterday came suddenly"
        self.client.force_login(self.user)
        page_edit = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        self.client.post(page_edit, {"text": text}, follow=True)
        response_index = self.client.get(reverse("index"))
        self.assertContains(response_index, text)

    def test_edited_post_is_on_profile(self):
        text = "Why she had to go"
        self.client.force_login(self.user)
        page_edit = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        self.client.post(page_edit, {"text": text}, follow=True)
        page_profile = reverse("profile",
                               kwargs={"username": self.user.username})
        response_profile = self.client.get(page_profile, follow=True)
        self.assertContains(response_profile, text)

    def test_edited_post_is_on_post(self):
        text = "I do not know, she would not say"
        self.client.force_login(self.user)
        page_edit = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        self.client.post(page_edit, {"text": text}, follow=True)
        page_post = reverse("post", kwargs={"username": self.user.username,
                                            "post_id": self.post.id})
        response_post = self.client.get(page_post, follow=True)
        self.assertContains(response_post, text)


class TestScriptsErrorsMethods(TestCase):
    def test_code_404_if_page_not_found(self):
        unknown_page = reverse("profile", kwargs={"username": "unknown"})
        response = self.client.get(unknown_page, follow=True)
        self.assertEqual(response.status_code, 404,
                         msg="page should not be found, code 404")


class TestScriptsImageMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Botticelli",
                                             password="alexthebest")
        self.group = Group.objects.create(title="Art", slug="art")
        self.post = Post.objects.create(text="The Birth of Venus",
                                        author=self.user)
        self.client.force_login(self.user)
        img = open("media/posts/La_nascita_di_Venere.jpg", "rb")
        edit_page = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        self.client.post(edit_page, {"text": self.post.text, "image": img,
                                     "group": self.group.id}, follow=True)

    def test_teg_img_is_on_post(self):
        post_page = reverse("post", kwargs={"username": self.user.username,
                                            "post_id": self.post.id})
        response = self.client.get(post_page, follow=True)
        tag = "<img class="
        self.assertContains(response, tag)

    def test_teg_img_is_on_index(self):
        cache.clear()
        response = self.client.get(reverse("index"), follow=True)
        tag = "<img class="
        self.assertContains(response, tag)

    def test_teg_img_is_on_profile(self):
        profile_page = reverse("profile",
                               kwargs={"username": self.user.username})
        response = self.client.get(profile_page, follow=True)
        tag = "<img class="
        self.assertContains(response, tag)

    def test_teg_img_is_on_group(self):
        group_page = reverse("group", kwargs={"slug": self.group.slug})
        response = self.client.get(group_page, follow=True)
        tag = "img "
        self.assertContains(response, tag)

    def test_upload_only_image_format(self):
        self.client.force_login(self.user)
        non_image = open("media/posts/La_nascita_di_Venere.docx", "rb")
        edit_page = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        response = self.client.post(edit_page,
                                    {"text": self.post.text,
                                     "image": non_image,
                                     "group": self.group.id}, follow=True)
        self.assertIn("image", response.context["form"].errors)


class TestScriptsCacheMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cache",
                                             password="cachepassword")
        self.post = Post.objects.create(text="Cache is a very important thing",
                                        author=self.user)

    def test_cache_work_on_index(self):
        text = "Cache is a very important thing"
        new_text = "I dont know"
        self.client.force_login(self.user)
        self.client.get(reverse("index"))
        page_edit = reverse("post_edit",
                            kwargs={"username": self.user.username,
                                    "post_id": self.post.id})
        self.client.post(page_edit, {"text": new_text}, follow=True)
        time.sleep(19)
        response_index_cache = self.client.get(reverse("index"))
        self.assertContains(response_index_cache, text)
        time.sleep(21)
        response_index = self.client.get(reverse("index"))
        self.assertContains(response_index, new_text)
