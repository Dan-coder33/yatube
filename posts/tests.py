from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post


class TestPostsCreation(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client_auth.force_login(self.user)
        Post.objects.create(text="text", author=self.user)  # noqa

    def test_profile(self):
        response = self.client.get(
            reverse(
                "profile",
                kwargs=dict(username=self.user.username)
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        posts_number_before = Post.objects.all().count()  # noqa
        response = self.client_auth.post(
            reverse("new_post"),
            data={"text": "test"}
        )
        self.assertEqual(response.status_code, 302)
        posts_number_after = Post.objects.all().count()  # noqa
        self.assertEqual(posts_number_before + 1, posts_number_after)
        self.assertTrue(Post.objects.filter(text="test").exists())  # noqa

    def test_new_post_cancel(self):
        posts_number_before = Post.objects.all().count()  # noqa
        self.client.post(reverse("new_post"), data={"text": "teeest"})
        posts_number_after = Post.objects.all().count()  # noqa
        self.assertEqual(posts_number_before, posts_number_after)
        self.assertFalse(Post.objects.filter(text="teeeest").exists())  # noqa

    def check_urls(self, post, post_text):
        for url in (
                reverse("index"),
                reverse("profile", kwargs={"username": self.user.username}),
                reverse("post", kwargs={
                    "username": self.user.username,
                    "post_id": post.id,
                })
        ):
            response = self.client.get(url)
            self.assertContains(response, post_text)

    def test_post_pg(self):
        post_text = "text"
        post = Post.objects.create(text=post_text, author=self.user)  # noqa
        self.check_urls(post, post_text)

    def test_post_pg_edit(self):
        post_text = "edit_text"
        post = get_object_or_404(Post, text="text")
        post_id = post.id
        self.client_auth.post(
            reverse(
                "post_edit",
                kwargs={
                    "username": self.user.username,
                    "post_id": post_id,
                }
            ),
            data={"text": post_text}
        )

        self.check_urls(post, post_text)


class TestErrors(TestCase):
    def test_404(self):
        response = self.client.get(
            "404/"
        )
        self.assertEqual(response.status_code, 404)


class TestImg(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client_auth.force_login(self.user)

    def test_post_img(self):
        with open("media/posts/test_picture.png", "rb") as img:
            post = self.client_auth.post(
                reverse("new_post"),
                data={
                    "author": self.user,
                    "text": "post with image",
                    "image": img
                },
                follow=True
            )

        self.assertEqual(post.status_code, 200)
        self.assertEqual(Post.objects.count(), 1) # noqa

    def test_all_contains_img(self):
        with open("media/posts/test_picture.png", "rb") as img:
            self.client_auth.post(
                reverse("new_post"),
                data={
                    "author": self.user,
                    "text": "post with image 2",
                    "image": img
                },
                follow=True
            )

        post = Post.objects.first() # noqa
        urls = [
            reverse("index"),
            reverse(
                "post",
                kwargs={
                    "username": post.author,
                    "post_id": post.id,
                }
            ),
            reverse(
                "profile",
                kwargs={
                    "username": post.author,
                }
            ),
        ]

        for url in urls:
            response = self.client_auth.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "img")

    def test_img_format(self):
        with open("media/posts/file.txt", "rb") as img:
            post = self.client_auth.post(
                reverse('new_post'),
                data={
                    "author": self.user,
                    "text": "post with image 3",
                    "image": img
                },
                follow=True)

        self.assertEqual(post.status_code, 200)
        self.assertEqual(Post.objects.count(), 1) # noqa


class TestCache(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client_auth.force_login(self.user)
        Post.objects.create(text="text", author=self.user)  # noqa

    def test_cache_index(self):
        pass
