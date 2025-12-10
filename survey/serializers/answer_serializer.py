# survey/serializers/answer_serializer.py
from rest_framework import serializers
from ..models import Answer

class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Answer
        fields = ['question_id', 'answer_text', 'answer_choice']
