from django.db import models
from user.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_user_project_title')
        ]

    def __str__(self):
        return self.title



class SiliconePerson(models.Model):
    id_str = models.CharField(max_length=100, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="silicone_people")
    name = models.CharField(max_length=100, blank=True, null=True)
    race = models.CharField(max_length=100, blank=True, null=True)
    discuss_politics = models.CharField(max_length=250, blank=True, null=True)
    ideology = models.CharField(max_length=100, blank=True, null=True)
    party = models.CharField(max_length=100, blank=True, null=True)
    church_goer = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    political_interest = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    financially = models.CharField(max_length=100, blank=True, null=True)
    patriotism = models.CharField(max_length=250, blank=True, null=True)
    more_info = models.JSONField(blank=True, null=True)
    real_vote = models.CharField(max_length=100, blank=True, null=True)
    dataset_name = models.CharField(max_length=100, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Silicone Person #{self.id}"



class Prompt(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="prompts")
    body = models.TextField()
    silicone_person = models.ForeignKey(SiliconePerson, on_delete=models.CASCADE, related_name="prompts", null=True, blank=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name="prompts", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prompt {self.id} for {self.project.title}"

class Cost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="costs")
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name="costs", null=True, blank=True)
    total_cost = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Question(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="questions")
    body = models.TextField(help_text="Content of the question")
    real_answer = models.TextField(blank=True, null=True)
    gpt_answer = models.BooleanField(default=False)
    is_analysed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Question {self.id} ({self.project.title})"



class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")
    silicone_person = models.ForeignKey(SiliconePerson, on_delete=models.CASCADE, related_name="responses")
    raw_response = models.TextField(help_text="Generated model response")
    structured_data = models.JSONField(blank=True, null=True, help_text="Parsed or scored data")
    confidence_score = models.FloatField(blank=True, null=True)
    gpt_model = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response #{self.id} (Person {self.silicone_person.id})(Model {self.gpt_model})"



class AnalysisResult(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="analysis_results")
    method = models.CharField(max_length=100, help_text="Analysis method (sentiment, correlation, etc.)", blank=True, null=True)
    parameters = models.JSONField(blank=True, null=True)
    result_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis ({self.method}) for {self.question.body}"



class ModelLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="model_logs")
    silicone_person = models.ForeignKey(SiliconePerson, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    prompt_text = models.TextField()
    response_text = models.TextField()
    model_name = models.CharField(max_length=100)
    tokens_used = models.IntegerField(blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ModelLog #{self.id} ({self.model_name})"
