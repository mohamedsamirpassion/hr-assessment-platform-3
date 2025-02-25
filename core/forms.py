from django import forms
from .models import Assessment

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = '__all__'
        widgets = {
            'open_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'close_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'time_limit': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }