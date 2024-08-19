from django.contrib import admin
from . import models

admin.site.register(models.CustomUser)
admin.site.register(models.Task)
admin.site.register(models.Project)
admin.site.register(models.Profile)
admin.site.register(models.Comment)
admin.site.register(models.Document)
admin.site.register(models.RateLimit)
admin.site.register(models.TimelineEvent)
admin.site.register(models.Notification)