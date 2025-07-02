from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.database.database import get_db
from app.service.recommendation_action import get_user_recommendations
from pydantic import BaseModel

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class RecommendationRequest(BaseModel):
    user_id: str
    test_survey_id: Optional[str] = None
    total_score: Optional[int] = None
    risk_level: Optional[str] = None

class CourseRecommendation(BaseModel):
    course_id: str
    title: str
    description: str
    score: float
    difficulty_level: str
    enrollment_count: int
    recommendation_type: str

class ConsultantRecommendation(BaseModel):
    consultant_id: str
    name: str
    specialization: Optional[str]
    experience_years: Optional[int]
    consultation_fee: float
    score: float
    total_appointments: int
    recommendation_type: str

class UserRiskInfo(BaseModel):
    latest_risk_level: Optional[str]
    latest_score: int
    completed_at: Optional[str]
    total_surveys_taken: int

class RecommendationResponse(BaseModel):
    courses: List[CourseRecommendation]
    consultants: List[ConsultantRecommendation]
    user_risk_info: UserRiskInfo
    status: str
    message: Optional[str] = None

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Lấy recommendations cho user dựa trên risk level và hành vi
    """
    try:
        # Gọi service để lấy recommendations
        result = get_user_recommendations(
            user_id=request.user_id,
            test_survey_id=request.test_survey_id or "",
            total_score=request.total_score or 0,
            risk_level=request.risk_level or "",
            db=db
        )
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )
        
        return RecommendationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{user_id}")
def get_user_recommendations_by_id(
    user_id: str,
    test_survey_id: str = "",       # query param
    total_score: int = 0,           # query param
    risk_level: str = "",           # query param
    db: Session = Depends(get_db)
):
    """
    Lấy recommendations cho user theo user_id (không cần request body)
    """
    try:
        result = get_user_recommendations(
            user_id=user_id,
            test_survey_id=test_survey_id,
            total_score=total_score,
            risk_level=risk_level,
            db=db
        )
        
        if result['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result['message']
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{user_id}/courses")
def get_course_recommendations_only(
    user_id: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Chỉ lấy course recommendations
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        courses = recommender.content_based_course_recommendations(user_id, top_k)
        
        return {
            "courses": courses,
            "total": len(courses)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting course recommendations: {str(e)}"
        )

@router.get("/{user_id}/consultants")
def get_consultant_recommendations_only(
    user_id: str,
    top_k: int = 3,
    db: Session = Depends(get_db)
):
    """
    Chỉ lấy consultant recommendations
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        consultants = recommender.content_based_consultant_recommendations(user_id, top_k)
        
        return {
            "consultants": consultants,
            "total": len(consultants)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting consultant recommendations: {str(e)}"
        )

@router.get("/{user_id}/collaborative")
def get_collaborative_recommendations(
    user_id: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Enhanced collaborative filtering recommendations (courses + consultants)
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        result = recommender.collaborative_filtering_recommendations(user_id, top_k)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting collaborative recommendations: {str(e)}"
        )

