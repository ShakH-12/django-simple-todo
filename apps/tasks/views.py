from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Task
from .serializers import TaskSerializer, CreateTaskSerializer, UpdateTaskSerializer


class CreateListTaskView(generics.ListCreateAPIView):
	queryset = Task.objects.all()
	
	def get_serializer_class(self):
		if self.request.method == "POST":
			return CreateTaskSerializer
		return TaskSerializer


class TaskDetailView(generics.RetrieveUpdateAPIView):
	queryset = Task.objects.all()
	
	def get_serializer_class(self):
		if self.request.method in ["PUT", "PATCH"]:
			return UpdateTaskSerializer
		return TaskSerializer
	
	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer_class = self.get_serializer_class()
		serializer = serializer_class(instance, data=request.data, partial=True)
		
		if serializer.is_valid():
			self.perform_update(serializer)
			if self.request.data.get("is_done"):
				instance.done()
			return Response(serializer.data)
		return Response(serializer.errors, status=400)


