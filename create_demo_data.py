"""
Demo data script for TalentSleuth AI
Run this to populate the database with sample data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talentsleuth.settings')
django.setup()

from django.contrib.auth.models import User
from recruitment.models import Candidate, Job, Application, Skill, Experience, Education
from recruitment.ai_engine import TalentSleuthAI
from datetime import date, timedelta
from decimal import Decimal

def create_demo_data():
    print("Creating demo data for TalentSleuth AI...")
    
    # Create a recruiter
    recruiter, created = User.objects.get_or_create(
        username='recruiter1',
        defaults={
            'email': 'recruiter@company.com',
            'is_staff': True
        }
    )
    if created:
        recruiter.set_password('password123')
        recruiter.save()
        print("✓ Created recruiter user")
    
    # Create candidate users
    candidates_data = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'full_name': 'John Doe',
            'current_role': 'Senior Python Developer',
            'years_of_experience': Decimal('5.5'),
            'location': 'San Francisco, CA',
            'summary': 'Experienced Python developer with expertise in Django, FastAPI, and cloud technologies.',
            'skills': [
                ('Python', 'expert', 5),
                ('Django', 'advanced', 4),
                ('PostgreSQL', 'advanced', 3),
                ('React', 'intermediate', 2),
                ('Docker', 'advanced', 3),
            ],
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'full_name': 'Jane Smith',
            'current_role': 'Full Stack Engineer',
            'years_of_experience': Decimal('3.0'),
            'location': 'New York, NY',
            'summary': 'Full-stack developer passionate about building scalable web applications.',
            'skills': [
                ('JavaScript', 'expert', 3),
                ('React', 'expert', 3),
                ('Node.js', 'advanced', 2.5),
                ('Python', 'intermediate', 1),
                ('AWS', 'intermediate', 1.5),
            ],
        },
        {
            'username': 'mike_johnson',
            'email': 'mike@example.com',
            'full_name': 'Mike Johnson',
            'current_role': 'DevOps Engineer',
            'years_of_experience': Decimal('7.0'),
            'location': 'Austin, TX',
            'summary': 'DevOps specialist with strong automation and cloud infrastructure experience.',
            'skills': [
                ('Kubernetes', 'expert', 4),
                ('Docker', 'expert', 5),
                ('AWS', 'expert', 6),
                ('Python', 'advanced', 4),
                ('Terraform', 'advanced', 3),
            ],
        },
    ]
    
    for cand_data in candidates_data:
        user, created = User.objects.get_or_create(
            username=cand_data['username'],
            defaults={'email': cand_data['email']}
        )
        if created:
            user.set_password('password123')
            user.save()
        
        candidate, created = Candidate.objects.get_or_create(
            user=user,
            defaults={
                'full_name': cand_data['full_name'],
                'email': cand_data['email'],
                'current_role': cand_data['current_role'],
                'years_of_experience': cand_data['years_of_experience'],
                'location': cand_data['location'],
                'summary': cand_data['summary'],
            }
        )
        
        if created:
            # Add skills
            for skill_name, proficiency, years in cand_data['skills']:
                Skill.objects.create(
                    candidate=candidate,
                    name=skill_name,
                    proficiency=proficiency,
                    years_experience=years
                )
            
            # Add experience
            Experience.objects.create(
                candidate=candidate,
                company='Tech Corp',
                job_title=cand_data['current_role'],
                location=cand_data['location'],
                start_date=date.today() - timedelta(days=int(cand_data['years_of_experience'] * 365)),
                is_current=True,
                description='Building amazing software products.'
            )
            
            # Add education
            Education.objects.create(
                candidate=candidate,
                institution='State University',
                degree='bachelor',
                field_of_study='Computer Science',
                start_date=date(2015, 9, 1),
                end_date=date(2019, 5, 15),
                grade='3.8 GPA'
            )
            
            TalentSleuthAI.update_candidate_overall_score(candidate)
            print(f"✓ Created candidate: {candidate.full_name}")
    
    # Create jobs
    jobs_data = [
        {
            'title': 'Senior Django Developer',
            'company': 'TechCorp Inc.',
            'location': 'San Francisco, CA',
            'employment_type': 'full_time',
            'description': 'We are looking for an experienced Django developer to join our growing team. You will be responsible for building scalable web applications.',
            'requirements': '- 5+ years of Python/Django experience\n- Strong PostgreSQL knowledge\n- Experience with REST APIs\n- Docker/containerization experience',
            'responsibilities': '- Design and implement new features\n- Optimize database queries\n- Mentor junior developers\n- Code reviews',
            'min_experience_years': Decimal('5.0'),
            'required_skills': 'Python, Django, PostgreSQL, Docker, REST APIs',
            'salary_min': 120000,
            'salary_max': 180000,
            'status': 'published',
        },
        {
            'title': 'Full Stack Engineer',
            'company': 'StartupXYZ',
            'location': 'Remote',
            'employment_type': 'full_time',
            'description': 'Join our fast-paced startup as a full-stack engineer. Work on exciting projects with modern technologies.',
            'requirements': '- 3+ years full-stack development\n- React and Node.js proficiency\n- Experience with cloud platforms\n- Agile methodology experience',
            'responsibilities': '- Build frontend and backend features\n- Collaborate with designers\n- Deploy to cloud infrastructure',
            'min_experience_years': Decimal('3.0'),
            'required_skills': 'React, JavaScript, Node.js, AWS, Python',
            'salary_min': 100000,
            'salary_max': 140000,
            'status': 'published',
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudSystems Ltd',
            'location': 'Austin, TX',
            'employment_type': 'full_time',
            'description': 'Looking for a DevOps engineer to manage our cloud infrastructure and CI/CD pipelines.',
            'requirements': '- 5+ years DevOps experience\n- Kubernetes and Docker expert\n- AWS/cloud infrastructure\n- Infrastructure as Code (Terraform)',
            'responsibilities': '- Manage Kubernetes clusters\n- Build CI/CD pipelines\n- Monitor system performance\n- Automate infrastructure provisioning',
            'min_experience_years': Decimal('5.0'),
            'required_skills': 'Kubernetes, Docker, AWS, Terraform, Python',
            'salary_min': 130000,
            'salary_max': 170000,
            'status': 'published',
        },
    ]
    
    for job_data in jobs_data:
        job, created = Job.objects.get_or_create(
            title=job_data['title'],
            recruiter=recruiter,
            defaults=job_data
        )
        if created:
            print(f"✓ Created job: {job.title}")
    
    # Create applications
    jobs = Job.objects.filter(status='published')
    candidates = Candidate.objects.all()
    
    for job in jobs:
        for candidate in candidates[:2]:  # Each job gets 2 applications
            app, created = Application.objects.get_or_create(
                candidate=candidate,
                job=job,
                defaults={
                    'cover_letter': f'I am very interested in the {job.title} position. My skills align perfectly with your requirements.',
                    'status': 'submitted'
                }
            )
            if created:
                # Calculate AI scores
                TalentSleuthAI.update_application_scores(app)
                print(f"✓ Created application: {candidate.full_name} → {job.title} (Score: {app.match_score})")
    
    print("\n✅ Demo data created successfully!")
    print("\nLogin credentials:")
    print("Recruiter - Username: recruiter1, Password: password123")
    print("Candidates - Username: john_doe/jane_smith/mike_johnson, Password: password123")
    print("Admin - Username: admin, Password: admin123")

if __name__ == '__main__':
    create_demo_data()
