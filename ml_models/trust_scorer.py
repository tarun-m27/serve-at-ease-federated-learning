import numpy as np
from datetime import datetime

class TrustScorer:
    """
    Calculates trust scores based on multiple factors:
    - Completion rate
    - Review authenticity
    - Response time
    - Dispute history
    - Anomaly indicators
    """
    
    def __init__(self):
        self.weights = {
            'completion_rate': 0.30,
            'review_authenticity': 0.25,
            'response_time': 0.20,
            'dispute_penalty': 0.15,
            'anomaly_penalty': 0.10
        }
    
    def calculate_trust_score(self, metrics):
        """Calculate overall trust score from individual metrics"""
        completion_score = metrics.get('completion_rate', 0) * 100
        review_score = metrics.get('review_authenticity', 50)
        response_score = metrics.get('response_time_score', 50)
        
        dispute_count = metrics.get('dispute_count', 0)
        dispute_penalty = min(50, dispute_count * 10)
        
        anomaly_score = metrics.get('anomaly_score', 0)
        anomaly_penalty = min(30, anomaly_score)
        
        overall_score = (
            completion_score * self.weights['completion_rate'] +
            review_score * self.weights['review_authenticity'] +
            response_score * self.weights['response_time'] -
            dispute_penalty * self.weights['dispute_penalty'] -
            anomaly_penalty * self.weights['anomaly_penalty']
        )
        
        overall_score = max(0, min(100, overall_score))
        
        return {
            'overall_score': round(overall_score, 2),
            'completion_rate': round(completion_score, 2),
            'review_authenticity': round(review_score, 2),
            'response_time_score': round(response_score, 2),
            'dispute_penalty': round(dispute_penalty, 2),
            'anomaly_penalty': round(anomaly_penalty, 2),
            'trust_level': self._get_trust_level(overall_score)
        }
    
    def _get_trust_level(self, score):
        """Convert numeric score to trust level"""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        elif score >= 20:
            return 'Poor'
        else:
            return 'Very Low'
    
    def calculate_completion_rate(self, total_bookings, completed_bookings):
        """Calculate completion rate metric"""
        if total_bookings == 0:
            return 0.0
        return completed_bookings / total_bookings
    
    def estimate_review_authenticity(self, reviews):
        """Estimate authenticity of reviews (simplified)"""
        if not reviews:
            return 50.0
        
        avg_rating = np.mean([r.get('rating', 3) for r in reviews])
        variance = np.var([r.get('rating', 3) for r in reviews])
        
        review_lengths = [len(r.get('text', '')) for r in reviews]
        avg_length = np.mean(review_lengths) if review_lengths else 0
        
        authenticity = 50.0
        
        if 2 <= avg_rating <= 4.5 and variance > 0.1:
            authenticity += 20
        
        if avg_length > 20:
            authenticity += 15
        
        if len(reviews) > 5:
            authenticity += 15
        
        return min(100, authenticity)
    
    def calculate_response_time_score(self, avg_response_hours):
        """Calculate score based on average response time"""
        if avg_response_hours is None:
            return 50.0
        
        if avg_response_hours <= 1:
            return 100.0
        elif avg_response_hours <= 6:
            return 80.0
        elif avg_response_hours <= 24:
            return 60.0
        elif avg_response_hours <= 48:
            return 40.0
        else:
            return 20.0

trust_scorer = TrustScorer()
