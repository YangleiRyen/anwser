# survey/serializers.py
from rest_framework import serializers
from .models import Survey, Question, Response, Answer, QRCode

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'is_required', 'options']

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

class AnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Answer
        fields = ['question_id', 'answer_text', 'answer_choice']

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

class QRCodeSerializer(serializers.ModelSerializer):
    survey_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = QRCode
        fields = ['id', 'name', 'short_code', 'scan_count', 
                 'created_at', 'survey_url', 'qr_code_url']
    
    def get_survey_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/survey/{obj.survey.id}/')
    
    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/qrcode/{obj.short_code}/image/')