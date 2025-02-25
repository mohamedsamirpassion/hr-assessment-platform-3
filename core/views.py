from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import HRProfile, CandidateProfile
from .models import Assessment, Question, Choice
from django.contrib.auth.decorators import login_required
from .models import CandidateProfile
from .models import Assessment, CandidateProfile
from .models import AssessmentAssignment
from .models import Assessment, CandidateProfile, AssessmentAssignment

@login_required
def assign_assessment(request, candidate_id):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can assign assessments.")
        return redirect('home')
    
    candidate = CandidateProfile.objects.get(id=candidate_id)
    assessments = Assessment.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        assessment_id = request.POST['assessment']
        assessment = Assessment.objects.get(id=assessment_id)
        AssessmentAssignment.objects.get_or_create(
            assessment=assessment,
            candidate=candidate
        )
        messages.success(request, f"Assessment '{assessment.title}' assigned to {candidate.user.username}.")
        return redirect('view_candidates')
    
    return render(request, 'assign_assessment.html', {'candidate': candidate, 'assessments': assessments})

@login_required
def statistics(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view statistics.")
        return redirect('home')
    
    total_assessments = Assessment.objects.filter(created_by=request.user).count()
    total_candidates = CandidateProfile.objects.count()
    # For now, we'll assume tests taken are tied to assessments (we'll refine this later)
    tests_taken = AssessmentAssignment.objects.filter(
        assessment__created_by=request.user,
        completed=True
    ).count()
    tests_never_taken = AssessmentAssignment.objects.filter(
        assessment__created_by=request.user,
        completed=False
    ).count()

    context = {
        'total_assessments': total_assessments,
        'total_candidates': total_candidates,
        'tests_taken': tests_taken,
        'tests_never_taken': tests_never_taken,
    }
    return render(request, 'statistics.html', context)

@login_required
def view_candidates(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view candidates.")
        return redirect('home')
    
    candidates = CandidateProfile.objects.all()
    return render(request, 'view_candidates.html', {'candidates': candidates})

@login_required
def create_assessment(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can create assessments.")
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        question_text = request.POST['question_text']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        correct_choice = request.POST['correct_choice']
        
        assessment = Assessment.objects.create(
            title=title,
            description=description,
            created_by=request.user
        )
        question = Question.objects.create(
            assessment=assessment,
            text=question_text,
            question_type='MC'
        )
        Choice.objects.create(question=question, text=choice1, is_correct=(correct_choice == '1'))
        Choice.objects.create(question=question, text=choice2, is_correct=(correct_choice == '2'))
        Choice.objects.create(question=question, text=choice3, is_correct=(correct_choice == '3'))
        
        messages.success(request, "Assessment created successfully!")
        return redirect('view_assessments')
    
    return render(request, 'create_assessment.html')

@login_required
def view_assessments(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view assessments.")
        return redirect('home')
    
    assessments = Assessment.objects.filter(created_by=request.user)
    return render(request, 'view_assessments.html', {'assessments': assessments})


def home(request):
    return render(request, 'home.html')

def hr_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        company_name = request.POST['company_name']
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken.")
            return render(request, 'hr_signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        HRProfile.objects.create(user=user, company_name=company_name)
        user.save()
        login(request, user)
        return redirect('hr_dashboard')  # Placeholder for now
    
    return render(request, 'hr_signup.html')

def hr_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and hasattr(user, 'hrprofile'):
            login(request, user)
            return redirect('hr_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an HR account.")
            return render(request, 'hr_login.html')
    
    return render(request, 'hr_login.html')

def candidate_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken.")
            return render(request, 'candidate_signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        CandidateProfile.objects.create(user=user, full_name=full_name)
        user.save()
        login(request, user)
        return redirect('candidate_dashboard')  # Placeholder for now
    
    return render(request, 'candidate_signup.html')

def candidate_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and hasattr(user, 'candidateprofile'):
            login(request, user)
            return redirect('candidate_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a Candidate account.")
            return render(request, 'candidate_login.html')
    
    return render(request, 'candidate_login.html')

# Temporary dashboards
def hr_dashboard(request):
    return render(request, 'hr_dashboard.html')

@login_required
def candidate_dashboard(request):
    if not hasattr(request.user, 'candidateprofile'):
        messages.error(request, "Only Candidate users can access this page.")
        return redirect('home')
    
    assignments = AssessmentAssignment.objects.filter(candidate=request.user.candidateprofile, completed=False)
    return render(request, 'candidate_dashboard.html', {'assignments': assignments})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def take_assessment(request, assignment_id):
    if not hasattr(request.user, 'candidateprofile'):
        messages.error(request, "Only Candidate users can take assessments.")
        return redirect('home')
    
    assignment = AssessmentAssignment.objects.get(id=assignment_id, candidate=request.user.candidateprofile)
    questions = assignment.assessment.questions.all()
    
    if request.method == 'POST':
        # Simple scoring for now (expand later)
        score = 0
        for question in questions:
            if question.question_type == 'MC':
                selected_choice = request.POST.get(f'question_{question.id}')
                if selected_choice:
                    choice = Choice.objects.get(id=selected_choice)
                    if choice.is_correct:
                        score += 1
        # Mark as completed and store results (placeholder for now)
        assignment.completed = True
        assignment.save()
        messages.success(request, f"Assessment completed! Your score: {score}/{questions.count()}")
        return redirect('candidate_dashboard')
    
    return render(request, 'take_assessment.html', {'assignment': assignment, 'questions': questions})