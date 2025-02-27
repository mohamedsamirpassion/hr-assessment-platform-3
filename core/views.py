from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assessment, Question, Choice, MatchPair, HRProfile, CandidateProfile, Result, AssessmentAssignment, Section
from .forms import AssessmentForm  # Ensure this import exists

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
        return redirect('core:hr_dashboard')
    
    return render(request, 'hr_signup.html')

def hr_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and hasattr(user, 'hrprofile'):
            login(request, user)
            return redirect('core:hr_dashboard')
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
        return redirect('core:candidate_dashboard')
    
    return render(request, 'candidate_signup.html')

def candidate_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and hasattr(user, 'candidateprofile'):
            login(request, user)
            return redirect('core:candidate_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a Candidate account.")
            return render(request, 'candidate_login.html')
    
    return render(request, 'candidate_login.html')

@login_required
def hr_dashboard(request):
    return render(request, 'hr_dashboard.html')

@login_required
def candidate_dashboard(request):
    if not hasattr(request.user, 'candidateprofile'):
        messages.error(request, "Only Candidate users can access this page.")
        return redirect('core:home')
    
    assignments = AssessmentAssignment.objects.filter(candidate=request.user.candidateprofile, completed=False)
    return render(request, 'candidate_dashboard.html', {'assignments': assignments})

@login_required
def create_assessment(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can create assessments.")
        return redirect('core:home')
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST, request.FILES)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            messages.success(request, "Assessment created successfully!")
            return redirect('core:view_assessments')
    else:
        form = AssessmentForm()
    return render(request, 'create_assessment.html', {'form': form})

@login_required
def view_assessments(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view assessments.")
        return redirect('core:home')
    
    assessments = Assessment.objects.filter(created_by=request.user)
    return render(request, 'view_assessments.html', {'assessments': assessments})

@login_required
def edit_assessment(request, assessment_id):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can edit assessments.")
        return redirect('core:home')
    
    assessment = get_object_or_404(Assessment, id=assessment_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AssessmentForm(request.POST, request.FILES, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assessment updated successfully!")
            return redirect('core:view_assessments')
    else:
        form = AssessmentForm(instance=assessment)
    return render(request, 'edit_assessment.html', {'form': form})

@login_required
def delete_assessment(request, assessment_id):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can delete assessments.")
        return redirect('core:home')
    
    assessment = get_object_or_404(Assessment, id=assessment_id, created_by=request.user)
    if request.method == 'POST':
        assessment.delete()
        messages.success(request, "Assessment deleted successfully!")
        return redirect('core:view_assessments')
    return render(request, 'confirm_delete_assessment.html', {'assessment': assessment})

@login_required
def view_candidates(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view candidates.")
        return redirect('core:home')
    
    candidates = CandidateProfile.objects.all()
    return render(request, 'view_candidates.html', {'candidates': candidates})

@login_required
def assign_assessment(request, candidate_id):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can assign assessments.")
        return redirect('core:home')
    
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
        return redirect('core:view_candidates')
    
    return render(request, 'assign_assessment.html', {'candidate': candidate, 'assessments': assessments})

@login_required
def statistics(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view statistics.")
        return redirect('core:home')
    
    total_assessments = Assessment.objects.filter(created_by=request.user).count()
    total_candidates = CandidateProfile.objects.count()
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
def view_results(request):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can view results.")
        return redirect('core:home')
    
    results = Result.objects.filter(
        assignment__assessment__created_by=request.user
    ).select_related('assignment__assessment', 'assignment__candidate__user')
    
    return render(request, 'view_results.html', {'results': results})

@login_required
def take_assessment(request, assignment_id, section_id=None, question_id=None):
    if not hasattr(request.user, 'candidateprofile'):
        messages.error(request, "Only Candidate users can take assessments.")
        return redirect('core:home')
    
    assignment = get_object_or_404(AssessmentAssignment, id=assignment_id, candidate=request.user.candidateprofile)
    assessment = assignment.assessment
    questions = assessment.questions.all().order_by('section__order', 'id')  # Order by section and question ID
    
    # Handle layout and navigation settings
    layout = assessment.layout
    navigation = assessment.navigation
    time_limit = assessment.time_limit

    # Initialize or retrieve answers from session
    if 'answers' not in request.session:
        request.session['answers'] = {}

    if request.method == 'POST':
        # Final assessment submission
        answers = request.session.get('answers', {})
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            if str(question.id) in request.POST and question.id in answers:
                answer = request.POST.get(f'question_{question.id}')
                if answer:
                    answers[question.id] = answer  # Update answer in session
                    if question.is_auto_graded:
                        if question.question_type == 'MC':
                            try:
                                choice = Choice.objects.get(id=answer)
                                if choice.is_correct:
                                    score += question.points
                            except Choice.DoesNotExist:
                                pass
                        elif question.question_type == 'TF':
                            if answer.lower() == 'true' or answer.lower() == 'false':
                                choice = Choice.objects.get(question=question, text__iexact=answer)
                                if choice.is_correct:
                                    score += question.points
                        elif question.question_type == 'MA':
                            user_pairs = {}
                            for pair in question.match_pairs.all():
                                user_answer = request.POST.get(f'question_{question.id}_pair_{pair.id}')
                                if user_answer:
                                    user_pairs[pair.id] = user_answer
                            answers[question.id] = user_pairs
                            correct_pairs = {pair.id: pair.right_text for pair in question.match_pairs.all()}
                            if all(user_pairs.get(pair_id) == correct_pairs[pair_id] for pair_id in correct_pairs):
                                score += question.points
                elif question.question_type == 'SA' or question.question_type == 'UP':
                    answer = request.POST.get(f'question_{question.id}')
                    if answer:
                        answers[question.id] = answer  # Store SA/UP answers
            request.session['answers'] = answers  # Update session
            request.session.modified = True  # Ensure session is updated

        if 'final_submit' in request.POST:  # Check for final submission
            percentage_score = (score / (total_questions * max([q.points for q in questions], default=1))) * 100 if total_questions > 0 else 0
            
            Result.objects.create(
                assignment=assignment,
                score=percentage_score,
                answers=answers
            )
            del request.session['answers']  # Clear session after submission
            assignment.completed = True
            assignment.save()
            messages.success(request, f"Assessment completed! Your score: {score}/{total_questions * max([q.points for q in questions], default=1)} ({percentage_score:.2f}%)")
            return redirect('core:candidate_dashboard')
        
        # Re-render the page with updated answers
        context = {
            'assignment': assignment,
            'questions': questions,
            'sections': assessment.sections.all().order_by('order'),
            'time_limit': time_limit,
            'layout': layout,
            'navigation': navigation
        }
        return render(request, 'take_assessment.html', context)
    
    # Determine which questions/sections to display based on layout
    sections = assessment.sections.all().order_by('order')
    if layout in ['all_one_page', 'all_sections']:
        # Show all questions or sections on one page
        context = {
            'assignment': assignment,
            'questions': questions,
            'sections': sections,
            'time_limit': time_limit,
            'layout': layout,
            'navigation': navigation
        }
        return render(request, 'take_assessment.html', context)
    elif layout in ['each_question', 'each_section']:
        # Handle pagination or separate pages
        if layout == 'each_question':
            if question_id:
                question = get_object_or_404(Question, id=question_id, assessment=assessment)
                context = {
                    'assignment': assignment,
                    'question': question,
                    'time_limit': time_limit,
                    'layout': layout,
                    'navigation': navigation
                }
                return render(request, 'take_assessment_question.html', context)
            else:
                # Redirect to the first question
                first_question = questions.first()
                if first_question:
                    return redirect('core:take_assessment_question', assignment_id=assignment_id, question_id=first_question.id)
                else:
                    messages.error(request, "No questions available for this assessment.")
                    return redirect('core:candidate_dashboard')
        elif layout == 'each_section':
            if section_id:
                section = get_object_or_404(Section, id=section_id, assessment=assessment)
                section_questions = section.questions.all()
                context = {
                    'assignment': assignment,
                    'section': section,
                    'questions': section_questions,
                    'time_limit': time_limit,
                    'layout': layout,
                    'navigation': navigation
                }
                return render(request, 'take_assessment_section.html', context)
            else:
                # Redirect to the first section
                first_section = sections.first()
                if first_section:
                    return redirect('core:take_assessment_section', assignment_id=assignment_id, section_id=first_section.id)
                else:
                    messages.error(request, "No sections available for this assessment.")
                    return redirect('core:candidate_dashboard')

    # Default to all questions on one page if layout is invalid
    context = {
        'assignment': assignment,
        'questions': questions,
        'sections': sections,
        'time_limit': time_limit,
        'layout': layout,
        'navigation': navigation
    }
    return render(request, 'take_assessment.html', context)


@login_required
def create_question(request, assessment_id):
    if not hasattr(request.user, 'hrprofile'):
        messages.error(request, "Only HR users can create questions.")
        return redirect('core:home')
    
    assessment = get_object_or_404(Assessment, id=assessment_id, created_by=request.user)
    sections = assessment.sections.all().order_by('order')  # Get all sections for the assessment
    
    if request.method == 'POST':
        section_id = request.POST.get('section')
        section_title = request.POST.get('section_title')
        section_order = request.POST.get('section_order', 0)
        question_type = request.POST.get('question_type')
        question_text = request.POST.get('question_text')
        points = request.POST.get('points', 1)
        is_auto_graded = request.POST.get('is_auto_graded', 'on') == 'on'

        # Create or get the section based on selection or new input
        if section_id:
            section = get_object_or_404(Section, id=section_id, assessment=assessment)
        else:
            # Ensure the section title is not empty and create a unique section
            if not section_title:
                messages.error(request, "Section title is required for new sections.")
                return render(request, 'create_question.html', {'assessment': assessment, 'sections': sections})
            
            # Check if a section with this title already exists for this assessment
            if Section.objects.filter(assessment=assessment, title=section_title).exists():
                messages.error(request, f"A section with the title '{section_title}' already exists.")
                return render(request, 'create_question.html', {'assessment': assessment, 'sections': sections})
            
            section, created = Section.objects.get_or_create(
                assessment=assessment,
                title=section_title,
                defaults={'order': section_order}
            )

        question = Question.objects.create(
            assessment=assessment,
            section=section,
            text=question_text,
            question_type=question_type,
            points=points if points else 0,
            is_auto_graded=is_auto_graded
        )
        
        if question_type == 'MC':
            choice1 = request.POST.get('choice1')
            choice2 = request.POST.get('choice2')
            choice3 = request.POST.get('choice3')
            correct_choice = request.POST.get('correct_choice')
            if choice1 and choice2 and choice3 and correct_choice:
                Choice.objects.create(question=question, text=choice1, is_correct=(correct_choice == '1'))
                Choice.objects.create(question=question, text=choice2, is_correct=(correct_choice == '2'))
                Choice.objects.create(question=question, text=choice3, is_correct=(correct_choice == '3'))
        elif question_type == 'TF':
            answer = request.POST.get('true_false_answer')
            if answer:
                Choice.objects.create(question=question, text='True', is_correct=(answer.lower() == 'true'))
                Choice.objects.create(question=question, text='False', is_correct=(answer.lower() == 'false'))
        elif question_type == 'SA':
            pass  # Manual grading for SA questions
        elif question_type == 'UP':
            pass  # Manual grading for UP questions
        elif question_type == 'MA':
            left1 = request.POST.get('left1')
            right1 = request.POST.get('right1')
            left2 = request.POST.get('left2')
            right2 = request.POST.get('right2')
            if left1 and right1 and left2 and right2:
                MatchPair.objects.create(question=question, left_text=left1, right_text=right1)
                MatchPair.objects.create(question=question, left_text=left2, right_text=right2)
        messages.success(request, "Question created successfully!")
        return redirect('core:view_assessments')
    
    context = {
        'assessment': assessment,
        'sections': sections,  # Pass sections to the template
    }
    return render(request, 'create_question.html', context)

def logout_view(request):
    logout(request)
    return redirect('core:home')