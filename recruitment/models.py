from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Candidate(models.Model):
    """Model representing a candidate/job seeker"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Professional information
    current_role = models.CharField(max_length=200, blank=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Resume and profile
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    summary = models.TextField(blank=True, help_text="Professional summary")
    
    # AI Scoring fields
    overall_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-calculated overall candidate score"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Profile visibility settings (like Naukri's Open/Closed profile)
    PROFILE_VISIBILITY_CHOICES = [
        ('open', 'Open to Opportunities'),
        ('closed', 'Not Looking for Jobs'),
        ('hidden', 'Hidden from Employers'),
    ]
    profile_visibility = models.CharField(max_length=20, choices=PROFILE_VISIBILITY_CHOICES, default='open')
    
    class Meta:
        ordering = ['-overall_score', '-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage like Naukri"""
        total_fields = 10
        completed = 0
        
        if self.full_name:
            completed += 1
        if self.email:
            completed += 1
        if self.phone:
            completed += 1
        if self.location:
            completed += 1
        if self.current_role:
            completed += 1
        try:
            years_exp = float(self.years_of_experience) if self.years_of_experience else 0
            if years_exp > 0:
                completed += 1
        except (TypeError, ValueError):
            try:
                if str(self.years_of_experience).strip() and str(self.years_of_experience).strip() != '0':
                    completed += 1
            except:
                pass
        if self.resume:
            completed += 1
        if self.skills.exists():
            completed += 1
        if self.experiences.exists():
            completed += 1
        if self.education.exists():
            completed += 1
        
        return int((completed / total_fields) * 100)


class Skill(models.Model):
    """Skills possessed by candidates"""
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')
    years_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    
    class Meta:
        unique_together = ['candidate', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.proficiency}"


class Experience(models.Model):
    """Work experience of candidates"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Education(models.Model):
    """Educational qualifications"""
    DEGREE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', 'Ph.D.'),
        ('certification', 'Certification'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=50, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-end_date']
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"


class Job(models.Model):
    """Job postings by recruiters"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    REMOTE_CHOICES = [
        ('no', 'No Remote'),
        ('partial', 'Partial Remote'),
        ('full', 'Fully Remote'),
        ('hybrid', 'Hybrid'),
    ]
    
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    
    # Compensation
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    
    # Required qualifications
    min_experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    required_skills = models.TextField(help_text="Comma-separated list of required skills")
    
    # Remote work option
    remote_type = models.CharField(max_length=20, choices=REMOTE_CHOICES, default='no')
    
    # Additional features from migration 0005
    blind_hiring_enabled = models.BooleanField(default=False)
    fair_pay_badge = models.BooleanField(default=False)
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_required_skills_list(self):
        """Return required skills as a list"""
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]


class Application(models.Model):
    """Job applications submitted by candidates"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('offered', 'Offer Extended'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # Application details
    cover_letter = models.TextField(blank=True)
    custom_resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # AI Scoring
    match_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-calculated job match score"
    )
    skill_match_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    experience_match_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Notes
    recruiter_notes = models.TextField(blank=True)
    
    # Additional from migration 0005
    keep_profile_visible_on_withdrawal = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-match_score', '-applied_at']
        unique_together = ['candidate', 'job']
    
    def __str__(self):
        return f"{self.candidate.full_name} → {self.job.title}"


class AIInsight(models.Model):
    """AI-generated insights for applications"""
    INSIGHT_TYPE_CHOICES = [
        ('strength', 'Strength'),
        ('weakness', 'Weakness'),
        ('recommendation', 'Recommendation'),
        ('alert', 'Alert'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='ai_insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI confidence in this insight (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.insight_type}: {self.title}"


class JobAlert(models.Model):
    """Job alerts for candidates - notifies when matching jobs are posted"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='job_alerts')
    keywords = models.CharField(max_length=500, help_text="Comma-separated keywords to match")
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Alert for {self.keywords} in {self.location or 'Any location'}"


class EmailNotification(models.Model):
    """Track all email notifications sent to users"""
    NOTIFICATION_TYPE_CHOICES = [
        ('application_confirmation', 'Application Confirmation'),
        ('status_update', 'Status Update'),
        ('job_alert', 'Job Alert'),
        ('interview_invite', 'Interview Invitation'),
        ('job_offer', 'Job Offer'),
    ]
    
    recipient = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    related_job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True, related_name='notifications')
    sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.subject}"


class CompanyProfile(models.Model):
    """Company profile for recruiters - showcases company culture and details"""
    SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    ]
    
    recruiter = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    founded_year = models.IntegerField(blank=True, null=True)
    benefits = models.TextField(blank=True)
    culture = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_average_rating(self):
        """Calculate average company rating"""
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


