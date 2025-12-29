from rest_framework import serializers
from .models import Project, SiliconePerson, Question
from .utils import MODEL_PRICING
import json

class CreateProjectSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class SingleSiliconPersonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    skin_color = serializers.CharField(max_length=50, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=50, required=False, allow_blank=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    race = serializers.CharField(max_length=100, required=False, allow_blank=True)
    religion = serializers.CharField(max_length=100, required=False, allow_blank=True)
    education = serializers.CharField(max_length=100, required=False, allow_blank=True)
    financially = serializers.CharField(max_length=100, required=False, allow_blank=True)
    ideological = serializers.CharField(max_length=100, required=False, allow_blank=True)
    political_orientation = serializers.CharField(max_length=100, required=False, allow_blank=True)
    more_info = serializers.CharField(required=False, allow_blank=True)
    conditioning_text = serializers.CharField(required=False, allow_blank=True)


class CreateSiliconPersonsSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    siliconpersons = SingleSiliconPersonSerializer(many=True)

class SiliconPersonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiliconePerson
        fields = '__all__'

class CreateQuestionSerializer(serializers.Serializer):
    # id = serializers.IntegerField(required=False)
    project_id = serializers.IntegerField()
    body = serializers.CharField(allow_blank=True)
    real_answer = serializers.CharField(allow_blank=True, required=False)
    model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'



class SiliconPersonCSVUploadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    silicon_persons = serializers.FileField()

class QuestionsCSVUploadSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    questions = serializers.FileField()


class TokenCostSerializer(serializers.Serializer):
    """
    Validates input for token cost estimation based on:
    1. Number of people (Multiplier)
    2. List of questions (Manual List OR File upload)
    """
    model_name = serializers.ChoiceField(choices=[(k, k) for k in MODEL_PRICING.keys()])
    
    num_silicon_people = serializers.IntegerField(
        min_value=1, 
        help_text="The total number of silicon people to simulate."
    )
    
    # Question Sources (Mutually Exclusive)
    questions_list = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        allow_null=True,
        help_text="List of questions entered manually."
    )
    questions_file = serializers.FileField(
        required=False, 
        allow_null=True,
        help_text="File containing questions. Supported formats: .csv, .xls, .xlsx."
    )

    def validate(self, attrs):
        """Ensure exactly one question source is provided."""
        has_list = bool(attrs.get('questions_list'))
        has_file = bool(attrs.get('questions_file'))
        
        if has_list == has_file: # Both True or Both False
            raise serializers.ValidationError(
                "Provide exactly one source for questions: 'questions_list' OR 'questions_file'."
            )
        return attrs