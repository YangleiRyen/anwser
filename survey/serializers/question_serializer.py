# survey/serializers/question_serializer.py
from rest_framework import serializers
from ..models import Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'is_required', 'options']
