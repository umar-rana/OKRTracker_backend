from django.contrib import admin
from .models import Objective, KeyResult, KeyResultHistory, RiskBlocker, Accomplishment, DecisionResource

@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'priority', 'status', 'owner', 'due_date')
    list_filter = ('organization', 'status', 'priority')

@admin.register(KeyResult)
class KeyResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'objective', 'current_value', 'target_value', 'rag_status', 'due_date')
    list_filter = ('objective__organization', 'rag_status')

@admin.register(KeyResultHistory)
class KeyResultHistoryAdmin(admin.ModelAdmin):
    list_display = ('key_result', 'new_value', 'new_rag_status', 'recorded_at', 'updated_by')

admin.site.register(RiskBlocker)
admin.site.register(Accomplishment)
admin.site.register(DecisionResource)
