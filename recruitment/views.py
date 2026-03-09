from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import (
    Candidate, Job, Application, Skill, Experience, Education, JobAlert, 
    EmailNotification, CompanyProfile, SavedJob, RecentSearch, Message, 
    InterviewSchedule, CompanyReview, CompanyFollow, SkillAssessment, 
    AssessmentResult, ResumeTemplate, CandidateResume, SalaryData, 
    PremiumMembership, InterviewQuestion, InterviewQuestionBookmark,
    Referral, ATSIntegration, BackgroundCheck, CandidateSearchProfile,
    Certification, CertificationVerification, ReferralBonus
)
from .ai_engine import TalentSleuthAI
from django.views.decorators.http import require_http_methods
import json

def home(request):
    context = {
        'total_jobs': Job.objects.filter(status='published').count(),
        'total_candidates': Candidate.objects.filter(is_active=True).count(),
        'featured_jobs': Job.objects.filter(status='published').order_by('-created_at')[:6],
    }
    return render(request, 'recruitment/home.html', context)

def register_candidate(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone', '')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'recruitment/register.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        candidate = Candidate.objects.create(user=user, full_name=full_name, email=email, phone=phone)
        PremiumMembership.objects.create(candidate=candidate)
        login(request, user)
        messages.success(request, 'Welcome to TalentSleuth AI!')
        return redirect('candidate_profile')
    return render(request, 'recruitment/register.html')

def register_recruiter(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'recruitment/register_recruiter.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.save()
        login(request, user)
        return redirect('recruiter_dashboard')
    return render(request, 'recruitment/register_recruiter.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('recruiter_dashboard')
            else:
                return redirect('candidate_profile')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'recruitment/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('home')

@login_required
def candidate_profile(request):
    try:
        candidate = request.user.candidate_profile
    except Candidate.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('home')
    if request.method == 'POST':
        from decimal import Decimal
        years_exp = request.POST.get('years_of_experience')
        if years_exp:
            try:
                years_exp = Decimal(str(years_exp))
            except:
                years_exp = candidate.years_of_experience
        else:
            years_exp = candidate.years_of_experience
        candidate.full_name = request.POST.get('full_name', candidate.full_name)
        candidate.phone = request.POST.get('phone', candidate.phone)
        candidate.location = request.POST.get('location', candidate.location)
        candidate.current_role = request.POST.get('current_role', candidate.current_role)
        candidate.years_of_experience = years_exp
        candidate.linkedin_url = request.POST.get('linkedin_url', candidate.linkedin_url)
        candidate.github_url = request.POST.get('github_url', candidate.github_url)
        candidate.summary = request.POST.get('summary', candidate.summary)
        if 'resume' in request.FILES:
            candidate.resume = request.FILES['resume']
        if 'profile_picture' in request.FILES:
            candidate.profile_picture = request.FILES['profile_picture']
        candidate.save()
        try:
            TalentSleuthAI.update_candidate_overall_score(candidate)
        except:
            pass
        messages.success(request, 'Profile updated')
    job_alerts = JobAlert.objects.filter(candidate=candidate)
    saved_jobs_count = SavedJob.objects.filter(candidate=candidate).count()
    premium = getattr(candidate, 'premium', None)
    profile_completion = candidate.get_profile_completion_percentage()
    context = {
        'candidate': candidate,
        'skills': candidate.skills.all(),
        'experiences': candidate.experiences.all().order_by('-start_date'),
        'education': candidate.education.all().order_by('-end_date'),
        'applications': candidate.applications.all().order_by('-applied_at')[:5],
        'job_alerts': job_alerts,
        'saved_jobs_count': saved_jobs_count,
        'premium': premium,
        'profile_completion': profile_completion,
    }
    return render(request, 'recruitment/candidate_profile.html', context)

@login_required
def add_skill(request):
    if request.method == 'POST':
        candidate = request.user.candidate_profile
        name = request.POST.get('name')
        proficiency = request.POST.get('proficiency')
        years_experience = request.POST.get('years_experience', 0)
        Skill.objects.create(candidate=candidate, name=name, proficiency=proficiency, years_experience=years_experience)
        try:
            TalentSleuthAI.update_candidate_overall_score(candidate)
        except:
            pass
        messages.success(request, 'Skill added')
    return redirect('candidate_profile')

@login_required
def add_experience(request):
    if request.method == 'POST':
        candidate = request.user.candidate_profile
        Experience.objects.create(
            candidate=candidate,
            company=request.POST.get('company'),
            job_title=request.POST.get('job_title'),
            location=request.POST.get('location', ''),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            description=request.POST.get('description', ''),
            is_current=request.POST.get('is_current') == 'on'
        )
        try:
            TalentSleuthAI.update_candidate_overall_score(candidate)
        except:
            pass
        messages.success(request, 'Experience added')
    return redirect('candidate_profile')

def job_listings(request):
    jobs = Job.objects.filter(status='published').order_by('-created_at')
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    employment_type = request.GET.get('employment_type', '')
    remote_type = request.GET.get('remote_type', '')
    salary_min = request.GET.get('salary_min', '')
    if search_query:
        jobs = jobs.filter(Q(title__icontains=search_query) | Q(company__icontains=search_query) | Q(description__icontains=search_query))
    if location:
        jobs = jobs.filter(location__icontains=location)
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    if remote_type:
        jobs = jobs.filter(remote_type=remote_type)
    if salary_min:
        jobs = jobs.filter(salary_max__gte=int(salary_min))
    if search_query and request.user.is_authenticated and hasattr(request.user, 'candidate_profile'):
        candidate = request.user.candidate_profile
        RecentSearch.objects.create(candidate=candidate, search_query=search_query, location=location, employment_type=employment_type)
    context = {'jobs': jobs, 'search_query': search_query, 'location': location, 'employment_type': employment_type, 'remote_type': remote_type, 'salary_min': salary_min}
    return render(request, 'recruitment/job_listings.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='published')
    has_applied = False
    is_saved = False
    if request.user.is_authenticated and hasattr(request.user, 'candidate_profile'):
        has_applied = Application.objects.filter(candidate=request.user.candidate_profile, job=job).exists()
        is_saved = SavedJob.objects.filter(candidate=request.user.candidate_profile, job=job).exists()
    company_profile = None
    company_reviews = []
    if hasattr(job.recruiter, 'company_profile'):
        company_profile = job.recruiter.company_profile
        company_reviews = company_profile.reviews.all()[:5]
    company_rating = 0
    if company_profile:
        company_rating = company_profile.get_average_rating()
    context = {'job': job, 'has_applied': has_applied, 'is_saved': is_saved, 'required_skills': job.get_required_skills_list(), 'company_profile': company_profile, 'company_reviews': company_reviews, 'company_rating': company_rating}
    return render(request, 'recruitment/job_detail.html', context)

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, status='published')
    candidate = request.user.candidate_profile
    if Application.objects.filter(candidate=candidate, job=job).exists():
        messages.warning(request, 'Already applied')
        return redirect('job_detail', job_id=job_id)
    premium = getattr(candidate, 'premium', None)
    if premium and premium.plan != 'free':
        if premium.applications_remaining <= 0:
            messages.error(request, 'Application limit reached. Upgrade your plan!')
            return redirect('job_detail', job_id=job_id)
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        application = Application.objects.create(candidate=candidate, job=job, cover_letter=cover_letter, status='submitted')
        try:
            TalentSleuthAI.update_application_scores(application)
        except:
            pass
        if premium and premium.plan != 'free':
            premium.applications_used += 1
            premium.save()
        messages.success(request, 'Application submitted!')
        return redirect('candidate_profile')
    return render(request, 'recruitment/apply_job.html', {'job': job})

@login_required
def saved_jobs(request):
    if not hasattr(request.user, 'candidate_profile'):
        messages.error(request, 'Candidate profile required')
        return redirect('home')
    candidate = request.user.candidate_profile
    saved = SavedJob.objects.filter(candidate=candidate).select_related('job__recruiter')
    return render(request, 'recruitment/saved_jobs.html', {'saved_jobs': saved})

@login_required
@require_http_methods(['POST'])
def toggle_save_job(request, job_id):
    if not hasattr(request.user, 'candidate_profile'):
        return JsonResponse({'error': 'Login required'}, status=401)
    job = get_object_or_404(Job, id=job_id)
    candidate = request.user.candidate_profile
    saved_job = SavedJob.objects.filter(candidate=candidate, job=job).first()
    if saved_job:
        saved_job.delete()
        saved = False
    else:
        SavedJob.objects.create(candidate=candidate, job=job)
        saved = True
    return JsonResponse({'saved': saved})

@login_required
def recent_searches(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    searches = RecentSearch.objects.filter(candidate=candidate)[:10]
    return render(request, 'recruitment/recent_searches.html', {'searches': searches})

@login_required
def clear_searches(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    RecentSearch.objects.filter(candidate=candidate).delete()
    messages.success(request, 'Search history cleared')
    return redirect('job_listings')

@login_required
def inbox(request):
    messages_list = Message.objects.filter(recipient=request.user).select_related('sender')
    unread_count = messages_list.filter(is_read=False).count()
    return render(request, 'recruitment/inbox.html', {'messages': messages_list, 'unread_count': unread_count})

@login_required
def sent_messages(request):
    messages_list = Message.objects.filter(sender=request.user).select_related('recipient')
    return render(request, 'recruitment/sent_messages.html', {'messages': messages_list})

@login_required
def compose_message(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        try:
            recipient = User.objects.get(username=recipient_username)
            Message.objects.create(sender=request.user, recipient=recipient, subject=subject, body=body)
            messages.success(request, 'Message sent!')
            return redirect('inbox')
        except User.DoesNotExist:
            messages.error(request, 'Recipient not found')
    return render(request, 'recruitment/compose_message.html')

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return render(request, 'recruitment/view_message.html', {'message': message})

@login_required
def company_reviews(request, company_id):
    company = get_object_or_404(CompanyProfile, id=company_id)
    reviews = company.reviews.filter(is_approved=True)
    avg_rating = company.get_average_rating()
    return render(request, 'recruitment/company_reviews.html', {'company': company, 'reviews': reviews, 'avg_rating': avg_rating})

@login_required
def write_company_review(request, company_id):
    company = get_object_or_404(CompanyProfile, id=company_id)
    candidate = request.user.candidate_profile
    if CompanyReview.objects.filter(company=company, reviewer=candidate).exists():
        messages.warning(request, 'You have already reviewed this company')
        return redirect('company_reviews', company_id=company_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        pros = request.POST.get('pros', '')
        cons = request.POST.get('cons', '')
        advice = request.POST.get('advice', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        CompanyReview.objects.create(company=company, reviewer=candidate, rating=rating, title=title, pros=pros, cons=cons, advice=advice, is_anonymous=is_anonymous)
        messages.success(request, 'Review submitted!')
        return redirect('company_reviews', company_id=company_id)
    return render(request, 'recruitment/write_review.html', {'company': company})

@login_required
def follow_company(request, company_id):
    company = get_object_or_404(CompanyProfile, id=company_id)
    candidate = request.user.candidate_profile
    follow = CompanyFollow.objects.filter(candidate=candidate, company=company).first()
    if follow:
        follow.delete()
        messages.success(request, f'Unfollowed {company.name}')
    else:
        CompanyFollow.objects.create(candidate=candidate, company=company)
        messages.success(request, f'Following {company.name}')
    return redirect('company_reviews', company_id=company_id)

@login_required
def schedule_interview(request, application_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    application = get_object_or_404(Application, id=application_id, job__recruiter=request.user)
    if request.method == 'POST':
        InterviewSchedule.objects.create(
            application=application,
            scheduled_date=request.POST.get('scheduled_date'),
            scheduled_time=request.POST.get('scheduled_time'),
            duration_minutes=request.POST.get('duration_minutes', 30),
            interview_type=request.POST.get('interview_type', 'video'),
            meeting_link=request.POST.get('meeting_link', ''),
            location=request.POST.get('location', ''),
            notes=request.POST.get('notes', ''),
            status='scheduled'
        )
        application.status = 'interview'
        application.save()
        messages.success(request, 'Interview scheduled!')
        return redirect('view_applications', job_id=application.job.id)
    return render(request, 'recruitment/schedule_interview.html', {'application': application})

@login_required
def my_interviews(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    applications = Application.objects.filter(candidate=candidate, status='interview')
    interviews = InterviewSchedule.objects.filter(application__in=applications).select_related('application__job')
    return render(request, 'recruitment/my_interviews.html', {'interviews': interviews})

def assessment_list(request):
    assessments = SkillAssessment.objects.filter(is_active=True)
    return render(request, 'recruitment/assessment_list.html', {'assessments': assessments})

@login_required
def take_assessment(request, assessment_id):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('login')
    assessment = get_object_or_404(SkillAssessment, id=assessment_id, is_active=True)
    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
        passed = score >= assessment.passing_score
        AssessmentResult.objects.create(candidate=request.user.candidate_profile, assessment=assessment, score=score, passed=passed)
        messages.success(request, f'Assessment completed! Score: {score}%')
        return redirect('assessment_results')
    return render(request, 'recruitment/take_assessment.html', {'assessment': assessment})

@login_required
def assessment_results(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    results = AssessmentResult.objects.filter(candidate=request.user.candidate_profile).select_related('assessment')
    return render(request, 'recruitment/assessment_results.html', {'results': results})

@login_required
def resume_builder(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    templates = ResumeTemplate.objects.filter(is_active=True)
    my_resumes = CandidateResume.objects.filter(candidate=candidate)
    if request.method == 'POST':
        title = request.POST.get('title')
        template_id = request.POST.get('template')
        template = ResumeTemplate.objects.get(id=template_id) if template_id else None
        content = {
            'summary': request.POST.get('summary', ''),
            'skills': [s.name for s in candidate.skills.all()],
            'experience': [{'company': e.company, 'job_title': e.job_title, 'start_date': str(e.start_date), 'end_date': str(e.end_date) if e.end_date else 'Present', 'description': e.description} for e in candidate.experiences.all()],
            'education': [{'institution': edu.institution, 'degree': edu.degree, 'field_of_study': edu.field_of_study, 'end_date': str(edu.end_date)} for edu in candidate.education.all()]
        }
        CandidateResume.objects.create(candidate=candidate, template=template, title=title, content_json=json.dumps(content))
        messages.success(request, 'Resume created!')
        return redirect('resume_builder')
    return render(request, 'recruitment/resume_builder.html', {'templates': templates, 'my_resumes': my_resumes, 'candidate': candidate})

def salary_estimator(request):
    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        location = request.POST.get('location')
        experience = request.POST.get('experience')
        salary_data = SalaryData.objects.filter(job_title__icontains=job_title, location__icontains=location, experience_level=experience)
        if salary_data:
            avg_median = sum(s.salary_median for s in salary_data) / salary_data.count()
            context = {'salary_data': salary_data, 'avg_median': int(avg_median), 'job_title': job_title, 'location': location}
        else:
            context = {'no_data': True, 'job_title': job_title}
    else:
        context = {}
    return render(request, 'recruitment/salary_estimator.html', context)

@login_required
def premium_plans(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    premium = getattr(candidate, 'premium', None)
    return render(request, 'recruitment/premium_plans.html', {'premium': premium})

@login_required
def upgrade_premium(request, plan):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    premium = getattr(candidate, 'premium', None)
    if premium:
        premium.plan = plan
        if plan == 'free':
            premium.applications_limit = 5
            premium.is_highlighted = False
            premium.is_priority = False
            premium.is_featured = False
        elif plan == 'silver':
            premium.applications_limit = 25
            premium.is_highlighted = True
        elif plan == 'gold':
            premium.applications_limit = 100
            premium.is_highlighted = True
            premium.is_priority = True
        elif plan == 'platinum':
            premium.applications_limit = 500
            premium.is_highlighted = True
            premium.is_priority = True
            premium.is_featured = True
        premium.save()
        messages.success(request, f'Upgraded to {plan.title()} plan!')
    return redirect('candidate_profile')

@login_required
def application_analytics(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    applications = candidate.applications.all()
    total_applications = applications.count()
    pending = applications.filter(status='submitted').count()
    under_review = applications.filter(status='under_review').count()
    shortlisted = applications.filter(status='shortlisted').count()
    interview = applications.filter(status='interview').count()
    offered = applications.filter(status='offered').count()
    rejected = applications.filter(status='rejected').count()
    context = {'total_applications': total_applications, 'pending': pending, 'under_review': under_review, 'shortlisted': shortlisted, 'interview': interview, 'offered': offered, 'rejected': rejected}
    return render(request, 'recruitment/application_analytics.html', context)

@login_required
def recruiter_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    jobs = Job.objects.filter(recruiter=request.user)
    applications = Application.objects.filter(job__recruiter=request.user)
    company_profile = None
    if hasattr(request.user, 'company_profile'):
        company_profile = request.user.company_profile
    follower_count = 0
    if company_profile:
        follower_count = company_profile.followers.count()
    context = {'total_jobs': jobs.count(), 'active_jobs': jobs.filter(status='published').count(), 'total_applications': applications.count(), 'pending_applications': applications.filter(status='submitted').count(), 'recent_jobs': jobs.order_by('-created_at')[:5], 'top_applications': applications.order_by('-match_score')[:10], 'company_profile': company_profile, 'follower_count': follower_count}
    return render(request, 'recruitment/recruiter_dashboard.html', context)

@login_required
def create_job(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        job = Job.objects.create(
            recruiter=request.user,
            title=request.POST.get('title'),
            company=request.POST.get('company'),
            location=request.POST.get('location'),
            employment_type=request.POST.get('employment_type'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities', ''),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            min_experience_years=request.POST.get('min_experience_years', 0),
            required_skills=request.POST.get('required_skills'),
            remote_type=request.POST.get('remote_type', 'no'),
            status=request.POST.get('status', 'draft'),
            deadline=request.POST.get('deadline') or None,
        )
        messages.success(request, 'Job created!')
        return redirect('recruiter_dashboard')
    return render(request, 'recruitment/create_job.html')

@login_required
def view_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = job.applications.all().order_by('-match_score')
    return render(request, 'recruitment/view_applications.html', {'job': job, 'applications': applications})

@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if not (request.user.is_staff or application.candidate.user == request.user):
        messages.error(request, 'Access denied')
        return redirect('home')
    context = {'application': application, 'candidate': application.candidate, 'job': application.job, 'insights': application.ai_insights.all().order_by('-confidence_score'), 'skills': application.candidate.skills.all(), 'experiences': application.candidate.experiences.all().order_by('-start_date')}
    return render(request, 'recruitment/application_detail.html', context)

@login_required
@require_http_methods(['POST'])
def update_application_status(request, application_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    application = get_object_or_404(Application, id=application_id)
    new_status = request.POST.get('status')
    if new_status in dict(Application.STATUS_CHOICES):
        old_status = application.status
        application.status = new_status
        application.save()
        return JsonResponse({'success': True, 'status': new_status})
    return JsonResponse({'error': 'Invalid status'}, status=400)

@login_required
def manage_job_alerts(request):
    if not hasattr(request.user, 'candidate_profile'):
        messages.error(request, 'Candidate profile required')
        return redirect('home')
    candidate = request.user.candidate_profile
    alerts = JobAlert.objects.filter(candidate=candidate)
    if request.method == 'POST':
        keywords = request.POST.get('keywords', '')
        location = request.POST.get('location', '')
        if keywords:
            JobAlert.objects.create(candidate=candidate, keywords=keywords, location=location, is_active=True)
            messages.success(request, 'Job alert created!')
        return redirect('manage_job_alerts')
    return render(request, 'recruitment/manage_job_alerts.html', {'alerts': alerts})

@login_required
def delete_job_alert(request, alert_id):
    alert = get_object_or_404(JobAlert, id=alert_id, candidate=request.user.candidate_profile)
    alert.delete()
    messages.success(request, 'Alert deleted')
    return redirect('manage_job_alerts')

@login_required
def toggle_job_alert(request, alert_id):
    alert = get_object_or_404(JobAlert, id=alert_id, candidate=request.user.candidate_profile)
    alert.is_active = not alert.is_active
    alert.save()
    return redirect('manage_job_alerts')

@login_required
def company_profile(request):
    if not request.user.is_staff:
        messages.error(request, 'Recruiter access required')
        return redirect('home')
    company_profile = getattr(request.user, 'company_profile', None)
    if request.method == 'POST':
        if company_profile:
            company_profile.name = request.POST.get('name', company_profile.name)
            company_profile.industry = request.POST.get('industry', company_profile.industry)
            company_profile.website = request.POST.get('website', company_profile.website)
            company_profile.description = request.POST.get('description', company_profile.description)
            company_profile.size = request.POST.get('size', company_profile.size)
            company_profile.headquarters = request.POST.get('headquarters', company_profile.headquarters)
            company_profile.benefits = request.POST.get('benefits', company_profile.benefits)
            company_profile.culture = request.POST.get('culture', company_profile.culture)
            if 'logo' in request.FILES:
                company_profile.logo = request.FILES['logo']
            company_profile.save()
            messages.success(request, 'Company profile updated!')
        else:
            CompanyProfile.objects.create(
                recruiter=request.user,
                name=request.POST.get('name'),
                industry=request.POST.get('industry'),
                website=request.POST.get('website'),
                description=request.POST.get('description'),
                size=request.POST.get('size'),
                headquarters=request.POST.get('headquarters'),
                benefits=request.POST.get('benefits', ''),
                culture=request.POST.get('culture', ''),
                logo=request.FILES.get('logo')
            )
            messages.success(request, 'Company profile created!')
        return redirect('recruiter_dashboard')
    return render(request, 'recruitment/company_profile.html', {'company_profile': company_profile})

@login_required
def recommended_jobs(request):
    if not hasattr(request.user, 'candidate_profile'):
        messages.error(request, 'Candidate profile required')
        return redirect('home')
    candidate = request.user.candidate_profile
    all_jobs = Job.objects.filter(status='published')
    scored_jobs = []
    for job in all_jobs:
        try:
            score = TalentSleuthAI.calculate_overall_match_score(candidate, job)
        except:
            score = 50
        scored_jobs.append((job, score))
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    recommended = [job for job, score in scored_jobs[:20] if score > 30]
    return render(request, 'recruitment/recommended_jobs.html', {'recommended_jobs': recommended, 'candidate': candidate})

@login_required
def notifications(request):
    if hasattr(request.user, 'candidate_profile'):
        notifications = EmailNotification.objects.filter(recipient=request.user.candidate_profile).order_by('-created_at')[:20]
    else:
        notifications = []
    return render(request, 'recruitment/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(EmailNotification, id=notification_id, recipient=request.user.candidate_profile)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def parse_resume(request):
    if not hasattr(request.user, 'candidate_profile'):
        return JsonResponse({'error': 'Candidate profile required'}, status=403)
    if request.method == 'POST' and request.FILES.get('resume'):
        candidate = request.user.candidate_profile
        resume_file = request.FILES['resume']
        try:
            parsed_data = TalentSleuthAI.parse_resume(resume_file)
            if parsed_data:
                return JsonResponse({'success': True, 'parsed_data': parsed_data})
            else:
                return JsonResponse({'success': False, 'error': 'Could not parse resume'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'error': 'No resume file provided'}, status=400)

@login_required
@require_http_methods(['POST'])
def quick_apply(request, job_id):
    if not hasattr(request.user, 'candidate_profile'):
        return JsonResponse({'error': 'Login required'}, status=401)
    job = get_object_or_404(Job, id=job_id, status='published')
    candidate = request.user.candidate_profile
    if Application.objects.filter(candidate=candidate, job=job).exists():
        return JsonResponse({'error': 'Already applied to this job'}, status=400)
    premium = getattr(candidate, 'premium', None)
    if premium and premium.plan != 'free':
        if premium.applications_remaining <= 0:
            return JsonResponse({'error': 'Application limit reached'}, status=400)
    if not candidate.resume:
        return JsonResponse({'error': 'Please upload a resume first'}, status=400)
    application = Application.objects.create(
        candidate=candidate,
        job=job,
        cover_letter=f"Quick Apply - Using my existing profile and resume for {job.title} position.",
        status='submitted'
    )
    try:
        TalentSleuthAI.update_application_scores(application)
    except:
        pass
    if premium and premium.plan != 'free':
        premium.applications_used += 1
        premium.save()
    return JsonResponse({'success': True, 'message': 'Application submitted successfully!', 'application_id': application.id})

def interview_questions(request):
    job_title = request.GET.get('job_title', '')
    company_id = request.GET.get('company_id')
    question_type = request.GET.get('type', '')
    questions = InterviewQuestion.objects.filter(is_active=True)
    if job_title:
        questions = questions.filter(job_title__icontains=job_title)
    if company_id:
        questions = questions.filter(company_id=company_id) | questions.filter(company__isnull=True)
    if question_type:
        questions = questions.filter(question_type=question_type)
    return render(request, 'recruitment/interview_questions.html', {'questions': questions[:50], 'job_title': job_title, 'question_type': question_type})

@login_required
def bookmark_interview_question(request, question_id):
    if not hasattr(request.user, 'candidate_profile'):
        return JsonResponse({'error': 'Login required'}, status=401)
    question = get_object_or_404(InterviewQuestion, id=question_id)
    candidate = request.user.candidate_profile
    bookmark, created = InterviewQuestionBookmark.objects.get_or_create(candidate=candidate, question=question)
    return JsonResponse({'success': True, 'bookmarked': created})

@login_required
def practice_interview_questions(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    bookmarked = InterviewQuestionBookmark.objects.filter(candidate=candidate).select_related('question')
    if bookmarked.exists():
        questions = [b.question for b in bookmarked]
    else:
        questions = list(InterviewQuestion.objects.filter(is_active=True)[:10])
    return render(request, 'recruitment/practice_questions.html', {'questions': questions, 'is_practice_mode': True})

@login_required
def submit_question_answer(request, question_id):
    if not hasattr(request.user, 'candidate_profile'):
        return JsonResponse({'error': 'Login required'}, status=401)
    question = get_object_or_404(InterviewQuestion, id=question_id)
    candidate = request.user.candidate_profile
    if request.method == 'POST':
        answer = request.POST.get('answer', '')
        bookmark, created = InterviewQuestionBookmark.objects.get_or_create(candidate=candidate, question=question, defaults={'my_answer': answer, 'is_practiced': True})
        if not created:
            bookmark.my_answer = answer
            bookmark.is_practiced = True
            bookmark.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def manage_certifications(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    certifications = Certification.objects.filter(candidate=candidate)
    if request.method == 'POST':
        name = request.POST.get('name')
        issuing_organization = request.POST.get('issuing_organization')
        issue_date = request.POST.get('issue_date')
        expiration_date = request.POST.get('expiration_date') or None
        credential_id = request.POST.get('credential_id', '')
        credential_url = request.POST.get('credential_url', '')
        cert = Certification.objects.create(candidate=candidate, name=name, issuing_organization=issuing_organization, issue_date=issue_date, expiration_date=expiration_date, credential_id=credential_id, credential_url=credential_url, certificate_file=request.FILES.get('certificate_file'))
        CertificationVerification.objects.create(certification=cert, status='pending')
        messages.success(request, 'Certification added! Verification requested.')
        return redirect('manage_certifications')
    return render(request, 'recruitment/manage_certifications.html', {'certifications': certifications})

@login_required
def verify_certification(request, certification_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    cert = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        verification = cert.verifications.first()
        if verification:
            verification.status = status
            verification.verified_by = request.user.username
            verification.verification_notes = notes
            if status == 'verified':
                verification.verified_at = timezone.now()
            verification.save()
        messages.success(request, f'Certification {status}!')
        return redirect('view_applications', job_id=0)
    return render(request, 'recruitment/verify_certification.html', {'certification': cert})

@login_required
def referral_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    referrals = Referral.objects.filter(referrer=request.user)
    total_referrals = referrals.count()
    hired = referrals.filter(status='hired').count()
    pending = referrals.filter(status='pending').count()
    bonuses = ReferralBonus.objects.filter(referral__referrer=request.user)
    total_bonus = sum(b.amount for b in bonuses.filter(status='paid'))
    return render(request, 'recruitment/referral_dashboard.html', {'referrals': referrals, 'total_referrals': total_referrals, 'hired': hired, 'pending': pending, 'bonuses': bonuses, 'total_bonus': total_bonus})

@login_required
def submit_referral(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    if request.method == 'POST':
        candidate_email = request.POST.get('candidate_email')
        job_id = request.POST.get('job_id')
        notes = request.POST.get('notes', '')
        try:
            candidate = Candidate.objects.get(email=candidate_email)
        except Candidate.DoesNotExist:
            return JsonResponse({'error': 'Candidate not found'}, status=404)
        job = None
        if job_id:
            job = get_object_or_404(Job, id=job_id)
        referral = Referral.objects.create(referrer=request.user, referred_candidate=candidate, job=job, referral_notes=notes, resume=request.FILES.get('resume'))
        return JsonResponse({'success': True, 'referral_id': referral.id})
    jobs = Job.objects.filter(recruiter=request.user, status='published')
    return render(request, 'recruitment/submit_referral.html', {'jobs': jobs})

@login_required
def manage_referrals(request):
    if not request.user.is_staff:
        return redirect('home')
    referrals = Referral.objects.filter(job__recruiter=request.user)
    if request.method == 'POST':
        referral_id = request.POST.get('referral_id')
        new_status = request.POST.get('status')
        referral = get_object_or_404(Referral, id=referral_id, job__recruiter=request.user)
        referral.status = new_status
        referral.save()
        if new_status == 'hired':
            ReferralBonus.objects.create(referral=referral, amount=500, status='pending')
        messages.success(request, f'Referral status updated to {new_status}')
        return redirect('manage_referrals')
    return render(request, 'recruitment/manage_referrals.html', {'referrals': referrals})

@login_required
def ats_integrations(request):
    if not request.user.is_staff:
        return redirect('home')
    company_profile = getattr(request.user, 'company_profile', None)
    if not company_profile:
        messages.error(request, 'Company profile required')
        return redirect('company_profile')
    integrations = ATSIntegration.objects.filter(company=company_profile)
    if request.method == 'POST':
        integration_type = request.POST.get('integration_type')
        api_key = request.POST.get('api_key', '')
        webhook_url = request.POST.get('webhook_url', '')
        ATSIntegration.objects.create(company=company_profile, integration_type=integration_type, api_key=api_key, webhook_url=webhook_url)
        messages.success(request, 'ATS integration added!')
        return redirect('ats_integrations')
    return render(request, 'recruitment/ats_integrations.html', {'integrations': integrations})

@login_required
def sync_ats(request, integration_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    integration = get_object_or_404(ATSIntegration, id=integration_id, company__recruiter=request.user)
    integration.last_sync = timezone.now()
    integration.status = 'active'
    integration.save()
    messages.success(request, 'ATS sync completed!')
    return redirect('ats_integrations')

@login_required
def background_checks(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    checks = BackgroundCheck.objects.filter(candidate=candidate)
    return render(request, 'recruitment/background_checks.html', {'checks': checks})

@login_required
def initiate_background_check(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        check_type = request.POST.get('check_type')
        provider = request.POST.get('provider')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        check = BackgroundCheck.objects.create(candidate=candidate, check_type=check_type, provider=provider, status='initiated')
        return JsonResponse({'success': True, 'check_id': check.id})
    applications = Application.objects.filter(job__recruiter=request.user)
    candidates = Candidate.objects.filter(id__in=applications.values('candidate_id')).distinct()
    return render(request, 'recruitment/initiate_background_check.html', {'candidates': candidates})

@login_required
def update_background_check(request, check_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    check = get_object_or_404(BackgroundCheck, id=check_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        result = request.POST.get('result', '')
        check.status = status
        check.result_summary = result
        if status == 'completed':
            check.completed_at = timezone.now()
            check.is_cleared = request.POST.get('is_cleared') == 'on'
        check.save()
        messages.success(request, 'Background check updated!')
        return redirect('view_applications', job_id=0)
    return render(request, 'recruitment/update_background_check.html', {'check': check})

def job_search_chat(request):
    query = request.GET.get('q', '')
    jobs = []
    if query:
        all_jobs = Job.objects.filter(status='published')
        jobs = all_jobs.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(description__icontains=query) | Q(required_skills__icontains=query) | Q(location__icontains=query)).distinct()[:20]
    return render(request, 'recruitment/job_search_chat.html', {'jobs': jobs, 'query': query})

@login_required
def advanced_candidate_search(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    keywords = request.GET.get('keywords', '')
    location = request.GET.get('location', '')
    min_experience = request.GET.get('min_experience', '')
    max_experience = request.GET.get('max_experience', '')
    skills = request.GET.get('skills', '')
    candidates = Candidate.objects.filter(is_active=True)
    if keywords:
        candidates = candidates.filter(Q(full_name__icontains=keywords) | Q(skills__name__icontains=keywords) | Q(experiences__job_title__icontains=keywords) | Q(experiences__company__icontains=keywords)).distinct()
    if location:
        candidates = candidates.filter(Q(location__icontains=location) | Q(experiences__location__icontains=location)).distinct()
    if min_experience:
        candidates = candidates.filter(years_of_experience__gte=int(min_experience))
    if max_experience:
        candidates = candidates.filter(years_of_experience__lte=int(max_experience))
    if skills:
        for skill in skills.split(','):
            candidates = candidates.filter(skills__name__icontains=skill.strip())
    return render(request, 'recruitment/advanced_candidate_search.html', {'candidates': candidates[:50], 'keywords': keywords, 'location': location, 'min_experience': min_experience, 'max_experience': max_experience, 'skills': skills})

@login_required
def saved_searches(request):
    if not request.user.is_staff:
        return redirect('home')
    searches = CandidateSearchProfile.objects.filter(recruiter=request.user)
    return render(request, 'recruitment/saved_searches.html', {'searches': searches})

@login_required
def delete_my_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted successfully')
        return redirect('home')
    return render(request, 'recruitment/delete_my_account.html')

@login_required
def request_work_verification(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    messages.success(request, 'Work verification request submitted!')
    return redirect('candidate_profile')

@login_required
def add_culture_score(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    company_id = request.POST.get('company_id')
    culture_type = request.POST.get('culture_type')
    score = request.POST.get('score')
    company = get_object_or_404(CompanyProfile, id=company_id)
    messages.success(request, f'Culture score added for {company.name}')
    return redirect('company_profile')

# Recruiter assessment management views
@login_required
def create_assessment(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        passing_score = request.POST.get('passing_score', 70)
        SkillAssessment.objects.create(
            title=title,
            description=description,
            passing_score=passing_score,
            created_by=request.user,
            is_active=True
        )
        messages.success(request, 'Assessment created!')
        return redirect('recruiter_dashboard')
    return render(request, 'recruitment/create_assessment.html')

@login_required
def manage_assessments(request):
    if not request.user.is_staff:
        applications = job.applications.all().order_by('-match_score')
        return redirect('home')
    assessments = SkillAssessment.objects.filter(created_by=request.user)
    return render(request, 'recruitment/manage_assessments.html', {'assessments': assessments})

@login_required
def resume_ranking(request, job_id):
    if not request.user.is_staff:
        ranked_applications = []
        return redirect('home')
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    for application in applications:
        try:
            rank_score = TalentSleuthAI.calculate_overall_match_score(application.candidate, job)
        except:
            rank_score = application.match_score or 50
        ranked_applications.append({
            'application': application,
            'rank_score': rank_score,
            'skills_match': application.get_skill_match_percentage() if hasattr(application, 'get_skill_match_percentage') else 0,
            'experience_match': application.match_score or 50
        })
    ranked_applications.sort(key=lambda x: x['rank_score'], reverse=True)
    return render(request, 'recruitment/resume_ranking.html', {'job': job, 'ranked_applications': ranked_applications})

@login_required
def my_interview_bookmarks(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    bookmarks = InterviewQuestionBookmark.objects.filter(candidate=candidate).select_related('question__company')
    return render(request, 'recruitment/interview_bookmarks.html', {'bookmarks': bookmarks})

@login_required
def edit_question_answer(request, answer_id):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    bookmark = get_object_or_404(InterviewQuestionBookmark, id=answer_id, candidate=request.user.candidate_profile)
    if request.method == 'POST':
        bookmark.my_answer = request.POST.get('answer', '')
        bookmark.is_practiced = True
        bookmark.save()
        messages.success(request, 'Answer updated!')
        return redirect('my_interview_answers')
    return render(request, 'recruitment/edit_answer.html', {'bookmark': bookmark})

@login_required
def delete_question_answer(request, answer_id):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    bookmark = get_object_or_404(InterviewQuestionBookmark, id=answer_id, candidate=request.user.candidate_profile)
    bookmark.my_answer = ''
    bookmark.is_practiced = False
    bookmark.save()
    messages.success(request, 'Answer deleted!')
    return redirect('my_interview_answers')

@login_required
def my_interview_answers(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    candidate = request.user.candidate_profile
    answers = InterviewQuestionBookmark.objects.filter(candidate=candidate, is_practiced=True).select_related('question')
    return render(request, 'recruitment/interview_answers.html', {'answers': answers})

@login_required
def run_saved_search(request, search_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    search_profile = get_object_or_404(CandidateSearchProfile, id=search_id, recruiter=request.user)
    keywords = search_profile.keywords
    location = search_profile.location
    min_experience = search_profile.min_experience_years
    max_experience = search_profile.max_experience_years
    skills = search_profile.required_skills
    candidates = Candidate.objects.filter(is_active=True)
    if keywords:
        candidates = candidates.filter(Q(full_name__icontains=keywords) | Q(skills__name__icontains=keywords) | Q(experiences__job_title__icontains=keywords) | Q(experiences__company__icontains=keywords)).distinct()
    if location:
        candidates = candidates.filter(Q(location__icontains=location) | Q(experiences__location__icontains=location)).distinct()
    if min_experience:
        candidates = candidates.filter(years_of_experience__gte=min_experience)
    if max_experience:
        candidates = candidates.filter(years_of_experience__lte=max_experience)
    if skills:
        for skill in skills.split(','):
            candidates = candidates.filter(skills__name__icontains=skill.strip())
    return render(request, 'recruitment/advanced_candidate_search.html', {'candidates': candidates[:50], 'keywords': keywords, 'location': location, 'min_experience': min_experience, 'max_experience': max_experience, 'skills': skills, 'search_name': search_profile.name})
