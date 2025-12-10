# survey/serializers/survey_serializer.py
from rest_framework import serializers
from ..models import Survey
from .question_serializer import QuestionSerializer

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'created_at', 
                 'questions', 'response_count', 'is_active',
                 'start_date', 'end_date']
    
    def get_response_count(self, obj):
        return obj.responses.count()
