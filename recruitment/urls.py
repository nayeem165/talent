from django.urls import path
from . import views

urlpatterns = [
    # Home and auth
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    
    # Candidate pages
    path('candidate/profile/', views.candidate_profile, name='candidate_profile'),
    path('candidate/add-skill/', views.add_skill, name='add_skill'),
    path('candidate/add-experience/', views.add_experience, name='add_experience'),
    path('candidate/job-alerts/', views.manage_job_alerts, name='manage_job_alerts'),
    path('candidate/job-alerts/<int:alert_id>/delete/', views.delete_job_alert, name='delete_job_alert'),
    path('candidate/job-alerts/<int:alert_id>/toggle/', views.toggle_job_alert, name='toggle_job_alert'),
    path('candidate/recommended-jobs/', views.recommended_jobs, name='recommended_jobs'),
    
    # Saved Jobs
    path('candidate/saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('jobs/<int:job_id>/save/', views.toggle_save_job, name='toggle_save_job'),
    
    # Recent Searches
    path('candidate/recent-searches/', views.recent_searches, name='recent_searches'),
    path('candidate/clear-searches/', views.clear_searches, name='clear_searches'),
    
    # Messaging
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/', views.compose_message, name='compose_message'),
    path('messages/<int:message_id>/', views.view_message, name='view_message'),
    
    # Company Reviews
    path('company/<int:company_id>/reviews/', views.company_reviews, name='company_reviews'),
    path('company/<int:company_id>/reviews/write/', views.write_company_review, name='write_company_review'),
    path('company/<int:company_id>/follow/', views.follow_company, name='follow_company'),
    
    # Interviews
    path('interview/<int:application_id>/schedule/', views.schedule_interview, name='schedule_interview'),
    path('candidate/interviews/', views.my_interviews, name='my_interviews'),
    
    # Skill Assessments
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('assessments/<int:assessment_id>/take/', views.take_assessment, name='take_assessment'),
    path('assessments/results/', views.assessment_results, name='assessment_results'),
    path('recruiter/assessments/create/', views.create_assessment, name='create_assessment'),
    path('recruiter/assessments/manage/', views.manage_assessments, name='manage_assessments'),
    
    # Resume Builder
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    
    # Salary Estimator
    path('salary-estimator/', views.salary_estimator, name='salary_estimator'),
    
    # Premium Membership
    path('premium/', views.premium_plans, name='premium_plans'),
    path('premium/upgrade/<str:plan>/', views.upgrade_premium, name='upgrade_premium'),
    
    # Application Analytics
    path('candidate/analytics/', views.application_analytics, name='application_analytics'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Job pages
    path('jobs/', views.job_listings, name='job_listings'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/search/chat/', views.job_search_chat, name='job_search_chat'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    
    # Recruiter pages
    path('recruiter/dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recruiter/create-job/', views.create_job, name='create_job'),
    path('recruiter/company-profile/', views.company_profile, name='company_profile'),
    path('recruiter/job/<int:job_id>/applications/', views.view_applications, name='view_applications'),
    path('recruiter/job/<int:job_id>/resume-ranking/', views.resume_ranking, name='resume_ranking'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    
    # ==================== MISSING FEATURES URLS ====================
    
    # Resume Parsing
    path('candidate/parse-resume/', views.parse_resume, name='parse_resume'),
    
    # Quick Apply
    path('jobs/<int:job_id>/quick-apply/', views.quick_apply, name='quick_apply'),
    
    # Interview Questions
    path('interview/questions/', views.interview_questions, name='interview_questions'),
    path('interview/questions/<int:question_id>/bookmark/', views.bookmark_interview_question, name='bookmark_interview_question'),
    path('candidate/interview-bookmarks/', views.my_interview_bookmarks, name='my_interview_bookmarks'),
    path('interview/practice/', views.practice_interview_questions, name='practice_interview_questions'),
    path('interview/question/<int:question_id>/answer/', views.submit_question_answer, name='submit_question_answer'),
    path('candidate/interview-answers/', views.my_interview_answers, name='my_interview_answers'),
    path('interview/answer/<int:answer_id>/edit/', views.edit_question_answer, name='edit_question_answer'),
    path('interview/answer/<int:answer_id>/delete/', views.delete_question_answer, name='delete_question_answer'),
    
    # Certifications
    path('candidate/certifications/', views.manage_certifications, name='manage_certifications'),
    path('certifications/<int:certification_id>/verify/', views.verify_certification, name='verify_certification'),
    
    # Employee Referrals
    path('recruiter/referral-dashboard/', views.referral_dashboard, name='referral_dashboard'),
    path('recruiter/referral/submit/', views.submit_referral, name='submit_referral'),
    path('recruiter/referrals/manage/', views.manage_referrals, name='manage_referrals'),
    
    # ATS Integrations
    path('recruiter/ats-integrations/', views.ats_integrations, name='ats_integrations'),
    path('recruiter/ats/<int:integration_id>/sync/', views.sync_ats, name='sync_ats'),
    
    # Background Checks
    path('candidate/background-checks/', views.background_checks, name='background_checks'),
    path('recruiter/background-check/initiate/', views.initiate_background_check, name='initiate_background_check'),
    path('recruiter/background-check/<int:check_id>/update/', views.update_background_check, name='update_background_check'),
    
    # Advanced Candidate Search
    path('recruiter/candidates/search/', views.advanced_candidate_search, name='advanced_candidate_search'),
    path('recruiter/searches/saved/', views.saved_searches, name='saved_searches'),
    path('recruiter/searches/<int:search_id>/run/', views.run_saved_search, name='run_saved_search'),
]