# ==================== MISSING FEATURES MODELS ====================

class SavedJob(models.Model):
    """Jobs bookmarked/saved by candidates for later"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-saved_at']
        unique_together = ['candidate', 'job']
    
    def __str__(self):
        return f"{self.candidate.full_name} saved {self.job.title}"


class RecentSearch(models.Model):
    """Recent search history for candidates"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='recent_searches')
    search_query = models.CharField(max_length=500)
    location = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(max_length=20, blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
    
    def __str__(self):
        return f"{self.candidate.full_name} searched: {self.search_query}"


class InterviewSchedule(models.Model):
    """Interview scheduling for candidates"""
    INTERVIEW_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    interview_type = models.CharField(max_length=20, choices=[
        ('phone', 'Phone'),
        ('video', 'Video'),
        ('onsite', 'On-site'),
    ], default='video')
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=INTERVIEW_STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
    
    def __str__(self):
        return f"Interview for {self.application.candidate.full_name} - {self.scheduled_date}"


class CompanyReview(models.Model):
    """Company reviews and ratings by candidates/employees"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='company_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    pros = models.TextField(blank=True)
    cons = models.TextField(blank=True)
    advice = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    is_verified_employee = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['company', 'reviewer']
    
    def __str__(self):
        return f"Review of {self.company.name} by {self.reviewer.full_name}"


class CompanyFollow(models.Model):
    """Candidates following companies"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='following_companies')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-followed_at']
        unique_together = ['candidate', 'company']
    
    def __str__(self):
        return f"{self.candidate.full_name} follows {self.company.name}"


class ResumeTemplate(models.Model):
    """Resume builder templates"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_code = models.CharField(max_length=50, unique=True)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CandidateResume(models.Model):
    """Resume builder - saved resumes for candidates"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='built_resumes')
    template = models.ForeignKey(ResumeTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    content_json = models.TextField(help_text="JSON storing resume sections")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', '-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.candidate.full_name}"


class SalaryData(models.Model):
    """Salary data for salary estimator feature"""
    job_title = models.CharField(max_length=200)
    company_size = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20)
    experience_level = models.CharField(max_length=50)
    salary_min = models.IntegerField()
    salary_max = models.IntegerField()
    salary_median = models.IntegerField()
    currency = models.CharField(max_length=3, default='USD')
    sample_size = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['job_title', 'location']
    
    def __str__(self):
        return f"{self.job_title} in {self.location}: {self.salary_median}"


# ==================== MISSING FEATURES - NEW MODELS ====================

class Certification(models.Model):
    """Candidate certifications"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=200, blank=True)
    credential_url = models.URLField(blank=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.name} - {self.candidate.full_name}"


class CertificationVerification(models.Model):
    """Track certification verification status"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
        ('expired', 'Expired'),
    ]
    
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='verifications')
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.CharField(max_length=200, blank=True)
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.certification.name} - {self.status}"


class Referral(models.Model):
    """Employee referral management system"""
    REFERRAL_STATUS = [
        ('pending', 'Pending Review'),
        ('interviewing', 'Interviewing'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('bonus_paid', 'Bonus Paid'),
    ]
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='referrals_received')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='referrals', blank=True, null=True)
    resume = models.FileField(upload_to='referral_resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REFERRAL_STATUS, default='pending')
    referral_notes = models.TextField(blank=True)
    is_quick_apply = models.BooleanField(default=False, help_text="Quick resume one-click apply")
    referred_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-referred_at']
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_candidate.full_name}"


class ReferralBonus(models.Model):
    """Track referral bonuses for employees"""
    BONUS_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name='bonuses')
    amount = models.IntegerField(default=500)
    status = models.CharField(max_length=20, choices=BONUS_STATUS, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_bonuses')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bonus ${self.amount} for {self.referral.referrer.username}"


class CandidateSearchProfile(models.Model):
    """Advanced search profile for recruiters to save searches"""
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    
    # Search criteria
    keywords = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    min_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    max_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    employment_type = models.CharField(max_length=20, blank=True)
    min_salary = models.IntegerField(blank=True, null=True)
    max_salary = models.IntegerField(blank=True, null=True)
    company_sizes = models.TextField(blank=True, help_text="Comma-separated company sizes")
    education_levels = models.TextField(blank=True, help_text="Comma-separated education levels")
    profile_visibility = models.CharField(max_length=20, default='open')
    
    # Notification settings
    notify_on_new = models.BooleanField(default=False)
    notify_frequency = models.CharField(max_length=20, choices=[
        ('instant', 'Instant'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='daily')
    
    last_run = models.DateTimeField(blank=True, null=True)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.recruiter.username}"

