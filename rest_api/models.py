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

    def save(self, *args, **kwargs):
        self.check_date
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            TimelineEvent.objects.create(
                event_type='project_created',
                description=f'Project "{self.title}" created.',
                project=self,
                user=self.team_members.first()  # Example: assigning first team member as the user
            )
        else:
            TimelineEvent.objects.create(
                event_type='project_updated',
                description=f'Project "{self.title}" updated.',
                project=self,
                user=self.team_members.first()  # Example: assigning first team member as the user
            )

    def delete(self, *args, **kwargs):
        TimelineEvent.objects.create(
            event_type='project_deleted',
            description=f'Project "{self.title}" deleted.',
            project=self,
            user=self.team_members.first()  # Example: assigning first team member as the user
        )
        super().delete(*args, **kwargs)


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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            TimelineEvent.objects.create(
                event_type='task_created',
                description=f'Task "{self.title}" created for project "{self.project.title}".',
                task=self,
                user=self.assignee
            )
        else:
            TimelineEvent.objects.create(
                event_type='task_updated',
                description=f'Task "{self.title}" updated for project "{self.project.title}".',
                task=self,
                user=self.assignee
            )

    def delete(self, *args, **kwargs):
        TimelineEvent.objects.create(
            event_type='task_deleted',
            description=f'Task "{self.title}" deleted from project "{self.project.title}".',
            task=self,
            user=self.assignee
        )
        super().delete(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            TimelineEvent.objects.create(
                event_type='document_uploaded',
                description=f'Document "{self.name}" uploaded for project "{self.project.title}".',
                document=self,
                user=self.project.team_members.first()
            )
        else:
            TimelineEvent.objects.create(
                event_type='document_updated',
                description=f'Document "{self.name}" updated for project "{self.project.title}".',
                document=self,
                user=self.project.team_members.first()
            )

    def delete(self, *args, **kwargs):
        TimelineEvent.objects.create(
            event_type='document_deleted',
            description=f'Document "{self.name}" deleted from project "{self.project.title}".',
            document=self,
            user=self.project.team_members.first()
        )
        super().delete(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            TimelineEvent.objects.create(
                event_type='comment_created',
                description=f'Comment by {self.author} on task "{self.task.title}" in project "{self.project.title}": {self.text}',
                comment=self,
                user=self.author
            )
        else:
            TimelineEvent.objects.create(
                event_type='comment_updated',
                description=f'Comment by {self.author} on task "{self.task.title}" in project "{self.project.title}" updated: {self.text}',
                comment=self,
                user=self.author
            )

    def delete(self, *args, **kwargs):
        TimelineEvent.objects.create(
            event_type='comment_deleted',
            description=f'Comment by {self.author} on task "{self.task.title}" in project "{self.project.title}" deleted.',
            comment=self,
            user=self.author
        )
        super().delete(*args, **kwargs)

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
    
class TimelineEvent(models.Model):
    EVENT_TYPES = [
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_deleted', 'Task Deleted'),
        ('document_uploaded', 'Document Uploaded'),
        ('document_updated', 'Document Updated'),
        ('document_deleted', 'Document Deleted'),
        ('comment_added', 'Comment Added'),
        ('comment_updated', 'Comment Updated'),
        ('comment_deleted', 'Comment Deleted'),
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('project_deleted', 'Project Deleted'),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='timeline_events', on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, related_name='timeline_events', on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey(Document, related_name='timeline_events', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, related_name='timeline_events', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(CustomUser, related_name='timeline_events', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - Read: {self.is_read}"