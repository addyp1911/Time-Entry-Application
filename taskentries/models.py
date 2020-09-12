from django.db import models
from authentication.models import BaseModel, User


class Project(BaseModel):
    """
    ORM for Project interactions
    """

    project_name = models.CharField(max_length=1000, unique=True)
    

    # str function to return name instead of object
    def __str__(self):
        """Return full name in representation instead of project object"""
        return self.project_name

    class Meta:
        """A meta object for defining name of the project table"""
        db_table = "project"


class TimeEntry(BaseModel):
    """A ORM for user interactions"""
    
    timestamp = models.DateField(auto_now_add=True)
    task_start = models.DateTimeField(null=True)
    task_end = models.DateTimeField(null=True)
    logged_time = models.TimeField(null=True)
    is_active = models.BooleanField(default=False)
    pause_time = models.DateTimeField(null=True)

    class Meta:
        """A meta object for defining name of the task table"""
        db_table = "time_entry"


class TaskEntry(BaseModel):
    """A ORM for user interactions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tasks")
    name = models.CharField(max_length=1000, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, related_name="tasks", on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    time_entries = models.ManyToManyField(TimeEntry, blank=True, related_name="task")


    # str function to return name instead of object
    def __str__(self):
        """Return full name in representation instead of task object"""
        return self.name

    class Meta:
        """A meta object for defining name of the task table"""
        db_table = "task_entry"    