@router.get("/{user_id}/risk-calculation")
def calculate_risk_from_score(
    user_id: str,
    survey_type_id: str,
    total_score: int,
    db: Session = Depends(get_db)
):
    """
    Tính toán risk level từ score dựa trên rules
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        risk_level = recommender.calculate_risk_level_from_score(survey_type_id, total_score)
        rules = recommender.get_risk_assessment_rules()
        
        return {
            "user_id": user_id,
            "survey_type_id": survey_type_id,
            "total_score": total_score,
            "calculated_risk_level": risk_level,
            "available_rules": rules.get(survey_type_id, [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating risk level: {str(e)}"
        )

@router.get("/{user_id}/recommendation-explanation")
def get_recommendation_explanation(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Giải thích tại sao user được recommend những courses/consultants này
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        recommendations = recommender.hybrid_recommendations(user_id, top_k=5)
        
        # Tạo explanation chi tiết
        explanation = {
            "user_id": user_id,
            "risk_info": recommendations.get('user_risk_info', {}),
            "recommendation_breakdown": recommendations.get('recommendation_summary', {}),
            "course_explanations": [],
            "consultant_explanations": []
        }
        
        # Explain courses
        for course in recommendations.get('courses', []):
            explanation["course_explanations"].append({
                "course_title": course['title'],
                "score": course.get('hybrid_score', course.get('score', 0)),
                "type": course['recommendation_type'],
                "reason": course.get('reason', 'No specific reason'),
                "factors": {
                    "content_based_score": course.get('score', 0) if course['recommendation_type'] in ['content_based', 'hybrid'] else 0,
                    "collaborative_score": course.get('collaborative_score', 0) if course['recommendation_type'] in ['collaborative', 'hybrid'] else 0,
                    "difficulty_match": course.get('difficulty_level', ''),
                    "target_audience_match": True  # Could be calculated
                }
            })
        
        # Explain consultants
        for consultant in recommendations.get('consultants', []):
            explanation["consultant_explanations"].append({
                "consultant_name": consultant['name'],
                "score": consultant['score'],
                "specialization": consultant['specialization'],
                "reason": f"Specialization matches your {recommendations.get('user_risk_info', {}).get('latest_risk_level', 'MEDIUM')} risk level"
            })
        
        return explanation
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendation explanation: {str(e)}"
        )

@router.get("/{user_id}/risk-summary")
def get_user_risk_summary(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy tóm tắt risk assessment của user
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        risk_summary = recommender.get_user_risk_summary(user_id)
        
        return risk_summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting risk summary: {str(e)}"
        )

@router.get("/demo/{user_id}")
def demo_full_recommendation_system(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Demo đầy đủ hệ thống recommendation với tất cả tính năng
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        
        print(f"🔍 Demoing full recommendation system for user: {user_id}")
        # 1. Lấy user risk info
        risk_info = recommender.get_user_risk_summary(user_id)
        print(f"User {user_id} risk summary: {risk_info}")
        
        # 2. Content-based recommendations
        content_courses = recommender.content_based_course_recommendations(user_id, 5)
        print(f"Content-based course recommendations: {len(content_courses)} found")
        
        # 3. Collaborative filtering recommendations  
        collab_courses = recommender.collaborative_filtering_recommendations(user_id, 5)
        print(f"Collaborative filtering course recommendations: {len(collab_courses)} found")
        
        # 4. Consultant recommendations
        consultants = recommender.content_based_consultant_recommendations(user_id, 3)
        print(f"Consultant recommendations: {len(consultants)} found")
        # 5. Hybrid recommendations
        hybrid_result = recommender.hybrid_recommendations(user_id, 10)
        print(f"Hybrid recommendations: {len(hybrid_result.get('courses', []))} courses, {len(hybrid_result.get('consultants', []))} consultants")
        
        return {
            "demo_title": "CRAFFT/ASSIST Recommendation System Demo",
            "user_info": {
                "user_id": user_id,
                "risk_summary": risk_info
            },
            "method_comparison": {
                "content_based": {
                    "courses": content_courses,
                    "count": len(content_courses),
                    "description": "Dựa trên risk level și profile của user"
                },
                "collaborative_filtering": {
                    "courses": collab_courses,
                    "count": len(collab_courses),
                    "description": "Dựa trên hành vi của users tương tự"
                },
                "consultants": {
                    "recommendations": consultants,
                    "count": len(consultants),
                    "description": "Chuyên viên phù hợp với risk level"
                }
            },
            "final_hybrid_result": hybrid_result,
            "system_performance": {
                "total_endpoints": 8,
                "recommendation_methods": ["content_based", "collaborative_filtering", "hybrid"],
                "supported_features": [
                    "Risk level mapping",
                    "TF-IDF similarity",
                    "User behavior analysis", 
                    "Business rules boost",
                    "Hybrid scoring",
                    "Explanation system"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo error: {str(e)}"
        )

@router.get("/data/user-surveys")
def get_all_user_survey_data(
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả dữ liệu survey của users qua SQLAlchemy ORM
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        survey_df = recommender.get_user_survey_data()
        
        if survey_df.empty:
            return {
                "message": "No survey data found",
                "data": [],
                "total_records": 0
            }
        # Chuyển DataFrame thành dict để return JSON
        data = survey_df.to_dict(orient='records')
        
        
        return {
            "message": "Survey data retrieved successfully",
            "data": data,
            "total_records": len(data),
            "columns": list(survey_df.columns),
            "data_types": {col: str(dtype) for col, dtype in survey_df.dtypes.items()}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving survey data: {str(e)}"
        )

@router.get("/data/courses-list")
def get_all_course(
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả dữ liệu survey của users qua SQLAlchemy ORM
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        survey_df = recommender.get_courses_data()
        print(f"Retrieved {len(survey_df)} courses from database")
        
        if survey_df.empty:
            return {
                "message": "No survey data found",
                "data": [],
                "total_records": 0
            }
        # Chuyển DataFrame thành dict để return JSON
        data = survey_df.to_dict(orient='records')
        
        return {
            "message": "Survey data retrieved successfully",
            "data": data,
            "total_records": len(data),
            "columns": list(survey_df.columns),
            "data_types": {col: str(dtype) for col, dtype in survey_df.dtypes.items()}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving survey data: {str(e)}"
        )

@router.get("/data/user-interactions")
def get_all_user_interactions(
    db: Session = Depends(get_db)
):
    """
    Lấy tất cả dữ liệu user interactions (courses + consultants)
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        interactions_df = recommender.get_user_interactions()
        
        if interactions_df.empty:
            return {
                "message": "No interaction data found",
                "data": [],
                "total_records": 0,
                "statistics": {
                    "course_interactions": 0,
                    "consultant_interactions": 0,
                    "unique_users": 0
                }
            }
        
        # Chuyển DataFrame thành dict để return JSON
        data = interactions_df.to_dict(orient='records')
        
        # Tính thống kê
        stats = {
            "course_interactions": len(interactions_df[interactions_df['item_type'] == 'course']),
            "consultant_interactions": len(interactions_df[interactions_df['item_type'] == 'consultant']),
            "unique_users": interactions_df['user_id'].nunique(),
            "unique_courses": len(interactions_df[interactions_df['item_type'] == 'course']['item_id'].unique()),
            "unique_consultants": len(interactions_df[interactions_df['item_type'] == 'consultant']['item_id'].unique()),
            "avg_rating": float(interactions_df['rating'].mean()),
            "rating_distribution": interactions_df['rating'].value_counts().to_dict()
        }
        
        return {
            "message": "User interactions data retrieved successfully",
            "data": data,
            "total_records": len(data),
            "columns": list(interactions_df.columns),
            "statistics": stats,
            "data_types": {col: str(dtype) for col, dtype in interactions_df.dtypes.items()}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user interactions: {str(e)}"
        )

