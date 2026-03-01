from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils import timezone


class Task(models.Model):
	name = models.CharField(
	    validators=[MinLengthValidator(5)],
	    max_length=64,
	    db_index=True,
	    verbose_name="Задача",
	    help_text="Назови задачу"
	)
	content = models.TextField(validators=[
	    MaxLengthValidator(1000),
	    MinLengthValidator(5)
	], verbose_name="Описание", help_text="Опиши", db_index=True)
	is_done = models.BooleanField(default=False, verbose_name="Статус задачи", db_index=True)
	done_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
	
	class Meta:
		verbose_name = "Задача"
		verbose_name_plural = "Задачи"
		ordering = ["-created_at"]
		indexes = [models.Index(fields=["name", "content", "is_done"])]
	
	def __str__(self):
		return f"<Task(id={self.id}, name={self.name})>"
	
	def done(self):
		self.is_done = True
		self.done_at = timezone.now()
		self.save(update_fields=["is_done", "done_at"])
	
	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)

