from PIL import Image
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse
from six import BytesIO

from posts.models import Post, Follow


class TestPostsCreation(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client_auth.force_login(self.user)
        Post.objects.create(text="text", author=self.user)  # noqa

    def test_open_profile(self):
        response = self.client.get(
            reverse(
                "profile",
                kwargs=dict(username=self.user.username)
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_auth_client_can_create_new_post(self):
        posts_number_before = Post.objects.all().count()  # noqa
        response = self.client_auth.post(
            reverse("new_post"),
            data={"text": "test"}
        )
        self.assertEqual(response.status_code, 302)
        posts_number_after = Post.objects.all().count()  # noqa
        self.assertEqual(posts_number_before + 1, posts_number_after)
        self.assertTrue(Post.objects.filter(text="test").exists())  # noqa

    def test_no_auth_client_can_create_new_post(self):
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

    def test_new_post_on_pages(self):
        post_text = "text"
        post = Post.objects.create(text=post_text, author=self.user)  # noqa
        self.check_urls(post, post_text)

    def test_edit_post_on_pages(self):
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

    def test_auth_client_create_new_post_with_img(self):
        img = self.create_test_image_file()
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
        self.assertEqual(Post.objects.count(), 1)  # noqa

    def test_new_post_with_img_on_pages(self):
        img = self.create_test_image_file()
        self.client_auth.post(
            reverse("new_post"),
            data={
                "author": self.user,
                "text": "post with image 2",
                "image": img
            },
            follow=True
        )

        post = Post.objects.first()  # noqa
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

    def test_new_post_with_wrong_img_format(self):
        img = self.create_test_image_file()
        post = self.client_auth.post(
            reverse("new_post"),
            data={
                "author": self.user,
                "text": "post with image 3",
                "image": img
            },
            follow=True
        )

        self.assertEqual(post.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)  # noqa

    @staticmethod
    def create_test_image_file():
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file


class TestCache(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username="sarah", email="connor.s@skynet.com", password="12345"
        )
        self.client_auth.force_login(self.user)

    def test_cache_index(self):
        Post.objects.create(text="check 1", author=self.user)  # noqa
        response = self.client_auth.get(reverse("index"))
        self.assertContains(response, "check 1")

        Post.objects.create(text="check 2", author=self.user)  # noqa
        response = self.client_auth.get(reverse("index"))
        self.assertNotContains(response, "check 2")


class TestCommentsFollows(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(
            username="follower", email="connor.s@skynet.com", password="12345678"
        )
        self.user_following = User.objects.create_user(
            username="following", email="blablabla@mail.ru", password="123456789"
        )
        self.user = User.objects.create_user(
            username="user", email="a@mail.ru", password="12345"
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_user_follow(self):
        before = Follow.objects.all().count()
        self.client_auth_follower.get(
            reverse(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                },
            )
        )
        after = Follow.objects.all().count()

        self.assertEqual(before + 1, after)

    def test_user_unfollow(self):
        self.client_auth_follower.get(
            reverse(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                },
            )
        )
        before = Follow.objects.all().count()
        self.client_auth_follower.get(
            reverse(
                "profile_unfollow",
                kwargs={
                    "username": self.user_following.username,
                },
            )
        )
        after = Follow.objects.all().count()

        self.assertEqual(before - 1, after)

    def test_client_leave_comment(self):
        post = Post.objects.create(
            text="Text",
            author=self.user_following
        )
        self.client_auth_follower.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": self.user_following.username,
                    "post_id": post.id,
                },
            ),
            data={
                "text": "Comment",
            }
        )
        response = self.client.get(
            reverse(
                "post",
                kwargs={
                    "username": self.user_following.username,
                    "post_id": post.id,
                }
            )
        )
        self.assertContains(response, "Comment")

        self.client.post(
            reverse(
                "add_comment",
                kwargs={
                    "username": self.user_following.username,
                    "post_id": post.id,
                },
            ),
            data={
                "text": "Comment 2",
            }
        )
        response = self.client.get(
            reverse(
                "post",
                kwargs={
                    "username": self.user_following.username,
                    "post_id": post.id,
                }
            )
        )
        self.assertNotContains(response, "Comment 2")

    def test_subscribed_users_receive_authors_posts(self):
        self.client_auth_follower.get(
            reverse(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                },
            )
        )
        Post.objects.create(
            text="Text123",
            author=self.user_following
        )
        response = self.client_auth_follower.get(
            reverse("follow_index")
        )
        self.assertContains(response, "Text123")

        self.client.force_login(self.user)

        response = self.client.get(
            reverse("follow_index")
        )
        self.assertNotContains(response, "Text123")