@router.get("/data/user-interactions/{user_id}")
def get_user_interactions_by_id(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Lấy interaction history của một user cụ thể
    """
    try:
        from app.service.recommendation_action import CRAFFTASSISTRecommendationSystem
        
        recommender = CRAFFTASSISTRecommendationSystem(db)
        interactions_df = recommender.get_user_interactions()
        
        if interactions_df.empty:
            return {
                "message": f"No interaction data found for user {user_id}",
                "user_id": user_id,
                "data": [],
                "total_interactions": 0
            }
        
        # Filter cho user cụ thể
        user_interactions = interactions_df[interactions_df['user_id'] == user_id]
        
        if user_interactions.empty:
            return {
                "message": f"No interactions found for user {user_id}",
                "user_id": user_id,
                "data": [],
                "total_interactions": 0
            }
        
        data = user_interactions.to_dict(orient='records')
        
        # Tính thống kê cho user này
        user_stats = {
            "course_interactions": len(user_interactions[user_interactions['item_type'] == 'course']),
            "consultant_interactions": len(user_interactions[user_interactions['item_type'] == 'consultant']),
            "unique_courses": len(user_interactions[user_interactions['item_type'] == 'course']['item_id'].unique()),
            "unique_consultants": len(user_interactions[user_interactions['item_type'] == 'consultant']['item_id'].unique()),
            "avg_rating": float(user_interactions['rating'].mean()),
            "latest_interaction": user_interactions['interaction_date'].max().isoformat() if not user_interactions.empty else None,
            "first_interaction": user_interactions['interaction_date'].min().isoformat() if not user_interactions.empty else None
        }
        
        return {
            "message": f"Interactions for user {user_id} retrieved successfully",
            "user_id": user_id,
            "data": data,
            "total_interactions": len(data),
            "user_statistics": user_stats,
            "columns": list(user_interactions.columns)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving interactions for user {user_id}: {str(e)}"
        )
