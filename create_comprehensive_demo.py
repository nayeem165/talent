#!/usr/bin/env python
"""
Create comprehensive demo data for TalentSleuth AI
This script populates the database with realistic data so all 19 features are immediately visible
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentsleuth.settings')
django.setup()

from django.contrib.auth.models import User
from recruitment.models import (
    Candidate, Job, Application, Skill, Experience, Education,
    CompanyProfile, SavedJob, InterviewQuestion, InterviewQuestionBookmark,
    SkillAssessment, AssessmentResult, Message, CompanyReview, Referral,
    CandidateSearchProfile, BackgroundCheck, ATSIntegration
)
from datetime import datetime, timedelta
from django.utils import timezone

print("🚀 Creating comprehensive demo data...\n")

# Clear existing demo data
print("📋 Clearing existing data...")
User.objects.filter(username__startswith='demo_').delete()
User.objects.filter(username__startswith='recruiter_').delete()

# ==================== CREATE USERS ====================
print("👥 Creating demo users...")

# Demo Candidate Users
candidate_users = []
for i in range(5):
    user = User.objects.create_user(
        username=f'demo_candidate_{i+1}',
        email=f'candidate{i+1}@example.com',
        password='demo123456',
        first_name=f'Candidate {i+1}',
        last_name='Demo',
        is_staff=False
    )
    candidate_users.append(user)
    print(f"  ✓ Created candidate user: {user.username}")

# Demo Recruiter Users
recruiter_users = []
for i in range(3):
    user = User.objects.create_user(
        username=f'recruiter_{i+1}',
        email=f'recruiter{i+1}@company.com',
        password='demo123456',
        first_name=f'Recruiter {i+1}',
        last_name='Demo',
        is_staff=True
    )
    recruiter_users.append(user)
    print(f"  ✓ Created recruiter user: {user.username}")

# ==================== CREATE CANDIDATES WITH PROFILES ====================
print("\n📝 Creating candidate profiles...")

candidate_profiles = []
for i, user in enumerate(candidate_users):
    candidate = Candidate.objects.create(
        user=user,
        full_name=user.first_name,
        email=user.email,
        phone=f'555-010{i}',
        location='New York, NY',
        current_role='Software Engineer',
        summary=f'Experienced software developer with passion for building great products. {i+1} years of experience.',
        years_of_experience=i + 2,
        is_active=True,
        overall_score=75 + i * 5
    )
    candidate_profiles.append(candidate)
    print(f"  ✓ Created candidate profile: {candidate.full_name}")

# ==================== ADD SKILLS TO CANDIDATES ====================
print("\n🎯 Adding skills to candidates...")

skills_data = ['Python', 'JavaScript', 'Django', 'React', 'PostgreSQL', 'AWS', 'Docker', 'Git']

for candidate in candidate_profiles:
    for skill_name in skills_data[:3]:  # Add first 3 skills to each
        Skill.objects.create(
            candidate=candidate,
            name=skill_name,
            proficiency='Expert',
            years_experience=candidate.years_of_experience
        )
    print(f"  ✓ Added skills to {candidate.full_name}")

# ==================== ADD EXPERIENCE TO CANDIDATES ====================
print("\n💼 Adding work experience...")

for candidate in candidate_profiles:
    for exp_idx in range(2):
        Experience.objects.create(
            candidate=candidate,
            job_title=f'Senior Developer' if exp_idx == 0 else 'Junior Developer',
            company=f'Tech Company {exp_idx + 1}',
            location='New York, NY',
            start_date=(timezone.now() - timedelta(days=365 * (2 + exp_idx))).date(),
            end_date=(timezone.now() - timedelta(days=365 * exp_idx)).date() if exp_idx > 0 else None,
            description='Worked on building scalable applications',
            is_current=exp_idx == 0
        )
    print(f"  ✓ Added experience to {candidate.full_name}")

# ==================== ADD EDUCATION ====================
print("\n🎓 Adding education...")

for candidate in candidate_profiles:
    Education.objects.create(
        candidate=candidate,
        institution='State University',
        degree='bachelor',
        field_of_study='Computer Science',
        start_date=(timezone.now() - timedelta(days=365 * 6)).date(),
        end_date=(timezone.now() - timedelta(days=365 * 2)).date(),
        grade='3.8'
    )
    print(f"  ✓ Added education to {candidate.full_name}")

# ==================== CREATE COMPANY PROFILES ====================
print("\n🏢 Creating company profiles...")

company_profiles = []
for i, recruiter in enumerate(recruiter_users):
    company = CompanyProfile.objects.create(
        recruiter=recruiter,
        name=f'Tech Company {i+1}',
        industry='Software Development',
        size=f'{(i+1)*100}-{(i+1)*500}',
        website=f'https://company{i+1}.com',
        description=f'Leading tech company focused on innovative solutions. Company {i+1}',
        headquarters='San Francisco, CA',
        founded_year=2015 + i,
        logo=None
    )
    company_profiles.append(company)
    print(f"  ✓ Created company: {company.name}")

# ==================== CREATE JOBS ====================
print("\n📢 Creating job postings...")

job_titles = ['Senior Engineer', 'Full Stack Developer', 'DevOps Engineer', 'Product Manager', 'Data Scientist']
job_postings = []

for i, company in enumerate(company_profiles):
    for j, title in enumerate(job_titles[:3]):
        job = Job.objects.create(
            recruiter=company.recruiter,
            company=company.name,
            title=title,
            description=f'Exciting opportunity to join our {company.name} team. We are looking for a talented {title}.',
            requirements=f'Looking for an experienced {title} to join our team.',
            location='New York, NY',
            salary_min=80000,
            salary_max=150000,
            salary_currency='USD',
            employment_type='full_time',
            required_skills='Python, Django, PostgreSQL',
            min_experience_years=2,
            remote_type='hybrid',
            status='published'
        )
        job_postings.append(job)
        print(f"  ✓ Created job: {job.title} at {company.name}")

# ==================== CREATE APPLICATIONS ====================
print("\n📨 Creating job applications...")

applications = []
for job in job_postings[:5]:
    for candidate in candidate_profiles[:3]:
        app = Application.objects.create(
            candidate=candidate,
            job=job,
            status='under_review',
            match_score=75 + (hash(f"{candidate.id}{job.id}") % 25),
            skill_match_score=80,
            experience_match_score=70
        )
        applications.append(app)
        print(f"  ✓ Created application: {candidate.full_name} → {job.title}")

# ==================== ADD SAVED JOBS ====================
print("\n❤️ Adding saved jobs...")

for candidate in candidate_profiles:
    for job in job_postings[:2]:
        SavedJob.objects.get_or_create(
            candidate=candidate,
            job=job
        )
    print(f"  ✓ {candidate.full_name} saved jobs")

# ==================== CREATE INTERVIEW QUESTIONS ====================
print("\n❓ Creating interview questions...")

interview_questions_data = [
    {
        'question_text': 'Tell me about your most challenging project',
        'sample_answer': 'Describe a complex problem you solved',
        'job_title': 'Software Developer',
        'difficulty': 'medium'
    },
    {
        'question_text': 'How do you handle tight deadlines?',
        'sample_answer': 'Prioritize tasks and communicate clearly',
        'job_title': 'Software Developer',
        'difficulty': 'medium'
    },
    {
        'question_text': 'Describe your experience with cloud platforms',
        'sample_answer': 'AWS, Azure, or GCP experience',
        'job_title': 'DevOps Engineer',
        'difficulty': 'hard'
    },
    {
        'question_text': 'How do you approach code reviews?',
        'sample_answer': 'Focus on quality, constructive feedback',
        'job_title': 'Software Developer',
        'difficulty': 'easy'
    },
    {
        'question_text': 'Tell me about a time you failed',
        'sample_answer': 'Learning experience and growth',
        'job_title': 'General',
        'difficulty': 'medium'
    },
]

interview_qs = []
for q_data in interview_questions_data:
    q = InterviewQuestion.objects.create(
        question_text=q_data['question_text'],
        sample_answer=q_data['sample_answer'],
        job_title=q_data['job_title'],
        difficulty=q_data['difficulty'],
        question_type='behavioral',
        is_active=True
    )
    interview_qs.append(q)
    print(f"  ✓ Created question: {q.question_text[:50]}...")

# ==================== CREATE INTERVIEW BOOKMARKS ====================
print("\n📌 Creating interview bookmarks...")

for candidate in candidate_profiles:
    for question in interview_qs[:3]:
        bookmark = InterviewQuestionBookmark.objects.create(
            candidate=candidate,
            question=question,
            my_answer='Sample answer for practice',
            is_practiced=True
        )
    print(f"  ✓ {candidate.full_name} bookmarked questions")

# ==================== CREATE SKILL ASSESSMENTS ====================
print("\n✅ Creating skill assessments...")

assessments = []
assessment_data = [
    {'title': 'Python Fundamentals', 'skill': 'Python', 'passes': 80},
    {'title': 'JavaScript ES6+', 'skill': 'JavaScript', 'passes': 85},
    {'title': 'PostgreSQL Advanced', 'skill': 'PostgreSQL', 'passes': 75},
]

for a_data in assessment_data:
    assessment = SkillAssessment.objects.create(
        title=a_data['title'],
        skill_category=a_data['skill'],
        description=f'Test your {a_data["skill"]} skills',
        total_questions=20,
        passing_score=a_data['passes'],
        duration_minutes=60,
        difficulty='intermediate',
        is_active=True
    )
    assessments.append(assessment)
    print(f"  ✓ Created assessment: {assessment.title}")

# ==================== CREATE ASSESSMENT RESULTS ====================
print("\n📊 Creating assessment results...")

for candidate in candidate_profiles:
    for assessment in assessments:
        result = AssessmentResult.objects.create(
            candidate=candidate,
            assessment=assessment,
            score=assessment.passing_score + (hash(str(candidate.id)) % 20),
            passed=True
        )
    print(f"  ✓ {candidate.full_name} completed assessments")

# ==================== CREATE MESSAGES ====================
print("\n💬 Creating messages...")

for candidate in candidate_profiles[:2]:
    for recruiter in recruiter_users[:1]:
        Message.objects.create(
            sender=recruiter,
            recipient=candidate.user,
            subject='Great fit for our team!',
            body=f'Hi {candidate.full_name}, we love your profile and would like to discuss opportunities.'
        )
    print(f"  ✓ Recruiter sent message to {candidate.full_name}")

# ==================== CREATE COMPANY REVIEWS ====================
print("\n⭐ Creating company reviews...")

for i, company in enumerate(company_profiles):
    for candidate in candidate_profiles[:2]:
        CompanyReview.objects.create(
            reviewer=candidate,
            company=company,
            title='Great place to work',
            pros='Excellent culture and work-life balance',
            cons='None so far',
            rating=4 + (i % 2),
            is_anonymous=False
        )
    print(f"  ✓ Created reviews for {company.name}")

# ==================== CREATE CANDIDATE SEARCH PROFILES ====================
print("\n💾 Creating saved search profiles...")

for recruiter in recruiter_users:
    search = CandidateSearchProfile.objects.create(
        recruiter=recruiter,
        name=f'Senior Python Developers - {recruiter.username}',
        keywords='Python',
        location='New York',
        min_experience=3,
        max_experience=10,
        skills='Python, Django',
        education_levels='Bachelor',
        notify_on_new=True,
        results_count=len(candidate_profiles)
    )
    print(f"  ✓ Created search profile for {recruiter.username}")

# ==================== CREATE BACKGROUND CHECKS ====================
print("\n🔍 Creating background checks...")

for candidate in candidate_profiles[:2]:
    for recruiter in recruiter_users[:1]:
        check = BackgroundCheck.objects.create(
            candidate=candidate,
            check_type='identity',
            provider='Checkr',
            status='completed',
            is_cleared=True,
            result_summary='All checks passed'
        )
    print(f"  ✓ Background check created for {candidate.full_name}")

# ==================== CREATE REFERRALS ====================
print("\n🤝 Creating referrals...")

# Create candidates to be referred
referred_candidates = []
for i in range(2):
    user = User.objects.create_user(
        username=f'referred_candidate_{i+1}',
        email=f'referred{i+1}@example.com',
        password='demo123456',
        first_name='Referred',
        last_name=f'Candidate {i+1}',
        is_staff=False
    )
    referred_cand = Candidate.objects.create(
        user=user,
        full_name=f'Referred Candidate {i+1}',
        email=user.email,
        is_active=True
    )
    referred_candidates.append(referred_cand)

for recruiter in recruiter_users:
    for i, candidate in enumerate(referred_candidates[:2]):
        Referral.objects.create(
            referrer=recruiter,
            referred_candidate=candidate,
            job=job_postings[0] if job_postings else None,
            status='pending'
        )
    print(f"  ✓ Created referral for {recruiter.username}")

# ==================== CREATE ATS INTEGRATION ====================
print("\n🔗 Creating ATS integrations...")

for company in company_profiles:
    ats = ATSIntegration.objects.create(
        company=company,
        integration_type='workday',
        api_key='demo_api_key_123',
        status='active'
    )
    print(f"  ✓ Created ATS integration for {company.name}")

# ==================== SUMMARY ====================
print("\n" + "="*60)
print("✨ DEMO DATA CREATION COMPLETE! ✨")
print("="*60)

print(f"\n📊 DATABASE SUMMARY:")
print(f"  • Users: {User.objects.filter(is_staff=False).count()} candidates + {User.objects.filter(is_staff=True).count()} recruiters")
print(f"  • Candidates: {Candidate.objects.count()}")
print(f"  • Companies: {CompanyProfile.objects.count()}")
print(f"  • Job Postings: {Job.objects.count()}")
print(f"  • Applications: {Application.objects.count()}")
print(f"  • Saved Jobs: {SavedJob.objects.count()}")
print(f"  • Interview Questions: {InterviewQuestion.objects.count()}")
print(f"  • Skill Assessments: {SkillAssessment.objects.count()}")
print(f"  • Assessment Results: {AssessmentResult.objects.count()}")
print(f"  • Messages: {Message.objects.count()}")
print(f"  • Company Reviews: {CompanyReview.objects.count()}")
print(f"  • Background Checks: {BackgroundCheck.objects.count()}")
print(f"  • Referrals: {Referral.objects.count()}")
print(f"  • Saved Searches: {CandidateSearchProfile.objects.count()}")

print(f"\n🔑 TEST ACCOUNTS:")
for i, user in enumerate(candidate_users[:2], 1):
    print(f"  Candidate {i}: {user.username} / demo123456")
for i, user in enumerate(recruiter_users[:2], 1):
    print(f"  Recruiter {i}: {user.username} / demo123456")

print(f"\n🌐 ACCESS THE APPLICATION:")
print(f"  URL: http://127.0.0.1:8000/")
print(f"  • Login to explore all 19 features")
print(f"  • Browse jobs, post positions, manage candidates")
print(f"  • View analytics, assessments, interviews")
print(f"  • Everything is ready to use!")

