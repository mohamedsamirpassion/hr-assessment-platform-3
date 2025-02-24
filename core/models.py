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

# Automatically create profiles when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # We'll decide HR or Candidate during signup, not here
        pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'hrprofile'):
        instance.hrprofile.save()
    elif hasattr(instance, 'candidateprofile'):
        instance.candidateprofile.save()