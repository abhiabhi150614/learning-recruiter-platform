from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.onboarding import Onboarding
from app.models.learning_plan import LearningPlan
from app.models.quiz import Quiz
from app.models.student_profile_summary import StudentProfileSummary
from app.core.embeddings import simple_text_embedding, cosine_similarity
import json


class GraphRAG:
    """Graph-based Retrieval Augmented Generation for candidate matching"""
    
    def __init__(self, db: Session):
        self.db = db
        self.knowledge_graph = {}
        self.user_embeddings = {}
        
    def build_knowledge_graph(self) -> Dict[str, Any]:
        """Build comprehensive knowledge graph from all user data"""
        users = self.db.query(User).all()
        graph = {
            "users": {},
            "skills": {},
            "topics": {},
            "learning_paths": {},
            "connections": []
        }
        
        for user in users:
            user_data = self._extract_user_knowledge(user.id)
            graph["users"][str(user.id)] = user_data
            
            # Build skill and topic nodes
            for skill in user_data.get("skills", []):
                if skill not in graph["skills"]:
                    graph["skills"][skill] = {"users": [], "related_topics": []}
                graph["skills"][skill]["users"].append(user.id)
            
            for topic in user_data.get("topics", []):
                if topic not in graph["topics"]:
                    graph["topics"][topic] = {"users": [], "related_skills": []}
                graph["topics"][topic]["users"].append(user.id)
        
        # Build connections between users based on similarity
        self._build_user_connections(graph)
        
        self.knowledge_graph = graph
        return graph
    
    def _extract_user_knowledge(self, user_id: int) -> Dict[str, Any]:
        """Extract comprehensive knowledge about a user"""
        # Get onboarding data
        onboarding = self.db.query(Onboarding).filter(Onboarding.user_id == user_id).first()
        
        # Get learning plan data
        learning_plan = self.db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
        
        # Get quiz performance
        quizzes = self.db.query(Quiz).filter(Quiz.user_id == user_id).all()
        
        # Extract skills and topics from learning plan
        skills = []
        topics = []
        completed_months = 0
        total_progress = 0
        
        if learning_plan and learning_plan.plan:
            months = learning_plan.plan.get("months", [])
            for month in months:
                if month.get("status") == "completed":
                    completed_months += 1
                
                month_topics = month.get("topics", [])
                if isinstance(month_topics, list):
                    topics.extend([t for t in month_topics if isinstance(t, str)])
                
                # Extract skills from topics (simplified)
                for topic in month_topics:
                    if isinstance(topic, str):
                        # Simple skill extraction logic
                        if any(tech in topic.lower() for tech in ["python", "javascript", "react", "node"]):
                            skills.append(topic)
            
            total_progress = completed_months / len(months) if months else 0
        
        # Get quiz performance metrics - fix for Quiz model
        quiz_scores = []
        for q in quizzes:
            # Try to get score from quiz submissions or use a default
            if hasattr(q, 'submissions') and q.submissions:
                scores = [s.score for s in q.submissions if hasattr(s, 'score') and s.score is not None]
                if scores:
                    quiz_scores.extend(scores)
        avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Extract career goals and interests
        career_goals = []
        current_skills = []
        
        if onboarding:
            if isinstance(onboarding.career_goals, list):
                career_goals = onboarding.career_goals
            elif isinstance(onboarding.career_goals, str):
                career_goals = [onboarding.career_goals]
            
            if isinstance(onboarding.current_skills, list):
                current_skills = onboarding.current_skills
            elif isinstance(onboarding.current_skills, str):
                current_skills = [onboarding.current_skills]
        
        return {
            "user_id": user_id,
            "skills": list(set(skills + current_skills)),
            "topics": list(set(topics)),
            "career_goals": career_goals,
            "learning_progress": total_progress,
            "completed_months": completed_months,
            "avg_quiz_score": avg_quiz_score,
            "total_quizzes": len(quizzes),
            "grade": getattr(onboarding, "grade", None) if onboarding else None,
            "time_commitment": getattr(onboarding, "time_commitment", None) if onboarding else None
        }
    
    def _build_user_connections(self, graph: Dict[str, Any]):
        """Build connections between users based on similarity"""
        users = list(graph["users"].keys())
        
        for i, user1 in enumerate(users):
            for user2 in users[i+1:]:
                similarity = self._calculate_user_similarity(
                    graph["users"][user1], 
                    graph["users"][user2]
                )
                
                if similarity > 0.3:  # Threshold for meaningful connection
                    graph["connections"].append({
                        "user1": int(user1),
                        "user2": int(user2),
                        "similarity": similarity,
                        "connection_type": "learning_similarity"
                    })
    
    def _calculate_user_similarity(self, user1_data: Dict, user2_data: Dict) -> float:
        """Calculate similarity between two users"""
        # Skill overlap
        skills1 = set(user1_data.get("skills", []))
        skills2 = set(user2_data.get("skills", []))
        skill_similarity = len(skills1.intersection(skills2)) / len(skills1.union(skills2)) if skills1.union(skills2) else 0
        
        # Topic overlap
        topics1 = set(user1_data.get("topics", []))
        topics2 = set(user2_data.get("topics", []))
        topic_similarity = len(topics1.intersection(topics2)) / len(topics1.union(topics2)) if topics1.union(topics2) else 0
        
        # Career goal similarity
        goals1 = set(user1_data.get("career_goals", []))
        goals2 = set(user2_data.get("career_goals", []))
        goal_similarity = len(goals1.intersection(goals2)) / len(goals1.union(goals2)) if goals1.union(goals2) else 0
        
        # Progress similarity
        progress1 = user1_data.get("learning_progress", 0)
        progress2 = user2_data.get("learning_progress", 0)
        progress_similarity = 1 - abs(progress1 - progress2)
        
        # Weighted combination
        return (
            skill_similarity * 0.4 +
            topic_similarity * 0.3 +
            goal_similarity * 0.2 +
            progress_similarity * 0.1
        )
    
    def enhanced_candidate_matching(self, job_description: str, requirements: List[str] = None) -> List[Dict[str, Any]]:
        """Enhanced candidate matching using graph RAG"""
        if not self.knowledge_graph:
            self.build_knowledge_graph()
        
        # Create job embedding
        job_text = f"{job_description} {' '.join(requirements or [])}"
        job_embedding = simple_text_embedding(job_text)
        
        candidates = []
        
        for user_id, user_data in self.knowledge_graph["users"].items():
            # Create user profile text for embedding
            profile_text = self._create_user_profile_text(user_data)
            user_embedding = simple_text_embedding(profile_text)
            
            # Calculate base similarity
            base_score = cosine_similarity(job_embedding, user_embedding)
            
            # Apply graph-based enhancements
            enhanced_score = self._apply_graph_enhancements(
                int(user_id), base_score, job_description, requirements or []
            )
            
            candidates.append({
                "user_id": int(user_id),
                "base_score": float(base_score),
                "enhanced_score": float(enhanced_score),
                "user_data": user_data,
                "match_reasons": self._generate_match_reasons(user_data, job_description, requirements or [])
            })
        
        # Sort by enhanced score
        candidates.sort(key=lambda x: x["enhanced_score"], reverse=True)
        
        return candidates
    
    def _create_user_profile_text(self, user_data: Dict[str, Any]) -> str:
        """Create comprehensive text representation of user profile"""
        parts = []
        
        if user_data.get("skills"):
            parts.append(f"Skills: {', '.join(user_data['skills'])}")
        
        if user_data.get("topics"):
            parts.append(f"Learning topics: {', '.join(user_data['topics'])}")
        
        if user_data.get("career_goals"):
            parts.append(f"Career goals: {', '.join(user_data['career_goals'])}")
        
        parts.append(f"Learning progress: {user_data.get('learning_progress', 0):.1%}")
        parts.append(f"Completed months: {user_data.get('completed_months', 0)}")
        parts.append(f"Average quiz score: {user_data.get('avg_quiz_score', 0):.1%}")
        
        if user_data.get("grade"):
            parts.append(f"Grade level: {user_data['grade']}")
        
        return " | ".join(parts)
    
    def _apply_graph_enhancements(self, user_id: int, base_score: float, job_description: str, requirements: List[str]) -> float:
        """Apply graph-based enhancements to matching score"""
        enhanced_score = base_score
        
        # Find similar users and boost score based on their performance
        similar_users = self._find_similar_users(user_id)
        if similar_users:
            avg_similar_score = sum(self._calculate_job_fit(uid, job_description, requirements) for uid in similar_users) / len(similar_users)
            enhanced_score += avg_similar_score * 0.2  # 20% boost from similar users
        
        # Boost based on learning trajectory
        user_data = self.knowledge_graph["users"][str(user_id)]
        if user_data.get("learning_progress", 0) > 0.7:  # High progress
            enhanced_score *= 1.1
        
        if user_data.get("avg_quiz_score", 0) > 0.8:  # High quiz performance
            enhanced_score *= 1.05
        
        return min(enhanced_score, 1.0)  # Cap at 1.0
    
    def _find_similar_users(self, user_id: int) -> List[int]:
        """Find users similar to the given user"""
        similar_users = []
        
        for connection in self.knowledge_graph.get("connections", []):
            if connection["user1"] == user_id and connection["similarity"] > 0.5:
                similar_users.append(connection["user2"])
            elif connection["user2"] == user_id and connection["similarity"] > 0.5:
                similar_users.append(connection["user1"])
        
        return similar_users[:5]  # Top 5 similar users
    
    def _calculate_job_fit(self, user_id: int, job_description: str, requirements: List[str]) -> float:
        """Calculate how well a user fits a job"""
        user_data = self.knowledge_graph["users"][str(user_id)]
        
        # Simple job fit calculation based on skill overlap
        user_skills = set(skill.lower() for skill in user_data.get("skills", []))
        job_skills = set()
        
        # Extract skills from job description and requirements
        for req in requirements:
            job_skills.update(req.lower().split())
        
        job_skills.update(job_description.lower().split())
        
        # Filter to relevant technical skills
        tech_keywords = {"python", "javascript", "react", "node", "aws", "docker", "sql", "java", "c++"}
        job_tech_skills = job_skills.intersection(tech_keywords)
        user_tech_skills = user_skills.intersection(tech_keywords)
        
        if not job_tech_skills:
            return 0.5  # Default score if no tech skills identified
        
        overlap = len(user_tech_skills.intersection(job_tech_skills))
        return overlap / len(job_tech_skills)
    
    def _generate_match_reasons(self, user_data: Dict[str, Any], job_description: str, requirements: List[str]) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        # Skill matches
        user_skills = [skill.lower() for skill in user_data.get("skills", [])]
        job_text = (job_description + " " + " ".join(requirements)).lower()
        
        matching_skills = [skill for skill in user_skills if skill in job_text]
        if matching_skills:
            reasons.append(f"Strong skill match: {', '.join(matching_skills[:3])}")
        
        # Learning progress
        progress = user_data.get("learning_progress", 0)
        if progress > 0.8:
            reasons.append("Excellent learning progress (80%+ completion)")
        elif progress > 0.5:
            reasons.append("Good learning progress (50%+ completion)")
        
        # Quiz performance
        quiz_score = user_data.get("avg_quiz_score", 0)
        if quiz_score > 0.8:
            reasons.append("High quiz performance (80%+ average)")
        
        # Career alignment
        career_goals = [goal.lower() for goal in user_data.get("career_goals", [])]
        if any(goal in job_text for goal in career_goals):
            reasons.append("Career goals align with position")
        
        return reasons[:3]  # Top 3 reasons
    
    def get_user_learning_insights(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive learning insights for a user"""
        if not self.knowledge_graph:
            self.build_knowledge_graph()
        
        user_data = self.knowledge_graph["users"].get(str(user_id))
        if not user_data:
            return {"error": "User not found"}
        
        similar_users = self._find_similar_users(user_id)
        
        # Get learning recommendations
        recommendations = self._generate_learning_recommendations(user_data, similar_users)
        
        return {
            "user_profile": user_data,
            "similar_users": similar_users,
            "learning_recommendations": recommendations,
            "strengths": self._identify_strengths(user_data),
            "growth_areas": self._identify_growth_areas(user_data),
            "career_readiness": self._assess_career_readiness(user_data)
        }
    
    def _generate_learning_recommendations(self, user_data: Dict[str, Any], similar_users: List[int]) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Based on progress
        progress = user_data.get("learning_progress", 0)
        if progress < 0.3:
            recommendations.append("Focus on completing current learning modules")
        elif progress > 0.7:
            recommendations.append("Consider advanced topics or specialization")
        
        # Based on quiz performance
        quiz_score = user_data.get("avg_quiz_score", 0)
        if quiz_score < 0.6:
            recommendations.append("Review fundamental concepts and practice more quizzes")
        
        # Based on similar users' success
        if similar_users:
            recommendations.append("Connect with similar learners for peer learning")
        
        return recommendations
    
    def _identify_strengths(self, user_data: Dict[str, Any]) -> List[str]:
        """Identify user's learning strengths"""
        strengths = []
        
        if user_data.get("learning_progress", 0) > 0.7:
            strengths.append("Consistent learning progress")
        
        if user_data.get("avg_quiz_score", 0) > 0.8:
            strengths.append("Strong knowledge retention")
        
        if len(user_data.get("skills", [])) > 5:
            strengths.append("Diverse skill set")
        
        return strengths
    
    def _identify_growth_areas(self, user_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        growth_areas = []
        
        if user_data.get("learning_progress", 0) < 0.5:
            growth_areas.append("Increase learning consistency")
        
        if user_data.get("avg_quiz_score", 0) < 0.7:
            growth_areas.append("Improve knowledge retention")
        
        if len(user_data.get("skills", [])) < 3:
            growth_areas.append("Expand skill portfolio")
        
        return growth_areas
    
    def _assess_career_readiness(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess user's readiness for career opportunities"""
        progress = user_data.get("learning_progress", 0)
        quiz_score = user_data.get("avg_quiz_score", 0)
        skill_count = len(user_data.get("skills", []))
        
        # Simple scoring algorithm
        readiness_score = (progress * 0.4 + quiz_score * 0.4 + min(skill_count / 5, 1) * 0.2)
        
        if readiness_score > 0.8:
            level = "High"
            description = "Ready for advanced positions"
        elif readiness_score > 0.6:
            level = "Medium"
            description = "Ready for entry-level positions"
        else:
            level = "Developing"
            description = "Continue learning to improve readiness"
        
        return {
            "score": readiness_score,
            "level": level,
            "description": description
        }