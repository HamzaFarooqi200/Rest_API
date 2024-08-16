from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .managers import UserManager


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=20, verbose_name="username", null=True, blank=True
    )
    email = models.EmailField(verbose_name="email", unique=True, null=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


def check_image(image):
    try:
        file_size = image.size
    except AttributeError:
        file_size = image.file.size
    limit = 2
    if file_size > limit * 1024 * 1024:
        raise ValidationError(f"The image should be less than {limit}mb")


def check_phone_number(number):
    if len(number) != 11:
        raise ValidationError("the number should be 11 digit")
    elif number[:2] != "03":
        raise ValidationError("number must start with 03!!!")


class Profile(models.Model):
    ROLE_CHOICES = [
        ("qa", "QA"),
        ("man", "MANAGER"),
        ("dev", "DEVELOPER"),
    ]
    profile_picture = models.ImageField(null=True, validators=[check_image])
    status = models.CharField(max_length=3, choices=ROLE_CHOICES)
    contact_number = models.CharField(max_length=11, validators=[check_phone_number])
    user = models.OneToOneField(
        CustomUser, related_name="user_profile", on_delete=models.CASCADE
    )


def check_end_date(date):
    today = timezone.now().date()
    if date < today:
        raise ValidationError("your start date must be end date from now or onwards")


class Project(models.Model):
    title = models.CharField(max_length=10)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(validators=[check_end_date])
    team_members = models.ManyToManyField(CustomUser, related_name="project_member")

    def __str__(self) -> str:
        return self.title

    @property
    def check_date(self):
        if not self.start_date < self.end_date:
            raise ValidationError("the end date must be greater than start date")

    def save(self):
        self.check_date
        return super().save()


class Task(models.Model):
    TASK_STATUS_CHOICES = [
        ("o", "OPEN"),
        ("r", "REVIEW"),
        ("w", "WORKING"),
        ("a", "AWAITING"),
        ("rl", "RELEASE"),
        ("wq", "WAITING QA"),
    ]
    title = models.CharField(max_length=10)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=TASK_STATUS_CHOICES)
    project = models.ForeignKey(
        Project, related_name="task_project", on_delete=models.CASCADE
    )
    assignee = models.OneToOneField(
        CustomUser, related_name="assigned_user", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.title


class Document(models.Model):
    name = models.CharField(max_length=10)
    description = models.TextField()
    file = models.FileField(verbose_name="file", null=True, blank=True)
    version = models.FloatField()
    project = models.ForeignKey(
        Project, related_name="document_project", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name


class Comment(models.Model):
    text = models.TextField()
    author = models.OneToOneField(
        CustomUser, related_name="comment_author", on_delete=models.DO_NOTHING
    )
    created_at = models.DateTimeField()
    task = models.ForeignKey(
        Task, related_name="task_comment", on_delete=models.DO_NOTHING
    )
    project = models.ForeignKey(
        Project, related_name="project_comment", on_delete=models.DO_NOTHING
    )

    def __str__(self) -> str:
        return str(self.author)


class RateLimit(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="rate_user", on_delete=models.CASCADE
    )
    login_time = models.DateTimeField(auto_now_add=True)
    req_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.user)