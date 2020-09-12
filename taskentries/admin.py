from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TaskEntry)
admin.site.register(Project)
admin.site.register(TimeEntry)