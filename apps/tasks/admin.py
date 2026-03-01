from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ["name", "created_at"]
	list_filter = ["is_done", "created_at", "updated_at"]
	search_fields = ["name", "content", "is_done"]
	readonly_fields = ["done_at", "created_at", "updated_at"]
	
	fieldsets = (
	    ("Основная информация", {
	        "fields": ("name", "content", "is_done")
	    }),
	    ("Временные метки", {
	        "fields": ("done_at", "created_at", "updated_at",),
	        "classes": ("collapse",)
	    })
	)
