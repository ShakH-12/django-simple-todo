from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = Task
		fields = ["id", "name", "content", "is_done", "done_at", "created_at", "updated_at"]
		read_only_fields = ["done_at", "created_at", "updated_at"]
		
	def validate_name(self, value):
		if not value.strip():
			raise serializers.ValidationError("Название не может быть пустым")
		return value.strip()
	
	def validate_content(self, value):
		if not value.strip():
			raise serializers.ValidationError("Описание не может быть пустым")
		return value.strip()


class CreateTaskSerializer(TaskSerializer):
	pass


class UpdateTaskSerializer(TaskSerializer):
	name = serializers.CharField(required=False)
	content = serializers.CharField(required=False)


