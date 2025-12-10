# survey/serializers/response_serializer.py
from rest_framework import serializers
from ..models import Response, Question
from .answer_serializer import AnswerSerializer

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)
    
    class Meta:
        model = Response
        fields = ['survey_id', 'answers', 'wechat_openid', 
                 'wechat_nickname', 'completion_time']
        read_only_fields = ['submit_time']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        
        for answer_data in answers_data:
            question_id = answer_data.pop('question_id')
            question = Question.objects.get(id=question_id)
            Answer.objects.create(
                response=response,
                question=question,
                **answer_data
            )
        
        return response
