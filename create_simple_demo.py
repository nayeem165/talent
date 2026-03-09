#!/usr/bin/env python
"""
Create simple demo data for TalentSleuth AI - Focuses on essentials only
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentsleuth.settings')
django.setup()

from django.contrib.auth.models import User
from recruitment.models import (
    Candidate, Job, Application, Skill, CompanyProfile
)
from datetime import datetime, timedelta
from django.utils import timezone

print("🚀 Creating simple demo data...\n")

# Clear existing demo data
print("📋 Clearing existing data...")
User.objects.filter(username__startswith='demo_').delete()
User.objects.filter(username__startswith='recruiter_').delete()

# CREATE TEST USERS
print("\n👥 Creating demo users...")

# Create 3 candidate users  
candidates = []
for i in range(1, 4):
    user = User.objects.create_user(
        username=f'demo_candidate_{i}',
        email=f'candidate{i}@example.com',
        password='demo123456',
        first_name=f'Candidate',
        last_name=f'{i}',
        is_staff=False
    )
    candidates.append(user)
    print(f"  ✓ Created candidate: {user.username} / demo123456")

# Create 2 recruiter users
recruiters = []
for i in range(1, 3):
    user = User.objects.create_user(
        username=f'recruiter_{i}',
        email=f'recruiter{i}@company.com',
        password='demo123456',
        first_name=f'Recruiter',
        last_name=f'{i}',
        is_staff=True
    )
    recruiters.append(user)
    print(f"  ✓ Created recruiter: {user.username} / demo123456")

# CREATE CANDIDATE PROFILES
print("\n📝 Creating candidate profiles...")

candidate_profiles = []
for i, user in enumerate(candidates):
    candidate = Candidate.objects.create(
        user=user,
        full_name=f'Candidate {i+1}',
        email=user.email,
        phone=f'555-010{i}',
        location='New York, NY',
        current_role='Software Engineer',
        summary='Experienced developer with full stack skills',
        years_of_experience=3 + i,
        is_active=True,
        overall_score=75
    )
    candidate_profiles.append(candidate)
    print(f"  ✓ Created profile: {candidate.full_name}")

# ADD SKILLS
print("\n🎯 Adding skills...")

for candidate in candidate_profiles:
    for skill_name in ['Python', 'JavaScript', 'React']:
        Skill.objects.create(
            candidate=candidate,
            name=skill_name,
            proficiency='Expert',
            years_experience=candidate.years_of_experience
        )
    print(f"  ✓ Skills added to {candidate.full_name}")

# CREATE COMPANY PROFILES
print("\n🏢 Creating company profiles...")

companies = []
for i, recruiter in enumerate(recruiters):
    company = CompanyProfile.objects.create(
        recruiter=recruiter,
        name=f'Tech Company {i+1}',
        industry='Software',
        website=f'https://company{i+1}.com',
        description='Leading tech company',
        size='50-100',
        headquarters='San Francisco',
        founded_year=2015
    )
    companies.append(company)
    print(f"  ✓ Created company: {company.name}")

# CREATE JOBS
print("\n📢 Creating job postings...")

jobs = []
job_titles = ['Senior Engineer', 'Full Stack Developer', 'DevOps Engineer']

for company in companies:
    for j, title in enumerate(job_titles[:2]):
        job = Job.objects.create(
            recruiter=company.recruiter,
            company=company.name,
            title=title,
            description=f'Exciting {title} role at {company.name}',
            requirements='5+ years experience, strong coding skills',
            responsibilities='Build and maintain scalable systems',
            location='New York, NY',
            salary_min=80000,
            salary_max=150000,
            salary_currency='USD',
            employment_type='full_time',
            required_skills='Python, Django, PostgreSQL',
            min_experience_years=2,
            remote_type='hybrid',
            status='published',
            deadline=(timezone.now() + timedelta(days=30)).date()
        )
        jobs.append(job)
        print(f"  ✓ Created job: {job.title} at {company.name}")

# CREATE APPLICATIONS
print("\n📨 Creating applications...")

for job in jobs[:4]:
    for candidate in candidate_profiles[:2]:
        app = Application.objects.create(
            candidate=candidate,
            job=job,
            status='under_review',
            match_score=75,
            skill_match_score=80,
            experience_match_score=70
        )
    print(f"  ✓ Applications created for {job.title}")

# SUMMARY
print("\n" + "="*60)
print("✨ DEMO DATA READY! ✨")
print("="*60)

print(f"\n📊 DATABASE SUMMARY:")
print(f"  • Candidates: {Candidate.objects.count()}")
print(f"  • Companies: {CompanyProfile.objects.count()}")
print(f"  • Jobs: {Job.objects.count()}")
print(f"  • Applications: {Application.objects.count()}")
print(f"  • Skills: {Skill.objects.count()}")

print(f"\n🔑 TEST ACCOUNTS:")
print(f"  Candidate: demo_candidate_1 / demo123456")
print(f"  Recruiter: recruiter_1 / demo123456")

print(f"\n🌐 ACCESS:")
print(f"  URL: http://127.0.0.1:8000/")
print(f"  • Click Login button")
print(f"  • Use any test account above")
print(f"  • Explore all 19 features!")

print(f"\n✨ Ready to use! Open browser at http://127.0.0.1:8000/")

