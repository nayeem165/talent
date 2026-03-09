from django.contrib import admin
from .models import Candidate, Skill, Experience, Education, Job, Application, AIInsight


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'current_role', 'years_of_experience', 'overall_score', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'email', 'current_role']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'candidate', 'proficiency', 'years_experience']
    list_filter = ['proficiency']
    search_fields = ['name', 'candidate__full_name']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'candidate', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['job_title', 'company', 'candidate__full_name']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'field_of_study', 'institution', 'candidate', 'end_date']
    list_filter = ['degree']
    search_fields = ['institution', 'field_of_study', 'candidate__full_name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'employment_type', 'status', 'created_at']
    list_filter = ['employment_type', 'status', 'created_at']
    search_fields = ['title', 'company', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'match_score', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['candidate__full_name', 'job__title']
    readonly_fields = ['applied_at', 'updated_at']


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['application', 'insight_type', 'title', 'confidence_score', 'created_at']
    list_filter = ['insight_type', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
