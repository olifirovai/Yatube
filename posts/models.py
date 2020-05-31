from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("title", max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField("description", max_length=250)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("post_text")
    pub_date = models.DateTimeField("date_published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="group_posts", blank=True,
                              null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return f"{self.author} {self.text[:20]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="post_comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="user_comment")
    text = models.TextField("comment_text")
    created = models.DateTimeField("date_comment", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
    created = models.DateTimeField("beginning_following_date",
                                   auto_now_add=True, db_index=True)

    def __str__(self):
        return f"follower - {self.user} following - {self.author}"
