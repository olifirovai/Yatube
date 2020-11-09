from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("title", max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField("description", max_length=250)

    def __str__(self):
        return self.title


class PostManager(models.Manager):
    def get_followed_authors(self, user, author):
        return self.get_queryset().get(user=user, author=author)

    def get_following_posts(self, user):
        return self.get_queryset().filter(author__following__user=user)


class Post(models.Model):
    text = models.TextField("post_text")
    pub_date = models.DateTimeField("date_published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="group_posts", blank=True,
                              null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    objects = PostManager()

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.author} {self.text[:20]}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="post_comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="user_comment")
    text = models.TextField("comment_text")
    created = models.DateTimeField("date_comment", auto_now_add=True)

    class Meta:
        ordering = ("-created",)


class FollowManager(models.Manager):
    def get_follow(self, author, user):
        return self.get_queryset().filter(author=author, user=user)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
    created = models.DateTimeField("beginning_following_date",
                                   auto_now_add=True, db_index=True)
    objects = FollowManager()

    def __str__(self):
        return f"follower - {self.user} following - {self.author} date - {self.created}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="liker")
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="liked_post")
    created = models.DateTimeField("like_date",
                                   auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"liker - {self.user} liked post - {self.post} like's date - {self.created}"
