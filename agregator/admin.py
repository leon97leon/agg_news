from django.contrib import admin
from .models import Files

admin.site.register(Files)
# Register your models here.
from .models import BaseWord, BaseParsingResult


@admin.register(BaseWord)
class BaseWordAdmin(admin.ModelAdmin):
    list_display = ['user','id', 'type','file','file_state']
    readonly_fields = ['created_at']
    list_filter = ['created_at']

@admin.register(BaseParsingResult)
class BaseResultAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'task_id', 'result_text']
    readonly_fields = ['created_at','updated_at']