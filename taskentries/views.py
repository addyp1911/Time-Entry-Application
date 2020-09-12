#django imports
import datetime, pytz
from django.shortcuts import render
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse

#rest_framework imports
from rest_framework import status, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

#project imports
from .serializers import *
from .models import *
from base.utils import *
from authentication.constants import *
from base.viewsets import BaseAPIViewSet
from .exceptions import * 
from .utils import *


# CRUD API for projects
class ProjectAction(BaseAPIViewSet):
    serializer_class = ProjectSerializer
    model_class = Project
    instance_name = 'project'
    search_fields = ['project_name']
    filter_backends = (filters.SearchFilter,)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        return Project.objects.all().order_by("-created_at")


    def list(self, request, *args, **kwargs):
        pagenumber = request.GET.get('page', 1)
        filtered_qs = self.filter_queryset(self.get_queryset()).order_by("-created_at")
        paginator = Paginator(filtered_qs, 10)

        project_qs = paginator.page(pagenumber).object_list
        response = list(project_qs.values('uid','project_name'))

        return JsonResponse(paginate(response, paginator, pagenumber), safe=False)


    def create(self, request, *args, **kwargs):
        if not Project.objects.filter(project_name=request.data.get("project_name")).exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(responsedata(True, "New project entry created", serializer.data), status=status.HTTP_200_OK)
        else:
            return Response(responsedata(False, "Project already exists"), status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk, *args, **kwargs):
        if Project.objects.filter(uid=pk).exists():
            project_instance = Project.objects.get(uid=pk)
            serializer = self.get_serializer(project_instance, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(responsedata(True, "Project entry updated", serializer.data), status=status.HTTP_200_OK)
        else:
            return Response(responsedata(False, "No project is present corresponding to the id"), status=status.HTTP_400_BAD_REQUEST)  


    def destroy(self, request, pk):
        try:
            # Checking Authorization
            if Project.objects.filter(uid=pk).exists():
                Project.objects.get(uid=pk).delete()
                return Response(responsedata(True, "Project successfully deleted"), \
                                    status=status.HTTP_200_OK)
            else:
                return Response(responsedata(False, "No project exists corresponding to this id"),\
                                                status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)              


# CRUD API for Tasks
class TaskAction(BaseAPIViewSet):
    serializer_class = TaskSerializer
    model_class = TaskEntry
    instance_name = 'task'
    search_fields = ['name', 'project__name']
    filter_backends = (filters.SearchFilter,)
    queryset = TaskEntry.objects.all().order_by("-created_at")


    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


    def validate_data(self, data, pk=None):
        
        if pk and not TaskEntry.objects.filter(uid=pk).exists():
            raise ValidationError("No task exists corresponding to this id for the user")

        if data.get("project") and not Project.objects.filter(uid=data.get("project")).exists():
            raise ValidationError("Project is invalid or deleted")

        if data.get("start_time") or data.get("end_time"):
            try:
                start_time = datetime.datetime.strptime(data["start_time"], '%H:%M:%S').time() \
                        if data.get("start_time") else None

                end_time = datetime.datetime.strptime(data["end_time"], '%H:%M:%S').time() if \
                    data.get("end_time") else None    
            except:
                raise ValidationError("Invalid time inputs")

            if start_time <= end_time:
                raise InvalidTime("Start and end timings are invalid!")

            data["start_time"] = start_time
            data["end_time"] = end_time


    def list(self, request, *args, **kwargs):
        """
        List all the tasks
        """

        queryset = self.filter_queryset(self.get_queryset()).filter(user=request.user)
        pagenumber = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)

        task_qs = paginator.page(pagenumber).object_list
        response = list(task_qs.values('uid', 'name', 'project__project_name', 'start_time', 'end_time'))

        # Paginated response
        return JsonResponse(paginate(response, paginator, pagenumber), safe=False)


    def create(self, request):
        try:
            data = request.data.copy()
            user_data = UserShowSerializer(request.user).data    

            self.validate_data(data)
            task_serializer = self.get_serializer(data=data)

            with transaction.atomic():
                if task_serializer.is_valid(raise_exception=True):
                    task_entry = task_serializer.save(user=request.user)

                    res_data = task_serializer.data
                    res_data.update(user=user_data, project=task_entry.project.project_name)

            return Response(responsedata(True, "Task entry is created for the user", res_data), \
                            status=status.HTTP_201_CREATED)

        except (ValidationError, InvalidTime) as e:
            return Response(responsedata(False, str(e)),status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        try:
            user_data = UserShowSerializer(request.user).data

            task_info = request.data.copy()
            self.validate_data(task_info, pk)

            task_instance = TaskEntry.objects.get(uid=pk)
            task_serializer = self.get_serializer(task_instance, data=task_info, partial=True)

            with transaction.atomic():
                if task_serializer.is_valid(raise_exception=True):
                    task_entry = task_serializer.save(user=request.user)

                    res_data = task_serializer.data
                    res_data.update(user=user_data, project=task_entry.project.project_name)

                    return Response(responsedata(True, "Task entry updated for the user", res_data), \
                                    status=status.HTTP_200_OK)

        except (ValidationError, InvalidTime) as e:
            return Response(responsedata(False, str(e)),status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk):
        try:
            self.validate_data(request.data)
            if TaskEntry.objects.filter(uid=pk, user=request.user).exists():
                TaskEntry.objects.get(uid=pk).delete()
                return Response(responsedata(True, "Task entry successfully deleted"), \
                                    status=status.HTTP_200_OK)
            else:
                return Response(responsedata(False, "Task id invalid for the user"), \
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)    


    def retrieve(self, request, pk, *args, **kwargs):
        """
        List all the time entries for a task
        """
        queryset = TimeEntry.objects.filter(task__uid=pk, task__user=request.user).order_by("-created_at")
        pagenumber = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)

        time_entry_qs = paginator.page(pagenumber).object_list
        response = list(time_entry_qs.values('timestamp', 'task_start', 'task_end', 'logged_time', 'is_active','task__name'))

        # Paginated response
        return JsonResponse(paginate(response, paginator, pagenumber), safe=False)


