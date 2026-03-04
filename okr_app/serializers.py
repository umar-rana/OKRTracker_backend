from rest_framework import serializers
from users_app.serializers import UserSerializer
from .models import Objective, KeyResult, KeyResultHistory, RiskBlocker, Accomplishment, DecisionResource, Notification, AuditLog

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_details = UserSerializer(source='performed_by', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'performed_at']

class KeyResultSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    
    class Meta:
        model = KeyResult
        fields = [
            'id', 'objective', 'title', 'description', 'kr_type',
            'start_value', 'target_value', 'current_value', 'unit',
            'owner', 'owner_details', 'co_owner', 'priority', 'rag_status',
            'due_date', 'key_activity', 'metric', 'notes',
            'related_files_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ObjectiveSerializer(serializers.ModelSerializer):
    key_results = KeyResultSerializer(many=True, read_only=True)
    owner_details = UserSerializer(source='owner', read_only=True)
    
    class Meta:
        model = Objective
        fields = [
            'id', 'organization', 'team', 'title', 'description', 
            'priority', 'status', 'owner', 'owner_details', 
            'due_date', 'rejection_reason', 'key_results', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class KeyResultHistorySerializer(serializers.ModelSerializer):
    updated_by_details = UserSerializer(source='updated_by', read_only=True)
    
    class Meta:
        model = KeyResultHistory
        fields = [
            'id', 'key_result', 'previous_value', 'new_value', 
            'previous_rag_status', 'new_rag_status', 'updated_by', 
            'updated_by_details', 'note', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']

class RiskBlockerSerializer(serializers.ModelSerializer):
    owner_details = UserSerializer(source='owner', read_only=True)
    logged_by_details = UserSerializer(source='logged_by', read_only=True)
    
    class Meta:
        model = RiskBlocker
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class AccomplishmentSerializer(serializers.ModelSerializer):
    logged_by_details = UserSerializer(source='logged_by', read_only=True)
    
    class Meta:
        model = Accomplishment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DecisionResourceSerializer(serializers.ModelSerializer):
    requested_by_details = UserSerializer(source='requested_by', read_only=True)
    decision_owner_details = UserSerializer(source='decision_owner', read_only=True)
    
    class Meta:
        model = DecisionResource
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
