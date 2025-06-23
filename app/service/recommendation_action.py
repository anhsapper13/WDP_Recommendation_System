import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

from app.models.survey_attempt import SurveyAttempt
from app.models.course import Course
from app.models.consultant import Consultant
from app.models.course_enrollment import CourseEnrollment
from app.models.appointment import Appointment
from app.models.user import User
from app.models.risk_assessment_rule import RiskAssessmentRule

class CRAFFTASSISTRecommendationSystem:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        
    def get_user_survey_data(self) -> pd.DataFrame:
        """Lấy dữ liệu khảo sát của người dùng qua SQLAlchemy ORM"""
        try:
            # Sử dụng raw SQL với table names chính xác
            survey_data = self.db.execute(text("""
                SELECT 
                    sa.user_id,
                    sa.test_survey_id,
                    sa.total_score,
                    sa.risk_level,
                    sa.completed_at,
                    u.first_name,
                    u.last_name,
                    u.age
                FROM "Survey_Attempts" sa
                JOIN "Users" u ON sa.user_id = u.id
                WHERE u.is_deleted = false
                ORDER BY sa.completed_at DESC
            """)).fetchall()
            print(f"Found {len(survey_data)} survey records")
            
            # Bước 2: Chuyển đổi thành list of dictionaries
            data_list = []
            for row in survey_data:
                data_list.append({
                    'user_id': row.user_id,
                    'test_survey_id': row.test_survey_id,
                    'total_score': row.total_score,
                    'risk_level': row.risk_level,
                    'completed_at': row.completed_at,
                    'first_name': row.first_name,
                    'last_name': row.last_name,
                    'age': row.age
                })
            
            # Bước 3: Tạo DataFrame từ data
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"Error in get_user_survey_data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def get_courses_data(self) -> pd.DataFrame:
        """Lấy dữ liệu khóa học qua SQLAlchemy ORM"""
        try:
            # Sử dụng raw SQL với table names chính xác
            courses_data = self.db.execute(text("""
                SELECT 
                    c.id,
                    c.title,
                    c.description,
                    c.target_audience,
                    c.duration_minutes,
                    c.status,
                    c.category_id,
                    COALESCE(ce.enrollment_count, 0) as enrollment_count
                FROM "Course" c
                LEFT JOIN (
                    SELECT 
                        course_id,
                        COUNT(*) as enrollment_count
                    FROM "Course_Enrollment"
                    GROUP BY course_id
                ) ce ON c.id = ce.course_id
                ORDER BY c.created_at DESC
            """)).fetchall()
            
            print(f"Found {len(courses_data)} course records")
            
            # Bước 2: Chuyển đổi SQLAlchemy result thành list of dictionaries
            data_list = []
            for row in courses_data:
                data_list.append({
                    'id': row.id,
                    'title': row.title,
                    'description': row.description,
                    'target_audience': row.target_audience,
                    'duration_minutes': row.duration_minutes,
                    'status': row.status,
                    'category_id': row.category_id,
                    'enrollment_count': row.enrollment_count
                })
            
            # Bước 3: Tạo DataFrame từ data
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"Error in get_courses_data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def get_consultants_data(self) -> pd.DataFrame:
        """Lấy dữ liệu chuyên viên tư vấn qua SQLAlchemy ORM"""
        try:
            # Sử dụng raw SQL với table names chính xác
            consultants_data = self.db.execute(text("""
                SELECT 
                    c.id,
                    c.specialization,
                    c.qualifications,
                    c.experience_years,
                    c.bio,
                    c.is_available,
                    u.first_name,
                    u.last_name,
                    COALESCE(app.total_appointments, 0) as total_appointments
                FROM "Consultants" c
                JOIN "Users" u ON c.user_id = u.id
                LEFT JOIN (
                    SELECT 
                        "consultantId",
                        COUNT(*) as total_appointments
                    FROM "Appointments"
                    WHERE is_deleted = false
                    GROUP BY "consultantId"
                ) app ON c.id = app."consultantId"
                WHERE c.is_available = true
                ORDER BY c.created_at DESC
            """)).fetchall()
            
            print(f"Found {len(consultants_data)} consultant records")
            
            # Bước 2: Chuyển đổi SQLAlchemy result thành list of dictionaries
            data_list = []
            for row in consultants_data:
                data_list.append({
                    'id': row.id,
                    'specialization': row.specialization,
                    'qualifications': row.qualifications,
                    'experience_years': row.experience_years,
                    'bio': row.bio,
                    'is_available': row.is_available,
                    'full_name': f"{row.first_name} {row.last_name}",
                    'total_appointments': row.total_appointments
                })
            
            # Bước 3: Tạo DataFrame từ data
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"Error in get_consultants_data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def get_user_interactions(self) -> pd.DataFrame:
        """Lấy dữ liệu tương tác của người dùng qua SQLAlchemy ORM"""
        try:
            # Bước 1: Lấy course interactions qua raw SQL
            course_interactions = self.db.execute(text("""
                SELECT 
                    user_id,
                    course_id as item_id,
                    progress_percentage,
                    enrollment_date as interaction_date
                FROM "Course_Enrollment"
            """)).fetchall()
            
            # Bước 2: Lấy appointment interactions qua raw SQL
            appointment_interactions = self.db.execute(text("""
                SELECT 
                    "userId" as user_id,
                    "consultantId" as item_id,
                    status,
                    booking_time as interaction_date
                FROM "Appointments"
                WHERE is_deleted = false
            """)).fetchall()
            
            # Bước 3: Chuyển đổi thành list of dictionaries
            data_list = []
            
            # Course interactions
            for row in course_interactions:
                data_list.append({
                    'user_id': row.user_id,
                    'item_id': row.item_id,
                    'item_type': 'course',
                    'rating': (row.progress_percentage or 0) / 100.0,
                    'interaction_date': row.interaction_date
                })
            
            # Appointment interactions
            for row in appointment_interactions:
                rating = 1.0 if row.status == 'COMPLETED' else 0.5
                data_list.append({
                    'user_id': row.user_id,
                    'item_id': row.item_id,
                    'item_type': 'consultant',
                    'rating': rating,
                    'interaction_date': row.interaction_date
                })
            
            # Bước 4: Tạo DataFrame từ data
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"Error in get_user_interactions: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def create_risk_level_mapping(self) -> Dict[str, Dict]:
        """Tạo mapping giữa risk level và recommendations"""
        return {
            'LOW': {
                'course_difficulty': ['BEGINNER'],
                'course_topics': ['prevention', 'awareness', 'healthy_lifestyle'],
                'consultant_specialization': ['general', 'prevention'],
                'priority_weight': 0.3
            },
            'MEDIUM': {
                'course_difficulty': ['BEGINNER', 'INTERMEDIATE'],
                'course_topics': ['intervention', 'coping_skills', 'family_support'],
                'consultant_specialization': ['intervention', 'family_therapy', 'cognitive_behavioral'],
                'priority_weight': 0.6
            },
            'HIGH': {
                'course_difficulty': ['INTERMEDIATE', 'ADVANCED'],
                'course_topics': ['treatment', 'recovery', 'intensive_support'],
                'consultant_specialization': ['addiction_specialist', 'clinical_psychology', 'psychiatry'],
                'priority_weight': 1.0
            }
        }

    def content_based_course_recommendations(self, user_id: str, top_k: int = 5) -> List[Dict]:
        """Content-based filtering cho khóa học"""
        # Lấy thông tin survey gần nhất của user
        user_surveys = self.get_user_survey_data()
        user_data = user_surveys[user_surveys['user_id'] == user_id]
        
        if user_data.empty:
            return []
            
        user_data = user_data.iloc[0]
        
        courses_df = self.get_courses_data()
        if courses_df.empty:
            return []
            
        risk_mapping = self.create_risk_level_mapping()
        user_risk = user_data['risk_level']
        
        # Tạo feature vector cho courses
        course_features = []
        for _, course in courses_df.iterrows():
            features = f"{course['description']} {course['category']} {course['target_audience']} {course['difficulty_level']}"
            course_features.append(features)
        
        if not course_features:
            return []
        
        # TF-IDF vectorization
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(course_features)
        
        # Tạo user profile dựa trên risk level
        user_profile = " ".join(risk_mapping.get(user_risk, risk_mapping['MEDIUM'])['course_topics'])
        user_vector = self.tfidf_vectorizer.transform([user_profile])
        
        # Tính cosine similarity
        similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
        
        # Áp dụng business rules
        course_scores = []
        for idx, (_, course) in enumerate(courses_df.iterrows()):
            base_score = similarities[idx]
            
            # Boost score dựa trên difficulty level phù hợp
            if course['difficulty_level'] in risk_mapping.get(user_risk, risk_mapping['MEDIUM'])['course_difficulty']:
                base_score *= 1.5
            
            # Boost score dựa trên target audience
            if course['target_audience'] == user_data.get('user_type') or course['target_audience'] == 'GENERAL':
                base_score *= 1.2
            
            # Boost score dựa trên age group
            if course['age_group'] == user_data.get('age_group') or course['age_group'] == 'ALL':
                base_score *= 1.1
            
            course_scores.append({
                'course_id': course['id'],
                'title': course['title'],
                'description': course['description'],
                'score': float(base_score),
                'difficulty_level': course['difficulty_level'],
                'enrollment_count': int(course['enrollment_count']) if course['enrollment_count'] else 0,
                'recommendation_type': 'content_based'
            })
        
        # Sắp xếp và trả về top K
        course_scores.sort(key=lambda x: x['score'], reverse=True)
        return course_scores[:top_k]

    def content_based_consultant_recommendations(self, user_id: str, top_k: int = 3) -> List[Dict]:
        """Content-based filtering cho consultant"""
        user_surveys = self.get_user_survey_data()
        user_data = user_surveys[user_surveys['user_id'] == user_id]
        
        if user_data.empty:
            return []
            
        user_data = user_data.iloc[0]
        
        consultants_df = self.get_consultants_data()
        if consultants_df.empty:
            return []
            
        risk_mapping = self.create_risk_level_mapping()
        user_risk = user_data['risk_level']
        
        consultant_scores = []
        for _, consultant in consultants_df.iterrows():
            base_score = risk_mapping.get(user_risk, risk_mapping['MEDIUM'])['priority_weight']
            
            # Boost score dựa trên specialization
            if consultant['specialization']:
                specializations = consultant['specialization'].lower().split(',')
                for spec in risk_mapping.get(user_risk, risk_mapping['MEDIUM'])['consultant_specialization']:
                    if any(spec in s.strip() for s in specializations):
                        base_score *= 1.5
                        break
            
            # Boost score dựa trên experience
            if consultant['experience_years'] and consultant['experience_years'] >= 5:
                base_score *= 1.2
            
            # Boost score dựa trên availability
            if consultant['is_available']:
                base_score *= 1.1
            
            consultant_scores.append({
                'consultant_id': consultant['id'],
                'name': consultant['full_name'],
                'specialization': consultant['specialization'],
                'experience_years': consultant['experience_years'],
                'consultation_fee': float(consultant['consultation_fee']) if consultant['consultation_fee'] else 0,
                'score': float(base_score),
                'total_appointments': int(consultant['total_appointments']) if consultant['total_appointments'] else 0,
                'recommendation_type': 'content_based'
            })
        
        consultant_scores.sort(key=lambda x: x['score'], reverse=True)
        return consultant_scores[:top_k]

    def collaborative_filtering_recommendations(self, user_id: str, top_k: int = 5) -> Dict:
        """
        Enhanced collaborative filtering cho cả courses và consultants
        Logic: Users tương tự (cùng risk level + behavior) → recommend items tương tự
        """
        try:
            print(f"🤝 Starting enhanced collaborative filtering - User: {user_id}")
            
            # Lấy course recommendations
            course_recommendations = self.collaborative_filtering_course_recommendations(user_id, top_k)
            
            # Lấy consultant recommendations
            consultant_recommendations = self.collaborative_filtering_consultant_recommendations(user_id, min(3, top_k))
            
            # Lấy thông tin risk của user
            user_risk_info = self.get_user_risk_summary(user_id)
            
            return {
                'courses': course_recommendations,
                'consultants': consultant_recommendations,
                'user_risk_info': user_risk_info,
                'recommendation_type': 'collaborative_filtering',
                'recommendation_summary': {
                    'total_courses': len(course_recommendations),
                    'total_consultants': len(consultant_recommendations),
                    'method': 'user_similarity_based'
                },
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Error in collaborative filtering: {str(e)}")
            return {
                'courses': [],
                'consultants': [],
                'user_risk_info': {},
                'status': 'error',
                'message': str(e)
            }

    def collaborative_filtering_course_recommendations(self, user_id: str, top_k: int = 5) -> List[Dict]:
        """Collaborative filtering cho courses sử dụng user similarity"""
        try:
            interactions_df = self.get_user_interactions()
            
            if interactions_df.empty:
                return []
            
            # Tạo user-item matrix cho courses
            course_interactions = interactions_df[interactions_df['item_type'] == 'course']
            
            if course_interactions.empty:
                return []
            
            # Pivot table: user_id x course_id
            user_item_matrix = course_interactions.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating', 
                fill_value=0
            )
            
            if user_id not in user_item_matrix.index:
                return []
            
            # Tính cosine similarity giữa users
            user_similarity = cosine_similarity(user_item_matrix.values)
            user_similarity_df = pd.DataFrame(
                user_similarity, 
                index=user_item_matrix.index, 
                columns=user_item_matrix.index
            )
            
            # Tìm users tương tự (loại bỏ chính user đó)
            similar_users = user_similarity_df[user_id].drop(user_id).sort_values(ascending=False)
            top_similar_users = similar_users.head(5)  # Top 5 similar users
            
            # Lấy courses mà similar users đã rated cao nhưng current user chưa thử
            user_rated_courses = set(course_interactions[course_interactions['user_id'] == user_id]['item_id'])
            
            course_recommendations = []
            courses_df = self.get_courses_data()
            
            for similar_user, similarity_score in top_similar_users.items():
                if similarity_score < 0.1:  # Threshold similarity
                    continue
                    
                similar_user_courses = course_interactions[
                    (course_interactions['user_id'] == similar_user) & 
                    (course_interactions['rating'] >= 0.7)  # High rating courses
                ]['item_id'].tolist()
                
                for course_id in similar_user_courses:
                    if course_id not in user_rated_courses:
                        course_info = courses_df[courses_df['id'] == course_id]
                        if not course_info.empty:
                            course_info = course_info.iloc[0]
                            
                            # Tính predicted rating
                            predicted_rating = similarity_score * 1.0  # Simple prediction
                            
                            course_recommendations.append({
                                'course_id': course_id,
                                'title': course_info['title'],
                                'description': course_info['description'],
                                'predicted_rating': float(predicted_rating),
                                'similarity_score': float(similarity_score),
                                'difficulty_level': course_info['difficulty_level'],
                                'enrollment_count': int(course_info['enrollment_count']) if course_info['enrollment_count'] else 0,
                                'recommendation_type': 'collaborative'
                            })
            
            # Remove duplicates và sort by predicted rating
            seen_courses = set()
            unique_recommendations = []
            for rec in course_recommendations:
                if rec['course_id'] not in seen_courses:
                    seen_courses.add(rec['course_id'])
                    unique_recommendations.append(rec)
            
            unique_recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
            return unique_recommendations[:top_k]
            
        except Exception as e:
            print(f"Error in collaborative course filtering: {str(e)}")
            return []

    def collaborative_filtering_consultant_recommendations(self, user_id: str, top_k: int = 3) -> List[Dict]:
        """
        Collaborative filtering cho consultants dựa trên appointment history
        Logic: Users có cùng risk level book cùng consultant → recommend consultant đó
        """
        try:
            print(f"🤝 Starting collaborative filtering for consultant recommendations - User: {user_id}")
            
            # Bước 1: Lấy risk level của current user
            user_surveys = self.get_user_survey_data()
            current_user_data = user_surveys[user_surveys['user_id'] == user_id]
            
            if current_user_data.empty:
                print(f"❌ No survey data found for user {user_id}")
                return []
            
            current_user_risk = current_user_data.iloc[0]['risk_level']
            print(f"📊 Current user risk level: {current_user_risk}")
            
            # Bước 2: Tìm users có cùng risk level
            users_same_risk = user_surveys[
                (user_surveys['risk_level'] == current_user_risk) &
                (user_surveys['user_id'] != user_id)
            ]['user_id'].unique().tolist()
            
            print(f"👥 Found {len(users_same_risk)} users with same risk level ({current_user_risk})")
            
            if len(users_same_risk) < 2:
                print("⚠️  Not enough users with same risk level for collaborative filtering")
                return []
            
            # Bước 3: Lấy appointment interactions cho users cùng risk level
            interactions_df = self.get_user_interactions()
            consultant_interactions = interactions_df[
                (interactions_df['item_type'] == 'consultant') &
                (interactions_df['user_id'].isin(users_same_risk + [user_id]))
            ]
            
            if consultant_interactions.empty:
                print("❌ No consultant interactions found for similar users")
                return []
            
            print(f"📋 Found {len(consultant_interactions)} consultant interactions")
            
            # Bước 4: Tạo user-consultant matrix
            user_consultant_matrix = consultant_interactions.pivot_table(
                index='user_id',
                columns='item_id', 
                values='rating',
                fill_value=0
            )
            
            print(f"📊 User-consultant matrix shape: {user_consultant_matrix.shape}")
            
            if user_id not in user_consultant_matrix.index:
                print(f"❌ User {user_id} not in consultant interaction matrix")
                return []
            
            # Bước 5: Tính cosine similarity giữa users
            user_similarity = cosine_similarity(user_consultant_matrix.values)
            user_similarity_df = pd.DataFrame(
                user_similarity,
                index=user_consultant_matrix.index,
                columns=user_consultant_matrix.index
            )
            
            # Bước 6: Tìm similar users (loại bỏ chính user đó)
            similar_users = user_similarity_df[user_id].drop(user_id).sort_values(ascending=False)
            top_similar_users = similar_users.head(5)  # Top 5 similar users
            
            print(f"🎯 Top similar users: {dict(top_similar_users.head(3))}")
            
            # Bước 7: Lấy consultants mà current user đã book
            user_booked_consultants = set(
                consultant_interactions[
                    (consultant_interactions['user_id'] == user_id) &
                    (consultant_interactions['rating'] >= 0.5)  # Confirmed/Completed appointments
                ]['item_id']
            )
            
            print(f"📅 User already booked consultants: {list(user_booked_consultants)}")
            
            # Bước 8: Lấy recommendations từ similar users
            consultant_recommendations = []
            consultants_df = self.get_consultants_data()
            
            for similar_user, similarity_score in top_similar_users.items():
                if similarity_score < 0.1:  # Threshold similarity
                    continue
                    
                # Lấy consultants mà similar user đã book với rating cao
                similar_user_consultants = consultant_interactions[
                    (consultant_interactions['user_id'] == similar_user) &
                    (consultant_interactions['rating'] >= 0.8)  # Completed appointments only
                ]['item_id'].tolist()
                
                for consultant_id in similar_user_consultants:
                    # Chỉ recommend consultants mà current user chưa book
                    if consultant_id not in user_booked_consultants:
                        consultant_info = consultants_df[consultants_df['id'] == consultant_id]
                        if not consultant_info.empty:
                            consultant_info = consultant_info.iloc[0]
                            
                            # Tính predicted rating
                            predicted_rating = similarity_score * 1.0
                            
                            consultant_recommendations.append({
                                'consultant_id': consultant_id,
                                'name': consultant_info['full_name'],
                                'specialization': consultant_info['specialization'],
                                'experience_years': consultant_info['experience_years'],
                                'consultation_fee': float(consultant_info['consultation_fee']) if consultant_info['consultation_fee'] else 0,
                                'predicted_rating': float(predicted_rating),
                                'similarity_score': float(similarity_score),
                                'total_appointments': int(consultant_info['total_appointments']) if consultant_info['total_appointments'] else 0,
                                'recommendation_type': 'collaborative',
                                'reason': f"Users with {current_user_risk} risk level also booked this consultant"
                            })
            
            # Bước 9: Remove duplicates và sort by predicted rating
            seen_consultants = set()
            unique_recommendations = []
            for rec in consultant_recommendations:
                if rec['consultant_id'] not in seen_consultants:
                    seen_consultants.add(rec['consultant_id'])
                    unique_recommendations.append(rec)
            
            unique_recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
            
            print(f"✅ Generated {len(unique_recommendations)} collaborative consultant recommendations")
            return unique_recommendations[:top_k]
            
        except Exception as e:
            print(f"❌ Error in collaborative consultant filtering: {str(e)}")
            return []

    def enhanced_collaborative_filtering_recommendations(self, user_id: str, top_k_courses: int = 5, top_k_consultants: int = 3) -> Dict:
        """
        Enhanced collaborative filtering cho cả courses và consultants
        """
        try:
            # Lấy collaborative recommendations cho cả courses và consultants
            course_recommendations = self.collaborative_filtering_recommendations(user_id, top_k_courses)
            consultant_recommendations = self.collaborative_filtering_consultant_recommendations(user_id, top_k_consultants)
            
            return {
                'courses': course_recommendations,
                'consultants': consultant_recommendations,
                'recommendation_type': 'enhanced_collaborative',
                'user_risk_info': self.get_user_risk_summary(user_id),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'courses': [],
                'consultants': [],
                'status': 'error',
                'message': str(e)
            }

    def demo_data_processing_workflow(self, user_id: str) -> Dict:
        """
        Demo quy trình xử lý dữ liệu: ORM → DataFrame → ML Processing
        """
        workflow_demo = {
            "step_1_orm_queries": {},
            "step_2_dataframes": {},
            "step_3_ml_processing": {},
            "summary": {}
        }
        
        try:
            print("🔍 STEP 1: Truy vấn dữ liệu qua SQLAlchemy ORM...")
            
            # Demo ORM queries
            survey_orm_count = self.db.query(SurveyAttempt).filter(SurveyAttempt.is_deleted == False).count()
            course_orm_count = self.db.query(Course).filter(Course.is_deleted == False).count()
            consultant_orm_count = self.db.query(Consultant).filter(Consultant.is_deleted == False).count()
            
            workflow_demo["step_1_orm_queries"] = {
                "description": "Sử dụng SQLAlchemy ORM thay vì raw SQL",
                "survey_attempts_count": survey_orm_count,
                "courses_count": course_orm_count,
                "consultants_count": consultant_orm_count,
                "advantages": [
                    "Type safety với Python objects",
                    "Dễ bảo trì và debug",
                    "Tự động handle relationships",
                    "Database agnostic"
                ]
            }
            
            print("📊 STEP 2: Chuyển đổi thành pandas DataFrame...")
            
            # Demo DataFrame conversion
            survey_df = self.get_user_survey_data()
            courses_df = self.get_courses_data()
            interactions_df = self.get_user_interactions()
            
            workflow_demo["step_2_dataframes"] = {
                "description": "Chuyển ORM results thành pandas DataFrame",
                "survey_dataframe_shape": survey_df.shape,
                "courses_dataframe_shape": courses_df.shape,
                "interactions_dataframe_shape": interactions_df.shape,
                "sample_columns": {
                    "surveys": list(survey_df.columns) if not survey_df.empty else [],
                    "courses": list(courses_df.columns) if not courses_df.empty else [],
                    "interactions": list(interactions_df.columns) if not interactions_df.empty else []
                },
                "advantages": [
                    "Powerful data manipulation với pandas",
                    "Easy integration với scikit-learn",
                    "Vectorized operations",
                    "Rich data analysis capabilities"
                ]
            }
            
            print("🤖 STEP 3: ML Processing với pandas/scikit-learn...")
            
            # Demo ML processing (không thay đổi)
            content_recs = self.content_based_course_recommendations(user_id, 3)
            collab_recs = self.collaborative_filtering_recommendations(user_id, 3)
            
            workflow_demo["step_3_ml_processing"] = {
                "description": "Giữ nguyên ML processing với pandas/sklearn",
                "content_based_results": len(content_recs),
                "collaborative_results": len(collab_recs),
                "ml_techniques_used": [
                    "TF-IDF Vectorization",
                    "Cosine Similarity",
                    "User-Item Matrix",
                    "Business Rules Boosting"
                ],
                "sample_recommendation": content_recs[0] if content_recs else None
            }
            
            workflow_demo["summary"] = {
                "workflow": "ORM → DataFrame → ML",
                "benefits": [
                    "✅ Type-safe database queries",
                    "✅ Maintainable code structure", 
                    "✅ Powerful data analysis",
                    "✅ ML-ready data format",
                    "✅ Best of both worlds"
                ],
                "performance": "Optimal balance between safety and performance"
            }
            
            return workflow_demo
            
        except Exception as e:
            return {
                "error": f"Demo workflow error: {str(e)}",
                "status": "failed"
            }

    def get_user_risk_summary(self, user_id: str) -> Dict:
        """Lấy tóm tắt risk assessment của user"""
        try:
            user_surveys = self.get_user_survey_data()
            user_data = user_surveys[user_surveys['user_id'] == user_id]
            
            if user_data.empty:
                return {
                    'latest_risk_level': None,
                    'latest_score': 0,
                    'completed_at': None,
                    'total_surveys_taken': 0
                }
            
            # Get the latest survey (first row since data is ordered by completed_at DESC)
            latest_survey = user_data.iloc[0]
            
            return {
                'latest_risk_level': latest_survey['risk_level'],
                'latest_score': int(latest_survey['total_score']) if latest_survey['total_score'] else 0,
                'completed_at': latest_survey['completed_at'].isoformat() if pd.notna(latest_survey['completed_at']) else None,
                'total_surveys_taken': len(user_data)
            }
            
        except Exception as e:
            print(f"Error in get_user_risk_summary: {str(e)}")
            return {
                'latest_risk_level': None,
                'latest_score': 0,
                'completed_at': None,
                'total_surveys_taken': 0
            }

    def hybrid_recommendations(self, user_id: str, top_k: int = 10) -> Dict:
        """
        Hybrid recommendation system combining content-based and collaborative filtering
        """
        try:
            print(f"🚀 Starting hybrid recommendations for user: {user_id}")
            
            # Get user risk summary
            user_risk_info = self.get_user_risk_summary(user_id)
            
            # Get content-based recommendations
            content_courses = self.content_based_course_recommendations(user_id, top_k)
            content_consultants = self.content_based_consultant_recommendations(user_id, min(3, top_k))
            
            # Get collaborative filtering recommendations
            collab_result = self.collaborative_filtering_recommendations(user_id, top_k)
            collab_courses = collab_result.get('courses', [])
            collab_consultants = collab_result.get('consultants', [])
            
            # Combine and deduplicate courses
            all_courses = content_courses + collab_courses
            unique_courses = []
            seen_course_ids = set()
            
            for course in all_courses:
                course_id = course.get('course_id')
                if course_id not in seen_course_ids:
                    seen_course_ids.add(course_id)
                    # Add hybrid score
                    course['hybrid_score'] = course.get('score', 0) + course.get('predicted_rating', 0)
                    unique_courses.append(course)
            
            # Sort by hybrid score and take top K
            unique_courses.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
            final_courses = unique_courses[:top_k]
            
            # Combine and deduplicate consultants
            all_consultants = content_consultants + collab_consultants
            unique_consultants = []
            seen_consultant_ids = set()
            
            for consultant in all_consultants:
                consultant_id = consultant.get('consultant_id')
                if consultant_id not in seen_consultant_ids:
                    seen_consultant_ids.add(consultant_id)
                    # Add hybrid score
                    consultant['hybrid_score'] = consultant.get('score', 0) + consultant.get('predicted_rating', 0)
                    unique_consultants.append(consultant)
            
            # Sort by hybrid score and take top K
            unique_consultants.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
            final_consultants = unique_consultants[:min(3, top_k)]
            
            return {
                'courses': final_courses,
                'consultants': final_consultants,
                'user_risk_info': user_risk_info,
                'recommendation_type': 'hybrid',
                'recommendation_summary': {
                    'total_courses': len(final_courses),
                    'total_consultants': len(final_consultants),
                    'content_based_courses': len(content_courses),
                    'collaborative_courses': len(collab_courses),
                    'content_based_consultants': len(content_consultants),
                    'collaborative_consultants': len(collab_consultants)
                },
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Error in hybrid recommendations: {str(e)}")
            return {
                'courses': [],
                'consultants': [],
                'user_risk_info': self.get_user_risk_summary(user_id),
                'status': 'error',
                'message': str(e)
            }
def get_user_recommendations(user_id: str, test_survey_id: str, total_score: int, risk_level: str, db: Session) -> dict:
    """
    Hàm chính để lấy recommendations cho user
    """
    try:
        # Khởi tạo recommendation system
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        # Lấy recommendations
        recommendations = recommender.hybrid_recommendations(user_id, top_k=10)
        
        return recommendations
    except Exception as e:
        return {
            'courses': [],
            'consultants': [],
            'user_risk_info': {},
            'status': 'error',
            'message': f"Error getting recommendations: {str(e)}"
        }