# CRUD api for time entries for a task
class TimeEntryAction(BaseAPIViewSet):
    serializer_class = TimeEntrySerializer
    model_class = TimeEntry
    instance_name = 'time-entry'
    serializer_class = TimeEntrySerializer
    queryset = TimeEntry.objects.all().order_by("-created_at")

    def list(self, request, *args, **kwargs):
        """
        List all the time entries
        """

        queryset = self.filter_queryset(self.get_queryset()).filter(task__user=request.user)
        pagenumber = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10)

        time_entry_qs = paginator.page(pagenumber).object_list
        response = list(time_entry_qs.values('timestamp', 'task_start', 'task_end', 'logged_time', 'is_active', 'task__name'))

        # Paginated response
        return JsonResponse(paginate(response, paginator, pagenumber), safe=False)


    @action(detail=False, methods=['post'])
    def start_task(self, request):

        try:
            data = request.data
            if not TaskEntry.objects.filter(uid=data.get("task_id"), user=request.user).exists():
                raise ValidationError("No task exists corresponding to this id for the user")
            else:
                task = TaskEntry.objects.get(uid=data.get("task_id"))

            if task.time_entries.filter(is_active=True).exists():
                raise TimerError("The timer is already on for this task")

            current_time_obj = fetch_current_time()
            data = {"timestamp": current_time_obj.date(), "is_active":True, "task_start": current_time_obj}

            time_entry_serializer = self.get_serializer(data=data)
            with transaction.atomic():
                if time_entry_serializer.is_valid(raise_exception=True):
                    time_entry = time_entry_serializer.save()
                    task.time_entries.add(time_entry)

            return Response(responsedata(True, "Timer started for the task"), \
                            status=status.HTTP_200_OK)

        except (TimerError, ValidationError) as e:
            return Response(responsedata(False, str(e)),status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def stop_task(self, request):
        try:
            data = request.data
            if not TaskEntry.objects.filter(uid=data.get("task_id"), user=request.user).exists():
                raise ValidationError("No task exists corresponding to this id for the user")
            else:
                task = TaskEntry.objects.get(uid=data.get("task_id"))

            if not task.time_entries.filter(is_active=True).exists():
                raise TimerError("No timer is on for this task")
            else:
                time_entry = task.time_entries.filter(is_active=True).first()
                current_time_obj = fetch_current_time()

                time_tracked = convert_time_format(current_time_obj, time_entry)
                data = {"task_end": current_time_obj, "is_active":False, "logged_time": time_tracked}

                time_entry_serializer = self.get_serializer(time_entry, data=data)
                with transaction.atomic():
                    if time_entry_serializer.is_valid(raise_exception=True):
                        time_entry = time_entry_serializer.save()
                        res_data = {"start_time":time_entry.task_start, "end_time":time_entry.task_end, "logged_time":time_tracked}
                        return Response(responsedata(True, "Timer stopped for the task", res_data), \
                                        status=status.HTTP_200_OK)

        except (TimerError, ValidationError) as e:
            return Response(responsedata(False, str(e)),status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(responsedata(False, GENERIC_ERR),status=status.HTTP_400_BAD_REQUEST)
