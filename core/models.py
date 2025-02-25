from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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

class Assessment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='assessments/', null=True, blank=True)  # For image/icon
    open_date = models.DateTimeField(default=timezone.now)
    close_date = models.DateTimeField(null=True, blank=True)
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes", null=True, blank=True)
    grading_method = models.CharField(
        max_length=20,
        choices=[
            ('auto', 'Self-Corrected'),
            ('manual', 'Manual'),
            ('partial', 'Partially Corrected'),
        ],
        default='auto'
    )
    layout = models.CharField(
        max_length=20,
        choices=[
            ('all_one_page', 'All questions on one page'),
            ('each_question', 'Each question on a separate page'),
            ('all_sections', 'All sections on one page'),
            ('each_section', 'Each section on a separate page'),
        ],
        default='all_one_page'
    )
    navigation = models.CharField(
        max_length=10,
        choices=[
            ('free', 'Free'),
            ('sequential', 'Sequential'),
        ],
        default='free'
    )
    shuffle_questions = models.BooleanField(default=False)
    feedback = models.CharField(
        max_length=20,
        choices=[
            ('deferred', 'Deferred Feedback'),
            ('immediate_question', 'Immediate per Question'),
            ('immediate_section', 'Immediate per Section'),
            ('none', 'No Feedback'),
        ],
        default='deferred'
    )
    unanswered_prompt = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'hrprofile__isnull': False})

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
        ('MA', 'Matching'),
    )
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default='MC')
    points = models.PositiveIntegerField(default=1, help_text="Points for this question")

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