"""
AI Intelligence Engine for TalentSleuth
Provides candidate scoring, matching, and insight generation
"""
from django.db.models import Q
from decimal import Decimal
import re


class TalentSleuthAI:
    """Main AI engine for candidate intelligence"""
    
    @staticmethod
    def calculate_skill_match_score(candidate, job):
        """
        Calculate how well candidate's skills match job requirements
        Returns score 0-100
        """
        required_skills = job.get_required_skills_list()
        if not required_skills:
            return 50  # Neutral score if no requirements specified
        
        candidate_skills = {
            skill.name.lower(): skill for skill in candidate.skills.all()
        }
        
        total_score = 0
        proficiency_weights = {
            'expert': 1.0,
            'advanced': 0.85,
            'intermediate': 0.65,
            'beginner': 0.4,
        }
        
        for required_skill in required_skills:
            skill_lower = required_skill.lower()
            if skill_lower in candidate_skills:
                # Found the skill - weight by proficiency
                skill_obj = candidate_skills[skill_lower]
                weight = proficiency_weights.get(skill_obj.proficiency, 0.5)
                total_score += weight
        
        # Calculate percentage
        match_percentage = (total_score / len(required_skills)) * 100
        return min(100, int(match_percentage))
    
    @staticmethod
    def calculate_experience_match_score(candidate, job):
        """
        Calculate how well candidate's experience matches job requirements
        Returns score 0-100
        """
        candidate_years = candidate.years_of_experience
        required_years = job.min_experience_years
        
        if candidate_years >= required_years * Decimal('1.5'):
            # Over-qualified
            return 95
        elif candidate_years >= required_years:
            # Meets or exceeds requirements
            return 100
        elif candidate_years >= required_years * Decimal('0.75'):
            # Close to requirements
            return 80
        elif candidate_years >= required_years * Decimal('0.5'):
            # Somewhat below requirements
            return 60
        else:
            # Significantly under-qualified
            return max(20, int((candidate_years / required_years) * 50))
    
    @staticmethod
    def calculate_overall_match_score(candidate, job):
        """
        Calculate overall match score for candidate-job pair
        Returns score 0-100
        """
        skill_score = TalentSleuthAI.calculate_skill_match_score(candidate, job)
        experience_score = TalentSleuthAI.calculate_experience_match_score(candidate, job)
        
        # Weighted average: 60% skills, 40% experience
        overall = (skill_score * 0.6) + (experience_score * 0.4)
        return int(overall)
    
    @staticmethod
    def generate_insights(application):
        """
        Generate AI insights for an application
        Returns list of insight data dictionaries
        """
        from .models import AIInsight
        
        insights = []
        candidate = application.candidate
        job = application.job
        
        # Insight 1: Skill Match Analysis
        skill_score = application.skill_match_score
        if skill_score >= 80:
            insights.append({
                'type': 'strength',
                'title': 'Excellent Skill Match',
                'description': f'{candidate.full_name} possesses {skill_score}% of the required skills with strong proficiency levels.',
                'confidence': 90
            })
        elif skill_score < 50:
            insights.append({
                'type': 'weakness',
                'title': 'Skill Gap Identified',
                'description': f'Candidate matches only {skill_score}% of required skills. Consider training or alternative candidates.',
                'confidence': 85
            })
        
        # Insight 2: Experience Analysis
        exp_score = application.experience_match_score
        if exp_score >= 90 and candidate.years_of_experience > job.min_experience_years * Decimal('1.5'):
            insights.append({
                'type': 'alert',
                'title': 'Over-Qualified Candidate',
                'description': f'Candidate has {candidate.years_of_experience} years of experience, significantly exceeding the {job.min_experience_years} year requirement. May seek higher compensation.',
                'confidence': 80
            })
        elif exp_score >= 90:
            insights.append({
                'type': 'strength',
                'title': 'Ideal Experience Level',
                'description': f'Candidate\'s {candidate.years_of_experience} years of experience aligns perfectly with job requirements.',
                'confidence': 95
            })
        
        # Insight 3: Overall Recommendation
        overall_score = application.match_score
        if overall_score >= 80:
            insights.append({
                'type': 'recommendation',
                'title': 'Strong Recommendation',
                'description': f'This candidate scores {overall_score}/100 overall. Highly recommended for interview.',
                'confidence': 90
            })
        elif overall_score >= 60:
            insights.append({
                'type': 'recommendation',
                'title': 'Potential Fit',
                'description': f'Candidate shows promise with {overall_score}/100 match score. Consider for screening.',
                'confidence': 75
            })
        else:
            insights.append({
                'type': 'recommendation',
                'title': 'Below Threshold',
                'description': f'Match score of {overall_score}/100 suggests limited alignment with job requirements.',
                'confidence': 85
            })
        
        # Insight 4: Education Check
        education_count = candidate.education.count()
        advanced_degrees = candidate.education.filter(
            degree__in=['master', 'phd']
        ).count()
        
        if advanced_degrees > 0:
            insights.append({
                'type': 'strength',
                'title': 'Advanced Education',
                'description': f'Candidate holds {advanced_degrees} advanced degree(s), demonstrating strong academic background.',
                'confidence': 85
            })
        
        return insights
    
    @staticmethod
    def update_application_scores(application):
        """
        Calculate and update all scores for an application
        """
        candidate = application.candidate
        job = application.job
        
        # Calculate scores
        application.skill_match_score = TalentSleuthAI.calculate_skill_match_score(candidate, job)
        application.experience_match_score = TalentSleuthAI.calculate_experience_match_score(candidate, job)
        application.match_score = TalentSleuthAI.calculate_overall_match_score(candidate, job)
        application.save()
        
        # Generate and save insights
        from .models import AIInsight
        
        # Clear old insights
        application.ai_insights.all().delete()
        
        # Generate new insights
        insight_data_list = TalentSleuthAI.generate_insights(application)
        for insight_data in insight_data_list:
            AIInsight.objects.create(
                application=application,
                insight_type=insight_data['type'],
                title=insight_data['title'],
                description=insight_data['description'],
                confidence_score=insight_data['confidence']
            )
    
    @staticmethod
    def update_candidate_overall_score(candidate):
        """
        Update candidate's overall score based on their applications
        """
        applications = candidate.applications.all()
        if applications.exists():
            avg_score = sum(app.match_score for app in applications) / len(applications)
            candidate.overall_score = int(avg_score)
        else:
            # Base score on completeness of profile
            score = 50  # Base score
            if candidate.skills.exists():
                score += 15
            if candidate.experiences.exists():
                score += 15
            if candidate.education.exists():
                score += 10
            if candidate.resume:
                score += 10
            candidate.overall_score = score
        
        candidate.save()
    
    @staticmethod
    def parse_resume(resume_file):
        """
        Parse uploaded resume and extract information
        Returns dictionary with parsed data or None if parsing fails
        """
        try:
            # Read the file content
            if hasattr(resume_file, 'read'):
                content = resume_file.read()
                # Try to decode if it's bytes
                if isinstance(content, bytes):
                    try:
                        content = content.decode('utf-8')
                    except:
                        # For binary files like PDF, return a message
                        return None
            else:
                # It's a file path
                with open(resume_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Simple text parsing (in production, use proper NLP/AI)
            parsed_data = {
                'summary': '',
                'skills': [],
                'experience': [],
                'education': []
            }
            
            # Basic parsing logic
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect sections
                lower_line = line.lower()
                if 'summary' in lower_line or 'objective' in lower_line or 'profile' in lower_line:
                    current_section = 'summary'
                    continue
                elif 'skills' in lower_line or 'technologies' in lower_line:
                    current_section = 'skills'
                    continue
                elif 'experience' in lower_line or 'work' in lower_line:
                    current_section = 'experience'
                    continue
                elif 'education' in lower_line or 'qualification' in lower_line:
                    current_section = 'education'
                    continue
                
                # Parse content based on section
                if current_section == 'summary' and len(parsed_data['summary']) < 500:
                    parsed_data['summary'] += line + ' '
                elif current_section == 'skills':
                    # Split by common delimiters
                    skills = [s.strip() for s in line.replace(',', ';').split(';') if s.strip()]
                    parsed_data['skills'].extend(skills)
                elif current_section == 'experience':
                    if len(parsed_data['experience']) < 5:  # Limit to 5 experiences
                        parsed_data['experience'].append(line)
                elif current_section == 'education':
                    if len(parsed_data['education']) < 3:  # Limit to 3 education entries
                        parsed_data['education'].append(line)
            
            # Clean up
            parsed_data['summary'] = parsed_data['summary'].strip()
            parsed_data['skills'] = list(set(parsed_data['skills']))  # Remove duplicates
            
            return parsed_data
            
        except Exception as e:
            print(f"Resume parsing error: {e}")
            return None
