# survey/models/answer.py
from django.db import models
from django.core.exceptions import ValidationError


class Answer(models.Model):
    """单个问题的回答"""
    response = models.ForeignKey(
        'Response',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="所属回答",
        db_index=True
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="问题",
        db_index=True
    )
    answer_text = models.TextField(
        blank=True,
        verbose_name="回答文本",
        help_text="用于文本题的回答"
    )
    answer_choice = models.JSONField(
        default=list,
        blank=True,
        verbose_name="选择答案",
        help_text="用于选择题的回答（JSON格式）"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="回答时间")
    
    class Meta:
        verbose_name = "答案"
        verbose_name_plural = "答案"
        ordering = ['response', 'question__survey_questions__order']
        unique_together = ('response', 'question')
        indexes = [
            models.Index(fields=['response', 'question']),
        ]
    
    def __str__(self):
        answer_display = self.get_answer_display()
        return f"{self.question.text[:30]}: {answer_display[:30]}"
    
    def get_answer_display(self):
        """获取答案的显示文本"""
        if self.answer_text:
            return self.answer_text
        
        if self.answer_choice:
            # 处理选择题答案
            if self.question.is_choice_question:
                choices = self.answer_choice if isinstance(self.answer_choice, list) else [self.answer_choice]
                labels = [self.question.get_option_label(choice) for choice in choices]
                return ', '.join(labels)
            return str(self.answer_choice)
        
        return "未回答"
    
    def clean(self):
        """数据验证"""
        if not self.answer_text and not self.answer_choice:
            raise ValidationError("必须提供答案文本或选择答案")
        
        # 验证选择题答案是否在选项范围内
        if self.question.is_choice_question and self.answer_choice:
            valid_values = set(self.question.options.values_list('value', flat=True))
            choices = self.answer_choice if isinstance(self.answer_choice, list) else [self.answer_choice]
            
            for choice in choices:
                if choice not in valid_values:
                    raise ValidationError(f"选项 '{choice}' 不在有效选项范围内")
    
    def save(self, *args, **kwargs):
        """保存前进行数据清理和验证"""
        self.clean()
        super().save(*args, **kwargs)
