import numpy as np

from typing import List, Dict
from telematics_insurance_model.utils.simulate import TelematicsDataPoint
from telematics_insurance_model.helpers.logger import logger



class TripAnalyzer:
    """
    Analyzes trip data for risk scoring metrics
    
    """
    
    def __init__(self):
        self.speeding_threshold = 30.0  # mph
        self.hard_braking_threshold = -0.35  # g
        self.hard_acceleration_threshold = 0.35  # g
    
    def analyze_trip(self, trip_data: List[TelematicsDataPoint]) -> Dict:
        """Analyze trip for risk metrics"""
        if not trip_data:
            return {}
        
        speeds = [point.speed_mph for point in trip_data]
        accelerations = [point.acceleration_g for point in trip_data]
        
        # Calculate trip length (estimated miles based on points and average speed)
        avg_speed = np.mean([s for s in speeds if s > 0])
        trip_duration_hours = len(trip_data) * 1 / (3*3600)  # 3 measurements a seconds converted to hours
        estimated_trip_miles = avg_speed * trip_duration_hours
        
        speeding_events = 0
        speed_counter = 0
        track_speed = False
        # only count something as a speeding event if the speed threshold is crossed
        for k in range(1,len(speeds)):
            if speeds[k-1] < self.speeding_threshold and speeds[k] > self.speeding_threshold:
                track_speed = True

            if speeds[k] > self.speeding_threshold:
                speed_counter += 1
                if speed_counter >=9 and track_speed:  # Sustained speeding for at least 9 measurements (~3 second)
                    speeding_events += 1
                    track_speed = False  # Reset tracking after counting an event
            else:
                speed_counter = 0
                track_speed = False



        # Speeding events
        # speeding_events = sum(1 for speed in speeds if speed > self.speeding_threshold)
        
        # Hard braking events
        hard_braking_events = sum(1 for accel in accelerations 
                                if accel <= self.hard_braking_threshold)
        
        # Hard acceleration events
        hard_acceleration_events = sum(1 for accel in accelerations 
                                     if accel >= self.hard_acceleration_threshold)
        
        # Additional metrics
        max_deceleration = min(accelerations) if accelerations else 0
        max_acceleration = max(accelerations) if accelerations else 0
        
        # Trip statistics
        analysis = {
            'trip_id': trip_data[0].trip_id,
            'driver_id': trip_data[0].driver_id,
            'trip_length_miles': round(estimated_trip_miles, 2),
            'trip_duration_minutes': round(len(trip_data) * 1 / (3*60), 1),
            'data_points': len(trip_data),
            'max_speed': round(max(speeds), 1),
            'avg_speed': round(np.mean(speeds), 1),
            'speeding_events': speeding_events,
            'hard_braking_events': hard_braking_events,
            'hard_acceleration_events': hard_acceleration_events,
            'max_acceleration': round(max_acceleration, 3),
            'max_deceleration': round(max_deceleration, 3),
            'risk_score': self.calculate_risk_score(
                speeding_events, hard_braking_events, hard_acceleration_events, 
                estimated_trip_miles, len(trip_data)
            )
        }
        
        return analysis
    
    def calculate_risk_score(self, speeding_events: int, hard_braking_events: int,
                           hard_acceleration_events: int, trip_miles: float, 
                           data_points: int) -> float:
        """Calculate a comprehensive risk score (0-100)"""
        if trip_miles == 0 or data_points == 0:
            return 0
        
        # Normalize by trip distance and time
        speeding_rate = (speeding_events / data_points) * 100
        hard_braking_rate = (hard_braking_events / data_points) * 100
        hard_acceleration_rate = (hard_acceleration_events / data_points) * 100
        
        # Weighted risk score calculation
        risk_score = (
            speeding_rate * 0.4 +         # 40% weight for speeding
            hard_braking_rate * 0.3 +     # 30% weight for hard braking
            hard_acceleration_rate * 0.3  # 30% weight for hard acceleration
        )
        
        # Apply trip length modifier (shorter trips are less reliable indicators)
        if trip_miles < 1.0:
            risk_score *= 0.8  # Reduce score for very short trips
        
        return min(100, max(0, round(risk_score, 2)))  # Cap between 0-100
