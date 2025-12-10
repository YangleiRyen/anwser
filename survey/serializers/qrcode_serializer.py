# survey/serializers/qrcode_serializer.py
from rest_framework import serializers
from ..models import QRCode

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
