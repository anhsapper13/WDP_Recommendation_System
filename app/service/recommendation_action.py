import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict
from app.models.survey_attempt import SurveyAttempt
from app.models.course import Course
from app.models.consultant import Consultant


class CRAFFTASSISTRecommendationSystem:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.svd_model = TruncatedSVD(n_components=50, random_state=42)
        
    def get_user_survey_data(self) -> pd.DataFrame:
        """Lấy dữ liệu khảo sát của người dùng qua SQLAlchemy ORM"""
        try:
           
            survey_data = self.db.execute(text("""
                SELECT 
                    sa.user_id,
                    sa.test_survey_id,
                    sa.total_score,
                    sa.risk_level,
                    sa.completed_at,
                    u.first_name,
                    u.last_name,
                    u.age,
                    ts.category_id
                FROM "Survey_Attempts" sa
                JOIN "Users" u ON sa.user_id = u.id
                JOIN "Test_Survey" ts ON sa.test_survey_id = ts.id
                WHERE u.is_deleted = false
                ORDER BY sa.completed_at DESC
            """)).fetchall()
            print(f"Found {len(survey_data)} survey records")
            
            data_list = []
            for row in survey_data:
                data_list.append({
                    'user_id': str(row.user_id),
                    'test_survey_id': str(row.test_survey_id),
                    'category_id': str(row.category_id),  # Ensure category_id is string
                    'total_score': row.total_score,
                    'risk_level': row.risk_level,
                    'completed_at': row.completed_at,
                    'first_name': row.first_name,
                    'last_name': row.last_name,
                    'age': row.age,
                    'user_type': ['adult', 'parents', 'teacher'] if row.age > 23 else ['youth', 'students'],
                })
            
         
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
                    cc.name as category_name,
                    COALESCE(ce.enrollment_count, 0) as enrollment_count
                FROM "Course" c
                LEFT JOIN "Course_Category" cc ON c.category_id = cc.id
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
                    'enrollment_count': row.enrollment_count,
                    'category_name': row.category_name
                })
            
            # Bước 3: Tạo DataFrame từ data
            return pd.DataFrame(data_list)
            
        except Exception as e:
            print(f"Error in get_courses_data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def get_consultants_data(self) -> pd.DataFrame:
        """Lấy dữ liệu chuyên viên tư vấn qua SQLAlchemy ORM"""
        try:
          
            consultants_data = self.db.execute(text("""
                SELECT 
                    c.id,
                    c.specialization,
                    c.experience_years,
                    c.bio,
                    c.is_available,
                    u.first_name,
                    u.last_name,
                    c.user_id,
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
            
        
            data_list = []
            for row in consultants_data:
                data_list.append({
                    'id': row.id,
                    'specialization': row.specialization,
                    'consult_id': str(row.user_id),  # Ensure user_id is string
                    # 'qualifications': row.qualifications,
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
            
            appointment_interactions = self.db.execute(text("""
                SELECT 
                    "userId" as user_id,
                    "consultantId" as item_id,
                    status,
                    booking_time as interaction_date
                FROM "Appointments"
                WHERE is_deleted = false 
            """)).fetchall()
            data_list = []
            # Course interactions
            for row in course_interactions:
                data_list.append({
                    'user_id': str(row.user_id),
                    'item_id': str(row.item_id),
                    'item_type': 'course',
                    'rating': (row.progress_percentage or 0) / 100.0,
                    'interaction_date': row.interaction_date
                })
                            
            # Appointment interactions
            for row in appointment_interactions:
                rating = 0.8 if row.status == 'completed' else 0.1 
                if row.user_id is None:
                    continue
                data_list.append({
                    'user_id': str(row.user_id),
                    'item_id': str(row.item_id),
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
        return {
            'low': {
                'course_topics': [
                    # Core prevention topics
                    'prevention', 'awareness', 'healthy lifestyle', 'peer pressure', 'self esteem',
                    'communication skills', 'basic psychology', 'digital wellbeing', 'goal setting',
                    'time management', 'substance education', 'nutrition', 'emotional awareness',
                    'decision making', 'personal safety', 'social skills', 'mindfulness',
                    'positive relationships', 'cyber safety', 'stress basics',
                    'substance abuse prevention', 'alcohol awareness', 'tobacco prevention',
                    'drug education', 'safe driving', 'responsible choices', 'risk awareness',
                    'health promotion', 'wellness education', 'lifestyle choices', 'peer education',
                    'youth development', 'resilience building', 'protective factors',
                    'community engagement', 'family communication', 'school engagement',
                    'extracurricular activities', 'mentorship programs', 'leadership skills',
                    'academic success', 'career planning', 'financial literacy', 'media literacy'
                ],
                'consultant_specialization': [
                    'general', 'prevention', 'school counselor', 'youth mentor', 'community worker',
                    'health educator', 'social worker', 'peer facilitator', 'psychosocial support',
                    'education consultant', 'life coach', 'wellness coach', 'guidance counselor',
                    'child development', 'mental wellbeing', 'digital health', 'parenting support',
                    'youth leader', 'school advisor', 'family liaison',
                    'substance abuse prevention specialist', 'alcohol prevention educator',
                    'tobacco cessation educator', 'safe driving instructor', 'peer educator',
                    'youth development specialist', 'resilience coach', 'protective factors specialist',
                    'community outreach coordinator', 'family engagement specialist'
                ],
                'priority_weight': 0.3
            },

            'medium': {
                'course_topics': [
                    # Early intervention core
                    'intervention', 'coping skills', 'family support', 'stress management',
                    'early intervention', 'brief intervention', 'motivational interviewing',
                    'screening and assessment', 'risk reduction', 'harm reduction',
                    'behavioral modification', 'cognitive restructuring', 'relapse prevention basics',
                    
                    # CRAFFT/ASSIST medium risk areas
                    'substance use awareness', 'alcohol moderation', 'tobacco reduction',
                    'driving safety intervention', 'peer influence management', 'social skills training',
                    'family intervention', 'communication enhancement', 'boundary establishment',
                    'impulse control', 'emotional regulation advanced', 'stress coping strategies',
                    'anxiety management', 'depression awareness', 'trauma informed care basics',
                    'group therapy introduction', 'peer support groups', 'family therapy basics',
                    'cognitive behavioral techniques', 'mindfulness based interventions',
                    'dialectical behavior therapy skills', 'acceptance commitment therapy basics'
                ],
                'consultant_specialization': [
                    'intervention', 'family therapy', 'cognitive behavioral', 'school psychologist',
                    'youth therapist', 'behavioral coach', 'licensed counselor', 'clinical social worker',
                    'group facilitator', 'addiction outreach', 'case manager', 'child behavior specialist',
                    'cbt therapist', 'trauma informed', 'parenting coach', 'preventive counselor',
                    'support group leader', 'emotional resilience trainer', 'youth rehabilitation worker',
                    'school interventionist',
                    'early intervention specialist', 'brief intervention counselor', 'motivational interviewing specialist',
                    'screening assessment specialist', 'risk reduction counselor', 'harm reduction specialist',
                    'behavioral modification therapist', 'cognitive restructuring specialist', 'relapse prevention counselor',
                    'substance use counselor', 'alcohol moderation therapist', 'tobacco cessation specialist',
                    'driving safety counselor', 'peer influence therapist', 'social skills trainer',
                    'anxiety therapist', 'depression counselor', 'trauma therapist', 'group therapy facilitator'
                ],
                'priority_weight': 0.6
            },

            'high': {
                'course_topics': [
                    # Core intensive concepts (keeping only one "treatment")
                    'treatment', 'recovery', 'intensive support', 'multidisciplinary',
                    # Specific areas (removed redundant "treatment")
                    'addiction therapy', 'substance abuse rehabilitation', 'alcohol dependence',
                    'drug addiction recovery', 'intensive outpatient programs', 'residential programs',
                    'inpatient rehabilitation', 'medical detoxification', 'withdrawal management',
                    'medication assisted therapy', 'pharmacotherapy', 'dual diagnosis therapy',
                    'co occurring mental health', 'psychiatric evaluation', 'psychological assessment',
                    'comprehensive planning', 'individualized care plans', 'evidence based practices',
                    # Advanced therapy modalities
                    'cognitive behavioral therapy intensive', 'dialectical behavior therapy',
                    'acceptance commitment therapy', 'contingency management',
                    'community reinforcement approach', 'matrix model',
                    'twelve step facilitation', 'motivational enhancement therapy',
                    'trauma informed care', 'mindfulness based relapse prevention', 
                    # Medical/clinical aspects
                    'medical monitoring', 'psychiatric medication management',
                    'addiction medicine', 'withdrawal protocols', 'overdose prevention',
                    'hepatitis c care', 'hiv care', 'mental health stabilization',
                    # Recovery support
                    'recovery coaching', 'peer recovery support', 'sober living',
                    'vocational rehabilitation', 'legal advocacy', 'family reunification',
                    'aftercare planning', 'continuing care', 'crisis intervention'
                ],
                'consultant_specialization': [
                    # Core medical professionals
                    'addiction specialist', 'clinical psychology', 'psychiatry',
                    'addiction medicine physician', 'substance abuse specialist', 'alcohol specialist',
                    'drug addiction counselor', 'intensive outpatient coordinator', 'residential director',
                    'inpatient rehabilitation specialist', 'medical detox physician', 'withdrawal nurse',
                    'medication assisted provider', 'addiction pharmacist', 'dual diagnosis specialist',
                    'co occurring disorders psychiatrist', 'psychiatric nurse practitioner', 'psychological evaluator',
                    # Specialized coordinators (removed redundant "treatment")
                    'planning specialist', 'care coordination manager', 'evidence based practitioner',
                    'addiction therapist', 'dbt therapist', 'act specialist', 'contingency management specialist',
                    'community reinforcement therapist', 'matrix model specialist', 'twelve step facilitator',
                    # Recovery support specialists
                    'recovery coach', 'peer recovery specialist', 'sober living manager',
                    'vocational counselor', 'legal advocate', 'family reunification specialist',
                    'aftercare coordinator', 'continuing care specialist', 'crisis interventionist',
                    'emergency response coordinator', 'overdose prevention specialist'
                ],
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
            features = f"{course['description']} {course['category_name']} {course['target_audience']}"
            course_features.append(features)
        
        if not course_features:
            return []
        
        print(f"📚 Total courses found: {len(course_features)}")
        # TF-IDF vectorization
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(course_features)
        
        # 📊 Enhanced debugging info
        print(f"📊 TF-IDF Matrix Shape: {tfidf_matrix.shape} (courses x vocabulary)")
        print(f"📊 Vocabulary Size: {len(self.tfidf_vectorizer.vocabulary_)}")
        print(f"📊 Non-zero Elements: {tfidf_matrix.nnz}")
        print(f"📊 Sparsity: {(1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100:.2f}%")
        
        # Show sample vocabulary terms
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        print(f"📝 Sample vocabulary terms: {list(feature_names[:10])}")
        
        # Show course-term matrix info for each course
        for i in range(min(5, tfidf_matrix.shape[0])):  # Show first 3 courses
            course_terms = tfidf_matrix[i].nonzero()[1]
            course_weights = tfidf_matrix[i].data
            if len(course_weights) > 0:
                print(f"📖 Course {i}: {len(course_terms)} terms, max_weight: {max(course_weights):.3f}")
            else:
                print(f"📖 Course {i}: {len(course_terms)} terms, max_weight: 0.000")
        
        print(f"📊 Total courses vectorized: {tfidf_matrix.shape[0]}")
        
        
        # Tạo user profile dựa trên risk level
        user_profile = " ".join(risk_mapping.get(user_risk, risk_mapping['medium'])['course_topics'])
        user_vector = self.tfidf_vectorizer.transform([user_profile])
        
        # 🎯 Enhanced user profile debugging
        print(f"👤 User Risk Level: {user_risk}")
        print(f"👤 User Profile Length: {len(user_profile)} characters")
        print(f"👤 User Profile Terms: {len(user_profile.split())} words")
        user_terms = user_vector.nonzero()[1]
        user_weights = user_vector.data
        if len(user_weights) > 0:
            print(f"👤 User Vector: {len(user_terms)} matching terms, max_weight: {max(user_weights):.3f}")
        else:
            print(f"👤 User Vector: {len(user_terms)} matching terms, max_weight: 0.000")
        
        # Show matching terms between user and vocabulary
        if len(user_terms) > 0:
            print(f"🔗 User matching terms: {[feature_names[i] for i in user_terms[:5]]}")
        
        # Tính cosine similarity
        similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
        
        # 🎯 Similarity debugging
        if len(similarities) > 0:
            print(f"🎯 Similarity Scores: min={min(similarities):.3f}, max={max(similarities):.3f}, mean={np.mean(similarities):.3f}")
            non_zero_similarities = similarities[similarities > 0]
            print(f"🎯 Non-zero Similarities: {len(non_zero_similarities)}/{len(similarities)} courses")
        else:
            print("🎯 No similarity scores computed")
        
        # Show top similarity scores with course info
        top_indices = np.argsort(similarities)[::-1][:5]
        print("🏆 Top 3 similarity scores:")
        for i, idx in enumerate(top_indices):
            print(f"  {i+1}. Course {idx}: similarity={similarities[idx]:.3f}")
        
        # Áp dụng business rules
        course_scores = []
        for idx, (_, course) in enumerate(courses_df.iterrows()):
            base_score = similarities[idx]
            original_score = base_score
            
            # Business rules boost
            if course['target_audience'] in user_data.get('user_type', []) or course['target_audience'] == 'all':
                base_score *= 1.2
                
            # Debug individual scores
            if idx < 3:  # Show details for first 3 courses
                boost_applied = "✅ Audience boost" if base_score != original_score else "❌ No boost"
                print(f"📊 Course {idx} ({course['title'][:20]}...): sim={original_score:.3f} → final={base_score:.3f} ({boost_applied})")
            
            course_scores.append({
                'course_id': str(course['id']),
                'title': str(course['title']),
                'description': str(course['description']) if pd.notna(course['description']) else '',
                'score': float(base_score),
                'enrollment_count': int(course['enrollment_count']) if pd.notna(course['enrollment_count']) else 0,
                'recommendation_type': 'content_based'
            })
        
        # Sắp xếp và trả về top K
        course_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 🎯 Final recommendations debugging
        print(f"🎯 Final Recommendation Results:")
        print(f"📊 Total courses scored: {len(course_scores)}")
        print(f"🏆 Top {min(top_k, len(course_scores))} recommendations:")
        for i, course in enumerate(course_scores[:top_k]):
            print(f"  {i+1}. {course['title'][:30]}... (Score: {course['score']:.4f})")
        
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
            base_score = risk_mapping.get(user_risk, risk_mapping['medium'])['priority_weight']
            
            # Boost score dựa trên specialization
            if consultant['specialization']:
                specializations = consultant['specialization'].lower().split(',')
                for spec in risk_mapping.get(user_risk, risk_mapping['medium'])['consultant_specialization']:
                    if any(spec in s.strip() for s in specializations):
                        base_score *= 1.2
                        break
            
            # Boost score dựa trên experience
            if consultant['experience_years'] and consultant['experience_years'] >= 5:
                base_score *= 1.12
        

            consultant_scores.append({
                'consultant_id': str(consultant['id']),
                'name': str(consultant['full_name']),
                'specialization': str(consultant['specialization']) if pd.notna(consultant['specialization']) else 'General',
                'experience_years': int(consultant['experience_years']) if pd.notna(consultant['experience_years']) else 0,
                'score': float(base_score),
                'total_appointments': int(consultant['total_appointments']) if pd.notna(consultant['total_appointments']) else 0,
                'recommendation_type': 'content_based'
            })
        
        consultant_scores.sort(key=lambda x: x['score'], reverse=True)
        return consultant_scores[:top_k]

    def collaborative_filtering_recommendations(self, user_id: str, top_k: int = 5) -> Dict:
        """
        Enhanced collaborative filtering cho cả courses và consultants
        Logic: Users tương tự (cùng risk level with category of this survey + behavior) → recommend items tương tự
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
            print(f"Error in collaborative filtering: {str(e)}")
            return {
                'courses': [],
                'consultants': [],
                'user_risk_info': {},
                'status': 'error',
                'message': str(e)
            }

    def collaborative_filtering_course_recommendations(self, user_id: str, top_k: int = 5) -> List[Dict]:
        """Collaborative filtering cho courses sử dụng user similarity với comprehensive debugging"""
        try:
            print(f"🤝 COLLABORATIVE FILTERING COURSES DEBUG - User: {user_id}")
            print("=" * 60)
            
            interactions_df = self.get_user_interactions()
            
            if interactions_df.empty:
                print("❌ No interactions data found")
                return []
            # Tạo user-item matrix cho courses
            course_interactions = interactions_df[interactions_df['item_type'] == 'course']
            print(f"📊 INTERACTION MATRIX ANALYSIS:")
            print(f"   Total interactions: {len(interactions_df)}")
            print(f"   Course interactions: {len(course_interactions)}")
            print(f"   Unique users: {interactions_df['user_id'].nunique()}")
            print(f"   Unique courses: {course_interactions['item_id'].nunique()}")
            
            if course_interactions.empty:
                print("❌ No course interactions found")
                return []
            
            # Pivot table: user_id x course_id
            user_item_matrix = course_interactions.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating', 
                fill_value=0
            )

            print(f"📊 USER-ITEM MATRIX STRUCTURE:")
            print(f"   Matrix shape: {user_item_matrix}")
            print(f"   Matrix shape: {user_item_matrix.shape} (users x courses)")
            print(f"   Total elements: {user_item_matrix.size}")
            print(f"   Non-zero elements: {(user_item_matrix != 0).sum().sum()}")
            print(f"   Sparsity: {(1 - (user_item_matrix != 0).sum().sum() / user_item_matrix.size) * 100:.2f}%")
            print(f"   Users in matrix: {list(user_item_matrix.index)}")
            print(f"   Courses in matrix: {list(user_item_matrix.columns)}")
            
            # Check if user exists in matrix
            if user_id not in user_item_matrix.index:
                print(f"❌ User {user_id} not found in interaction matrix")
                print(f"   Available users: {list(user_item_matrix.index)}")
                return []
            
            # Show user's interaction profile
            user_row = user_item_matrix.loc[user_id]
            user_interactions_count = (user_row != 0).sum()
            user_avg_rating = user_row[user_row != 0].mean() if user_interactions_count > 0 else 0
            
            print(f"👤 USER INTERACTION PROFILE:")
            print(f"   User interactions count: {user_interactions_count}")
            print(f"   User avg rating: {user_avg_rating:.3f}")
            print(f"   User rated courses: {list(user_row[user_row != 0].index)}")
            
            # 🆕 STRICT SURVEY CATEGORY FILTERING FOR SIMILARITY
            # Get user's survey category for strict similarity matching (same as consultant logic)
            user_surveys = self.get_user_survey_data()
            current_user_survey = user_surveys[user_surveys['user_id'] == user_id]
            
            if not current_user_survey.empty:
                current_user_risk = current_user_survey.iloc[0]['risk_level']
                current_user_category = current_user_survey.iloc[0]['category_id']
                print(f"👤 USER SURVEY PROFILE:")
                print(f"   Risk level: {current_user_risk}")
                print(f"   Survey category: {current_user_category}")
                
                # Find users with same risk level and category (STRICT FILTERING)
                strict_similar_users = user_surveys[
                    (user_surveys['risk_level'] == current_user_risk) &
                    (user_surveys['category_id'] == current_user_category) &
                    (user_surveys['user_id'] != user_id)
                ]['user_id'].unique().tolist()
                
                print(f"   Users with same risk+category (STRICT): {len(strict_similar_users)}")
                print(f"   Strict similar users: {strict_similar_users}")
                
                # Get intersection of users in both interaction matrix and survey similarity
                if strict_similar_users:
                    available_similar_users = [u for u in strict_similar_users if u in user_item_matrix.index]
                    print(f"   Available similar users in interaction matrix: {len(available_similar_users)}")
                    print(f"   Available users: {available_similar_users}")
                    
                    if not available_similar_users:
                        print(f"❌ No users with same risk+category found in interaction matrix")
                        print(f"   Falling back to risk level only...")
                        
                        # Fallback to risk level only if no same category users have interactions
                        risk_only_users = user_surveys[
                            (user_surveys['risk_level'] == current_user_risk) &
                            (user_surveys['user_id'] != user_id)
                        ]['user_id'].unique().tolist()
                        
                        available_similar_users = [u for u in risk_only_users if u in user_item_matrix.index]
                        print(f"   Fallback users (risk level only): {len(available_similar_users)}")
                        print(f"   Fallback available users: {available_similar_users}")
                else:
                    print(f"❌ No users with same risk+category found")
                    available_similar_users = []
            else:
                print(f"❌ No survey data found for user")
                available_similar_users = []
            
            # Tính cosine similarity chỉ với filtered users (strict filtering)
            if not available_similar_users:
                print(f"❌ No similar users available for recommendations")
                return []
                
            # Filter user_item_matrix to only include target user and similar users
            filtered_users = [user_id] + available_similar_users
            filtered_matrix = user_item_matrix.loc[filtered_users]
            
            print(f"📊 FILTERED USER SIMILARITY MATRIX:")
            print(f"   Original matrix users: {len(user_item_matrix)}")
            print(f"   Filtered matrix users: {len(filtered_matrix)} (target + {len(available_similar_users)} similar)")
            print(f"   Filtered users: {filtered_users}")
            
            user_similarity = cosine_similarity(filtered_matrix.values)
            user_similarity_df = pd.DataFrame(
                user_similarity, 
                index=filtered_matrix.index, 
                columns=filtered_matrix.index
            )
           
            print(f"📊 SIMILARITY CALCULATION RESULTS:")
            print(f"   Similarity matrix shape: {user_similarity_df.shape}")
            
            user_sim_stats = user_similarity_df[user_id].drop(user_id)
            print(f"   Similarity scores - min: {user_sim_stats.min():.3f}, max: {user_sim_stats.max():.3f}, mean: {user_sim_stats.mean():.3f}")
            print(f"   Non-zero similarities: {(user_sim_stats > 0).sum()}/{len(user_sim_stats)}")
            
            # Tìm users tương tự (đã được filtered by survey profile)
            similar_users = user_similarity_df[user_id].drop(user_id)
            similar_users = similar_users.sort_values(ascending=False)
            top_similar_users = similar_users.head(7)  # Top 7 similar users from filtered list
            
            print(f"👥 TOP SIMILAR USERS (STRICT RISK+CATEGORY FILTERING):")
            for i, (sim_user, sim_score) in enumerate(top_similar_users.items(), 1):
                sim_user_interactions = (filtered_matrix.loc[sim_user] != 0).sum()
                print(f"   {i}. 📋 User {sim_user}: similarity={sim_score:.3f}, interactions={sim_user_interactions} (same risk+category)")
            
            if len(top_similar_users) == 0:
                print(f"❌ No similar users found with sufficient similarity")
                return []
            
            # Lấy courses mà similar users đã rated cao nhưng current user chưa thử
            user_rated_courses = set(course_interactions[course_interactions['user_id'] == user_id]['item_id'])
            
            print(f"📚 COURSE RECOMMENDATION GENERATION:")
            print(f"   User already rated courses: {len(user_rated_courses)}")
            print(f"   Courses to exclude: {list(user_rated_courses)}")
            
            course_recommendations = []
            courses_df = self.get_courses_data()
            
            similarity_threshold = 0.1
            rating_threshold = 0.4
            
            print(f"🔍 FILTERING CRITERIA:")
            print(f"   Similarity threshold: {similarity_threshold}")
            print(f"   Rating threshold: {rating_threshold}")
            
            for similar_user, similarity_score in top_similar_users.items():
                if similarity_score < similarity_threshold:
                    print(f"   ⏭️  Skipping user {similar_user} (similarity {similarity_score:.3f} < {similarity_threshold})")
                    continue
                    
                similar_user_courses = course_interactions[
                    (course_interactions['user_id'] == similar_user) & 
                    (course_interactions['rating'] >= rating_threshold)  
                ]['item_id'].tolist()
                
                print(f"   👤 User {similar_user} (sim: {similarity_score:.3f}):")
                print(f"      High-rated courses: {len(similar_user_courses)} courses")
                print(f"      Course IDs: {similar_user_courses}")
                
                for course_id in similar_user_courses:
                    if course_id not in user_rated_courses:
                        print(f"type (course_id): {type(course_id)}")
                        # Ensure type consistency for comparison
                        course_info = courses_df[courses_df['id'].astype(str) == str(course_id)]
                        if not course_info.empty:
                            course_info = course_info.iloc[0]
                            
                            print(f"✅ Recommending course {course_id}: '{course_info['title'][:30]}...' (similarity_score: {similarity_score:.3f})")
                            
                            course_recommendations.append({
                                'course_id': str(course_id),
                                'title': str(course_info['title']),
                                'description': str(course_info['description']) if pd.notna(course_info['description']) else '',
                                'similarity_score': float(similarity_score),
                                'enrollment_count': int(course_info['enrollment_count']) if pd.notna(course_info['enrollment_count']) else 0,
                                'recommendation_type': 'collaborative',
                                'source_user': str(similar_user)
                            })
                        else:
                            print(f"         ❌ Course {course_id} not found in courses database")
                    else:
                        print(f"         ⏭️  Course {course_id} already rated by user")
            
            print(f"📊 DEDUPLICATION AND RANKING:")
            print(f"   Raw recommendations: {len(course_recommendations)}")
            print(f"   Raw recommendations 1: {(course_recommendations)}")
            
            # Remove duplicates và sort by predicted rating
            seen_courses = set()
            unique_recommendations = []
            for rec in course_recommendations:
                if rec['course_id'] not in seen_courses:
                    seen_courses.add(rec['course_id'])
                    unique_recommendations.append(rec)
                else:
                    print(f"   🔄 Removing duplicate course: {rec['course_id']}")
            
            print(f"   Unique recommendations: {len(unique_recommendations)}")
            
            unique_recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"🏆 FINAL COLLABORATIVE COURSE RECOMMENDATIONS:")
            for i, rec in enumerate(unique_recommendations[:top_k], 1):
                print(f"   {i}. {rec['title'][:40]}... (Score: {rec['similarity_score']:.4f}, Source: User {rec['source_user']})")
            
            print("=" * 60)
            return unique_recommendations[:top_k]
            
        except Exception as e:
            print(f"❌ Error in collaborative course filtering: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def collaborative_filtering_consultant_recommendations(self, user_id: str, top_k: int = 3) -> List[Dict]:
        """
        Collaborative filtering cho consultants dựa trên appointment history với comprehensive debugging
        Logic: Users có cùng risk level book cùng consultant → recommend consultant đó
        """
        try:
            print(f"🤝 COLLABORATIVE FILTERING CONSULTANTS DEBUG - User: {user_id}")
            print("=" * 60)
            
            # Bước 1: Lấy risk level của current user
            user_surveys = self.get_user_survey_data()
            print(f"📊 RISK LEVEL ANALYSIS:")
            print(f"   Total user surveys: {len(user_surveys)}")
            print(f"   Unique users in surveys: {user_surveys['user_id'].nunique()}")
            
            # 🔍 DEBUG: Kiểm tra user_id có trong DataFrame không
            print(f"🔍 USER LOOKUP DEBUG:")
            print(f"   All unique user_ids: {list(user_surveys['user_id'].unique())}")
            print(f"   Looking for user_id: '{user_id}' (type: {type(user_id)})")
            print(f"   DataFrame user_id dtype: {user_surveys['user_id'].dtype}")
            
            # 🔍 Check exact match
            exact_matches = user_surveys[user_surveys['user_id'] == user_id]
            print(f"   Exact matches found: {len(exact_matches)}")
            
            # 🔍 Check với .str.strip() để loại bỏ whitespace
            if user_surveys['user_id'].dtype == 'object':
                stripped_matches = user_surveys[user_surveys['user_id'].str.strip() == str(user_id).strip()]
                print(f"   Stripped matches found: {len(stripped_matches)}")
            
            current_user_data = user_surveys[user_surveys['user_id'] == user_id]
            
            if current_user_data.empty:
                print(f"❌ No survey data found for user {user_id}")
                print(f"   Available users: {list(user_surveys['user_id'].unique())}")
                return []
            
            current_user_risk = current_user_data.iloc[0]['risk_level']
            current_user_category = current_user_data.iloc[0]['category_id']
            print(f"✅ Current user risk level: {current_user_risk}")
            print(f"✅ Current user survey category: {current_user_category}")
            
            # Bước 2: Tìm users có cùng risk level AND same survey category
            users_same_risk_and_category = user_surveys[
                (user_surveys['risk_level'] == current_user_risk) &
                (user_surveys['category_id'] == current_user_category) &
                (user_surveys['user_id'] != user_id)
            ]['user_id'].unique().tolist()
            
            print(f"👥 SIMILAR USERS ANALYSIS:")
            print(f"   Users with same risk level ({current_user_risk}) AND category ({current_user_category}): {len(users_same_risk_and_category)}")
            print(f"   Similar user IDs: {users_same_risk_and_category}")
            
            # If no users with exact match, fallback to same risk level only
            if len(users_same_risk_and_category) < 1:
                print(f"⚠️  No users found with same risk level AND category, falling back to risk level only...")
                users_same_risk_and_category = user_surveys[
                    (user_surveys['risk_level'] == current_user_risk) &
                    (user_surveys['user_id'] != user_id)
                ]['user_id'].unique().tolist()
                print(f"   Fallback users with same risk level only: {len(users_same_risk_and_category)}")
            
            # Risk level and category distribution
            risk_distribution = user_surveys['risk_level'].value_counts()
            category_distribution = user_surveys['category_id'].value_counts()
            print(f"   Risk level distribution: {dict(risk_distribution)}")
            print(f"   Category distribution: {dict(category_distribution)}")
            
            if len(users_same_risk_and_category) < 1:  
                print("⚠️  Not enough users with same risk level for collaborative filtering")
                return []
            
            # Bước 3: Lấy appointment interactions cho users cùng risk level
            interactions_df = self.get_user_interactions()
            print(f"📊 INTERACTION DATA ANALYSIS:")
            print(f"   Total interactions: {len(interactions_df)}")
            print(f"   Interaction types: {interactions_df['item_type'].value_counts().to_dict()}")
            
            consultant_interactions = interactions_df[
                (interactions_df['item_type'] == 'consultant') &
                (interactions_df['user_id'].isin(users_same_risk_and_category + [user_id]))
            ]
            
            print(f"   Consultant interactions for risk group: {len(consultant_interactions)}")
            print(f"   Unique users in consultant interactions: {consultant_interactions['user_id'].nunique()}")
            print(f"   Unique consultants in interactions: {consultant_interactions['item_id'].nunique()}")
            
            if consultant_interactions.empty:
                print("❌ No consultant interactions found for similar users")
                return []
            
            # Show rating distribution
            rating_distribution = consultant_interactions['rating'].value_counts().sort_index()
            print(f"   Rating distribution: {dict(rating_distribution)}")
            
            # Bước 4: Tạo user-consultant matrix
            user_consultant_matrix = consultant_interactions.pivot_table(
                index='user_id',
                columns='item_id', 
                values='rating',
                fill_value=0
            )
            
            print(f"📊 USER-CONSULTANT MATRIX:")
            print(f"   Matrix shape: {user_consultant_matrix} ")
            print(f"   Matrix shape: {user_consultant_matrix.shape} (users x consultants)")
            print(f"   Total elements: {user_consultant_matrix.size}")
            print(f"   Non-zero elements: {(user_consultant_matrix != 0).sum().sum()}")
            print(f"   Sparsity: {(1 - (user_consultant_matrix != 0).sum().sum() / user_consultant_matrix.size) * 100:.2f}%")
            print(f"   Users in matrix: {list(user_consultant_matrix.index)}")
            print(f"   Consultants in matrix: {list(user_consultant_matrix.columns)}")
            
            # Check if current user has interactions
            current_user_in_matrix = user_id in user_consultant_matrix.index
            print(f"   Current user in matrix: {current_user_in_matrix}")
            
            # it should be content base consultant
            if not current_user_in_matrix:
                print(f"ℹ️ User {user_id} has no consultant interactions (cold start)")
                print(f"🎯 Using popularity-based recommendations from similar users...")
                return []
                
                # Popularity-based fallback for cold start
                # popular_consultants = consultant_interactions[
                #     consultant_interactions['rating'] >= 0.4
                # ].groupby('item_id').agg({
                #     'rating': ['count', 'mean'],
                #     'user_id': 'nunique'
                # }).round(3)
                
                # popular_consultants.columns = ['booking_count', 'avg_rating', 'unique_users']
                # popular_consultants = popular_consultants.sort_values(['booking_count', 'avg_rating'], ascending=False)
                
                # print(f"📊 POPULARITY-BASED RECOMMENDATIONS:")
                # print(f"   Top consultants by bookings:\n{popular_consultants.head()}")
                
                # # Create recommendations from popular consultants
                # consultants_df = self.get_consultants_data()
                # popular_recommendations = []
                
                # for consultant_id in popular_consultants.index[:top_k]:
                #     consultant_info = consultants_df[consultants_df['id'] == consultant_id]
                #     if not consultant_info.empty:
                #         consultant_info = consultant_info.iloc[0]
                #         popularity_score = popular_consultants.loc[consultant_id, 'booking_count'] * 0.1 + \
                #                          popular_consultants.loc[consultant_id, 'avg_rating'] * 0.9
                        
                #         popular_recommendations.append({
                #             'consultant_id': consultant_id,
                #             'name': consultant_info['full_name'],
                #             'specialization': consultant_info['specialization'],
                #             'experience_years': consultant_info['experience_years'],
                #             'predicted_rating': float(popularity_score),
                #             'popularity_score': float(popularity_score),
                #             'booking_count': int(popular_consultants.loc[consultant_id, 'booking_count']),
                #             'avg_rating': float(popular_consultants.loc[consultant_id, 'avg_rating']),
                #             'total_appointments': int(consultant_info['total_appointments']) if consultant_info['total_appointments'] else 0,
                #             'recommendation_type': 'collaborative_popularity',
                #             'reason': f"Popular among users with {current_user_risk} risk level"
                #         })
                
                # print(f"🏆 POPULARITY-BASED RESULTS: {len(popular_recommendations)} recommendations")
                # return popular_recommendations
            
            # Continue with existing collaborative logic for users with interactions
            user_similarity = cosine_similarity(user_consultant_matrix.values)
            user_similarity_df = pd.DataFrame(
                user_similarity,
                index=user_consultant_matrix.index,
                columns=user_consultant_matrix.index
            )
            
            print(f"📊 USER SIMILARITY ANALYSIS:")
            print(f"   Similarity matrix shape: {user_similarity_df.shape}")
            
            # Check if user exists in similarity matrix (additional safety check)
            if user_id not in user_similarity_df.columns:
                print(f"⚠️ User {user_id} not in similarity matrix")
                return []
            
            # Show user's consultant interaction profile
            user_row = user_consultant_matrix.loc[user_id]
            user_consultant_count = (user_row != 0).sum()
            user_avg_rating = user_row[user_row != 0].mean() if user_consultant_count > 0 else 0
            
            print(f"👤 USER CONSULTANT PROFILE:")
            print(f"   Consultant interactions: {user_consultant_count}")
            print(f"   Average rating: {user_avg_rating:.3f}")
            print(f"   Consulted with: {list(user_row[user_row != 0].index)}")
            
            # Find similar users
            similar_users = user_similarity_df[user_id].drop(user_id).sort_values(ascending=False)
            user_sim_stats = similar_users
            print(f"   Similarity scores - min: {user_sim_stats.min():.3f}, max: {user_sim_stats.max():.3f}, mean: {user_sim_stats.mean():.3f}")
            
            top_similar_users = similar_users.head(5)  # Top 5 similar users
            
            print(f"👥 TOP SIMILAR USERS:")
            for i, (sim_user, sim_score) in enumerate(top_similar_users.items(), 1):
                sim_user_consultants = (user_consultant_matrix.loc[sim_user] != 0).sum()
                sim_user_avg = user_consultant_matrix.loc[sim_user][user_consultant_matrix.loc[sim_user] != 0].mean()
                print(f"   {i}. User {sim_user}: similarity={sim_score:.3f}, consultants={sim_user_consultants}, avg_rating={sim_user_avg:.3f}")
            
            user_booked_consultants = set(
                consultant_interactions[
                    (consultant_interactions['user_id'] == user_id) &
                    (consultant_interactions['rating'] >= 0.5)  
                ]['item_id']
            )
            print(f"📅 USER HISTORY:")
            print(f"   Already completely booked consultants: {(user_booked_consultants)}")
            
            consultant_recommendations = []
            consultants_df = self.get_consultants_data()
            
            
            similarity_threshold = 0.1
            rating_threshold = 0.5
            
            print(f"🔍 FILTERING CRITERIA:")
            print(f"   Similarity threshold: {similarity_threshold}")
            print(f"   Rating threshold: {rating_threshold}")
            
            for similar_user, similarity_score in top_similar_users.items():
                if similarity_score < similarity_threshold:
                    print(f"   ⏭️  Skipping user {similar_user} (similarity {similarity_score:.3f} < {similarity_threshold})")
                    continue   
                
                # Lấy consultants mà similar user đã book với rating cao
                similar_user_consultants = consultant_interactions[
                    (consultant_interactions['user_id'] == similar_user) &
                    (consultant_interactions['rating'] >= rating_threshold)
                ]['item_id'].tolist()
                print(f"   👤 User {similar_user} (sim: {similarity_score:.3f}):")
                print(f"      High-rated consultants: {len(similar_user_consultants)}")
                print(f"      Consultant IDs: {similar_user_consultants}")
                for consultant_id in similar_user_consultants:
                    # Chỉ recommend consultants mà current user chưa book
                    if consultant_id not in user_booked_consultants:
                        consultant_info = consultants_df[(consultants_df['consult_id']) == (consultant_id)]
                        
                        if not consultant_info.empty:
                            consultant_info = consultant_info.iloc[0]
                            print(f"         ✅ Recommending consultant {consultant_id}: '{consultant_info['full_name']}' (similarity_score: {similarity_score:.3f})")
                            
                            consultant_recommendations.append({
                                'consultant_id': str(consultant_id),
                                'name': str(consultant_info['full_name']),
                                'specialization': str(consultant_info['specialization']) if consultant_info['specialization'] else 'General',
                                'experience_years': int(consultant_info['experience_years']) if pd.notna(consultant_info['experience_years']) else 0,
                                'similarity_score': float(similarity_score),
                                'total_appointments': int(consultant_info['total_appointments']) if pd.notna(consultant_info['total_appointments']) else 0,
                                'recommendation_type': 'collaborative',
                                'reason': f"Users with {current_user_risk} risk level and {current_user_category} survey category also booked this consultant",
                                'source_user': str(similar_user)
                            })
                        else:
                            print(f"         ❌ Consultant {consultant_id} not found in consultants database")
                    else:
                        print(f"         ⏭️  Consultant {consultant_id} already booked by user")
            
            print(f"📊 DEDUPLICATION AND RANKING:")
            print(f"   Raw recommendations: {(consultant_recommendations)}")
            
            # Bước 9: Remove duplicates và sort by predicted rating
            seen_consultants = set()
            unique_recommendations = []
            for rec in consultant_recommendations:
                if rec['consultant_id'] not in seen_consultants:
                    seen_consultants.add((rec['consultant_id']))
                    unique_recommendations.append(rec)
                else:
                    print(f"   🔄 Removing duplicate consultant: {rec['consultant_id']}")
            
            print(f"   Unique recommendations: {len(unique_recommendations)}")
            
            unique_recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            print(f"🏆 FINAL COLLABORATIVE CONSULTANT RECOMMENDATIONS:")
            for i, rec in enumerate(unique_recommendations[:top_k], 1):
                print(f"   {i}. {rec['name']} (Score: {rec['similarity_score']:.4f}, Source: User {rec['source_user']})")
            
            print("=" * 60)
            return unique_recommendations[:top_k]
            
        except Exception as e:
            print(f"❌ Error in collaborative consultant filtering: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

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
                    'total_surveys_taken': 0,
                    'latest_category_id': None
                }
            
            # Get the latest survey (first row since data is ordered by completed_at DESC)
            latest_survey = user_data.iloc[0]
            
            # Log the category of the latest survey
            category_id = latest_survey['category_id']
            print(f"🏷️  User {user_id} latest survey category: {category_id}")
            
            return {
                'latest_risk_level': latest_survey['risk_level'],
                'latest_score': int(latest_survey['total_score']) if latest_survey['total_score'] else 0,
                'completed_at': latest_survey['completed_at'].isoformat() if pd.notna(latest_survey['completed_at']) else None,
                'total_surveys_taken': len(user_data),
                'latest_category_id': str(category_id) if category_id else None
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
        Enhanced hybrid recommendation system combining content-based and collaborative filtering
        with proper score normalization and weighting
        """
        try:
            print(f"🚀 Starting hybrid recommendations for user: {user_id}")
            print("=" * 60)
            
            # Get user risk summary
            user_risk_info = self.get_user_risk_summary(user_id)
            print(f"📊 User risk info: {user_risk_info}")
            
            # GET CONTENT-BASED AND COLLABORATIVE RECOMMENDATIONS FROM
            # Get content-based recommendations
            content_courses = self.content_based_course_recommendations(user_id, top_k * 2)  # Get more to increase diversity
            print(f"📚 Content-based course recommendations: {len(content_courses)} found")
            content_consultants = self.content_based_consultant_recommendations(user_id, min(6, top_k * 2))
            print(f"👩‍⚕️ Content-based consultant recommendations: {len(content_consultants)} found")
            
            # Get collaborative filtering recommendations
            collab_result = self.collaborative_filtering_recommendations(user_id, top_k * 2)
            collab_courses = collab_result.get('courses', [])
            collab_consultants = collab_result.get('consultants', [])
            print(f"🤝 Collaborative course recommendations: {len(collab_courses)}")
            print(f"🤝 Collaborative consultant recommendations: {len(collab_consultants)} found")
            # GET CONTENT-BASED AND COLLABORATIVE RECOMMENDATIONS TO

            
            # Combine and deduplicate courses with enhanced hybrid scoring
            print(f"🔄 COMBINING COURSE RECOMMENDATIONS:")
            all_courses = content_courses + collab_courses
            course_ids_seen = {}
            for i, course in enumerate(all_courses):
                course_id = course.get('course_id')
                if course_id in course_ids_seen:
                    print(f"   🔄 DUPLICATE FOUND:")
                    print(f"      Course {course_id} appeared before at index {course_ids_seen[course_id]}")
                    print(f"      Previous: {all_courses[course_ids_seen[course_id]]}")
                    print(f"      Current: {course}")
                    print(f"      → Current will be SKIPPED due to deduplication logic")
                else:
                    course_ids_seen[course_id] = i
                    print(f"   ✅ Course {course_id}: {course.get('recommendation_type', 'unknown')} - score: {course.get('score', 0):.3f}, similarity: {course.get('similarity_score', 0):.3f}")
                
            print(f"   Total courses from both methods: {(all_courses)}")
            unique_courses = []
            seen_course_ids = set()
            
            # Weights for hybrid scoring (can be tuned)
            content_weight = 0.5
            collaborative_weight = 0.5
            print(f"📊 COURSE APPEARANCE ORDER:")
            for i, course in enumerate(all_courses):
                course_id = course.get('course_id')
                course_type = course.get('recommendation_type', 'unknown')
                content_score = course.get('score', 0)
                collab_score = course.get('similarity_score', 0)
                print(f"   {i:2d}. {course_id} ({course_type}): content={content_score:.3f}, collab={collab_score:.3f}")
            
            # SMART DEDUPLICATION WITH MERGING - Group all course versions by course_id
            course_groups = {}
            for course in all_courses:
                course_id = course.get('course_id')
                if course_id not in course_groups:
                    course_groups[course_id] = []
                course_groups[course_id].append(course)
            
            print(f"📊 SMART MERGING ANALYSIS:")
            for course_id, course_versions in course_groups.items():
                print(f"   Course {course_id}: {len(course_versions)} versions found")
                for i, version in enumerate(course_versions):
                    content_score = version.get('score', 0)
                    collab_score = version.get('similarity_score', 0)
                    rec_type = version.get('recommendation_type', 'unknown')
                    print(f"      Version {i+1}: {rec_type} - content={content_score:.3f}, collab={collab_score:.3f}")
            
            # Merge all versions of each course
            for course_id, course_versions in course_groups.items():
                # Start with the first version as base
                merged_course = course_versions[0].copy()
                
                # Collect all available scores from all versions
                content_score = 0
                collab_score = 0
                has_content = False
                has_collab = False
                
                for version in course_versions:
                    if 'score' in version and version['score'] > 0:
                        content_score = max(content_score, version['score'])  # Take the highest content score
                        has_content = True
                    if 'similarity_score' in version and version['similarity_score'] > 0:
                        collab_score = max(collab_score, version['similarity_score'])  # Take the highest collab score
                        has_collab = True
                
                # Calculate hybrid score from merged scores
                hybrid_score = (content_score * content_weight) + (collab_score * collaborative_weight)
                
                # Determine source and apply boost
                if has_content and has_collab:
                    # hybrid_score *= 1.1  # 10% boost for items recommended by both methods
                    source = 'both'
                    print(f"   ✅ Course {course_id} MERGED: content={content_score:.3f}, collab={collab_score:.3f}, hybrid={hybrid_score:.3f} (BOOSTED - {source})")
                elif has_content:
                    source = 'content_based'
                    print(f"   📚 Course {course_id}: content={content_score:.3f}, hybrid={hybrid_score:.3f} ({source})")
                else:
                    source = 'collaborative'
                    print(f"   🤝 Course {course_id}: collab={collab_score:.3f}, hybrid={hybrid_score:.3f} ({source})")
                
                # Update merged course with final scores
                if has_content:
                    merged_course['score'] = content_score
                if has_collab:
                    merged_course['similarity_score'] = collab_score
                merged_course['hybrid_score'] = float(hybrid_score)
                merged_course['recommendation_source'] = str(source)
                
                unique_courses.append(merged_course)
            
            # Sort by hybrid score and take top K
            unique_courses.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
            final_courses = unique_courses[:top_k]
            
            # Combine and deduplicate consultants with enhanced hybrid scoring
            print(f"🔄 COMBINING CONSULTANT RECOMMENDATIONS:")
            all_consultants = content_consultants + collab_consultants
            consultant_ids_seen = {}
            for i, consultant in enumerate(all_consultants):
                consultant_id = consultant.get('consultant_id')
                if consultant_id in consultant_ids_seen:
                    print(f"   🔄 DUPLICATE FOUND:")
                    print(f"      Consultant {consultant_id} appeared before at index {consultant_ids_seen[consultant_id]}")
                    print(f"      Previous: {all_consultants[consultant_ids_seen[consultant_id]]}")
                    print(f"      Current: {consultant}")
                    print(f"      → Current will be SKIPPED due to deduplication logic")
                else:
                    consultant_ids_seen[consultant_id] = i
                    print(f"   ✅ Consultant {consultant_id}: {consultant.get('recommendation_type', 'unknown')} - score: {consultant.get('score', 0):.3f}, similarity: {consultant.get('similarity_score', 0):.3f}")
                
            print(f"   Total consultants from both methods: {len(all_consultants)}")
            
            print(f"📊 CONSULTANT APPEARANCE ORDER:")
            for i, consultant in enumerate(all_consultants):
                consultant_id = consultant.get('consultant_id')
                consultant_type = consultant.get('recommendation_type', 'unknown')
                content_score = consultant.get('score', 0)
                collab_score = consultant.get('similarity_score', 0)
                print(f"   {i:2d}. {consultant_id} ({consultant_type}): content={content_score:.3f}, collab={collab_score:.3f}")
            
            # SMART DEDUPLICATION WITH MERGING - Group all consultant versions by consultant_id
            consultant_groups = {}
            for consultant in all_consultants:
                consultant_id = consultant.get('consultant_id')
                if consultant_id not in consultant_groups:
                    consultant_groups[consultant_id] = []
                consultant_groups[consultant_id].append(consultant)
            
            print(f"📊 SMART MERGING ANALYSIS:")
            for consultant_id, consultant_versions in consultant_groups.items():
                print(f"   Consultant {consultant_id}: {len(consultant_versions)} versions found")
                for i, version in enumerate(consultant_versions):
                    content_score = version.get('score', 0)
                    collab_score = version.get('similarity_score', 0)
                    rec_type = version.get('recommendation_type', 'unknown')
                    print(f"      Version {i+1}: {rec_type} - content={content_score:.3f}, collab={collab_score:.3f}")
            
            # Merge all versions of each consultant
            unique_consultants = []
            for consultant_id, consultant_versions in consultant_groups.items():
                # Start with the first version as base
                merged_consultant = consultant_versions[0].copy()
                
                # Collect all available scores from all versions
                content_score = 0
                collab_score = 0
                has_content = False
                has_collab = False
                
                for version in consultant_versions:
                    if 'score' in version and version['score'] > 0:
                        content_score = max(content_score, version['score'])  # Take the highest content score
                        has_content = True
                    if 'similarity_score' in version and version['similarity_score'] > 0:
                        collab_score = max(collab_score, version['similarity_score'])  # Take the highest collab score
                        has_collab = True
                
                # Calculate hybrid score from merged scores
                hybrid_score = (content_score * content_weight) + (collab_score * collaborative_weight)
                
                # Determine source and apply boost
                if has_content and has_collab:
                    # hybrid_score *= 1.1  # 10% boost for items recommended by both methods
                    source = 'both'
                    print(f"   ✅ Consultant {consultant_id} MERGED: content={content_score:.3f}, collab={collab_score:.3f}, hybrid={hybrid_score:.3f} (BOOSTED - {source})")
                elif has_content:
                    source = 'content_based'
                    print(f"   👩‍⚕️ Consultant {consultant_id}: content={content_score:.3f}, hybrid={hybrid_score:.3f} ({source})")
                else:
                    source = 'collaborative'
                    print(f"   🤝 Consultant {consultant_id}: collab={collab_score:.3f}, hybrid={hybrid_score:.3f} ({source})")
                
                # Update merged consultant with final scores
                if has_content:
                    merged_consultant['score'] = content_score
                if has_collab:
                    merged_consultant['similarity_score'] = collab_score
                merged_consultant['hybrid_score'] = float(hybrid_score)
                merged_consultant['recommendation_source'] = str(source)
                
                unique_consultants.append(merged_consultant)
            
            # Sort by hybrid score and take top K
            unique_consultants.sort(key=lambda x: x.get('hybrid_score', 0), reverse=True)
            final_consultants = unique_consultants[:min(5, top_k)]
            
            # Final results summary
            print(f"🎯 HYBRID RECOMMENDATION RESULTS:")
            print(f"   Final courses: {len(final_courses)} (from {len(unique_courses)} unique)")
            print(f"   Final consultants: {len(final_consultants)} (from {len(unique_consultants)} unique)")
            print(f"   Content weight: {content_weight}, Collaborative weight: {collaborative_weight}")
            
            # Show top recommendations
            if final_courses:
                print(f"🏆 Top 3 Course Recommendations:")
                for i, course in enumerate(final_courses[:3], 1):
                    source = course.get('recommendation_source', 'unknown')
                    score = course.get('hybrid_score', 0)
                    print(f"   {i}. {course.get('title', 'Unknown')[:40]}... (Score: {score:.4f}, Source: {source})")
            
            if final_consultants:
                print(f"🏆 Top Consultant Recommendations:")
                for i, consultant in enumerate(final_consultants, 1):
                    source = consultant.get('recommendation_source', 'unknown')
                    score = consultant.get('hybrid_score', 0)
                    print(f"   {i}. {consultant.get('name', 'Unknown')} (Score: {score:.4f}, Source: {source})")
            
            return {
                'courses': final_courses,
                'consultants': final_consultants,
                'user_risk_info': user_risk_info,
                'recommendation_type': 'hybrid',
                'hybrid_config': {
                    'content_weight': content_weight,
                    'collaborative_weight': collaborative_weight,
                    'diversity_boost': 1.1
                },
                'recommendation_summary': {
                    'total_courses': len(final_courses),
                    'total_consultants': len(final_consultants),
                    'content_based_courses': len(content_courses),
                    'collaborative_courses': len(collab_courses),
                    'content_based_consultants': len(content_consultants),
                    'collaborative_consultants': len(collab_consultants),
                    'unique_courses_found': len(unique_courses),
                    'unique_consultants_found': len(unique_consultants)
                },
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Error in hybrid recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
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