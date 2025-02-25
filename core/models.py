from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class HRProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} (HR)"

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} (Candidate)"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'hrprofile'):
        instance.hrprofile.save()
    elif hasattr(instance, 'candidateprofile'):
        instance.candidateprofile.save()

class Assessment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'hrprofile__isnull': False})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    QUESTION_TYPES = (
        ('MC', 'Multiple Choice'),
        ('SA', 'Short Answer'),
        ('TF', 'True/False'),
        ('UP', 'File Upload'),
        ('MA', 'Matching'),  # Add more as needed
    )
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default='MC')

    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class MatchPair(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='match_pairs')
    left_text = models.CharField(max_length=200)
    right_text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.left_text} -> {self.right_text}"

class Result(models.Model):
    assignment = models.OneToOneField('AssessmentAssignment', on_delete=models.CASCADE)
    score = models.FloatField(default=0)  # Percentage or raw score
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(default=dict)  # Store question answers

    def __str__(self):
        return f"Result for {self.assignment.candidate.user.username} - {self.assignment.assessment.title}"

class AssessmentAssignment(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.user.username} - {self.assessment.title}"