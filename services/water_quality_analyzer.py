# /services/water_quality_analyzer.py
import logging
from utils.error_handler import handle_error

class WaterQualityAnalyzer:
    """Analyzes water quality based on chemistry parameters."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define ideal parameter ranges
        self.ideal_ranges = {
            'ph': (7.2, 7.8),
            'chlorine': (2.0, 4.0),
            'alkalinity': (80, 120)
        }
    
    @handle_error
    def analyze_quality(self, parameters):
        """Analyze water quality based on parameters."""
        self.logger.info(f"Analyzing water quality: {parameters}")
        
        # Calculate score based on parameters
        score = 100
        status = 'good'
        
        # Check pH
        ph = parameters.get('ph')
        if ph:
            ph_min, ph_max = self.ideal_ranges['ph']
            if ph < ph_min or ph > ph_max:
                score -= 20 * min(abs(ph - ph_min), abs(ph - ph_max))
        
        # Check chlorine
        chlorine = parameters.get('chlorine')
        if chlorine:
            cl_min, cl_max = self.ideal_ranges['chlorine']
            if chlorine < cl_min:
                score -= 25 * (cl_min - chlorine) / cl_min
            elif chlorine > cl_max:
                score -= 15 * (chlorine - cl_max) / cl_max
        
        # Check alkalinity
        alkalinity = parameters.get('alkalinity')
        if alkalinity:
            alk_min, alk_max = self.ideal_ranges['alkalinity']
            if alkalinity < alk_min:
                score -= 15 * (alk_min - alkalinity) / alk_min
            elif alkalinity > alk_max:
                score -= 10 * (alkalinity - alk_max) / alk_max
        
        # Determine status based on score
        score = max(0, min(100, score))  # Clamp between 0 and 100
        
        if score < 60:
            status = 'poor'
        elif score < 80:
            status = 'fair'
        
        return {
            'score': round(score, 1),
            'status': status
        }
    
    @handle_error
    def get_recommendations(self, parameters):
        """Get recommendations for improving water quality."""
        self.logger.info(f"Generating recommendations for: {parameters}")
        
        recommendations = []
        
        # Check pH
        ph = parameters.get('ph')
        if ph:
            ph_min, ph_max = self.ideal_ranges['ph']
            if ph < ph_min:
                recommendations.append(f"Increase pH from {ph} to {ph_min}-{ph_max} using pH increaser")
            elif ph > ph_max:
                recommendations.append(f"Decrease pH from {ph} to {ph_min}-{ph_max} using pH decreaser")
        
        # Check chlorine
        chlorine = parameters.get('chlorine')
        if chlorine:
            cl_min, cl_max = self.ideal_ranges['chlorine']
            if chlorine < cl_min:
                recommendations.append(f"Increase chlorine from {chlorine} to {cl_min}-{cl_max} ppm")
            elif chlorine > cl_max:
                recommendations.append(f"Reduce chlorine from {chlorine} to {cl_min}-{cl_max} ppm by adding fresh water")
        
        # Check alkalinity
        alkalinity = parameters.get('alkalinity')
        if alkalinity:
            alk_min, alk_max = self.ideal_ranges['alkalinity']
            if alkalinity < alk_min:
                recommendations.append(f"Increase alkalinity from {alkalinity} to {alk_min}-{alk_max} ppm using alkalinity increaser")
            elif alkalinity > alk_max:
                recommendations.append(f"Decrease alkalinity from {alkalinity} to {alk_min}-{alk_max} ppm")
        
        return recommendations
