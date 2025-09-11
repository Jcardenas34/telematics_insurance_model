import numpy as np
import pandas as pd
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class DrivingBehavior(Enum):
    GOOD = "good"
    AGGRESSIVE = "aggressive"
    MIXED = "mixed"

@dataclass
class TelematicsEvent:
    timestamp: datetime
    acceleration: float  # mph²
    velocity: float     # mph
    position: float     # miles from start
    trip_id: str
    behavior_type: DrivingBehavior

class TelematicsSimulator:
    def __init__(self, sampling_rate_hz: float = 10.0):
        self.sampling_rate = sampling_rate_hz
        self.time_delta = 1.0 / sampling_rate_hz  # seconds
        
        # Driving behavior parameters
        self.speeding_threshold = 30.0  # mph
        self.hard_brake_threshold = -7.7  
        self.hard_accel_threshold = 4.5   
        
        # Current state
        self.reset_trip()
        
    def reset_trip(self):
        """Reset trip state for new trip"""
        self.current_velocity = 0.0
        self.current_position = 0.0
        self.trip_start_time = datetime.now()
        self.trip_id = f"trip_{int(time.time())}"
        
    def generate_driving_scenario(self, behavior: DrivingBehavior, duration_minutes: float) -> List[float]:
        """Generate acceleration pattern for different driving behaviors"""
        total_samples = int(duration_minutes * 60 * self.sampling_rate)
        accelerations = []
        
        if behavior == DrivingBehavior.GOOD:
            accelerations = self._generate_good_driving(total_samples)
        elif behavior == DrivingBehavior.AGGRESSIVE:
            accelerations = self._generate_aggressive_driving(total_samples)
        else:  # MIXED
            accelerations = self._generate_mixed_driving(total_samples)
            
        return accelerations
    
    def _generate_good_driving(self, samples: int) -> List[float]:
        """Generate smooth, gradual acceleration patterns"""
        accelerations = []
        
        # Phases: startup, cruise, city driving, highway, stopping
        phases = [
            ("startup", 0.1),      # 10% startup
            ("city", 0.3),         # 30% city driving
            ("highway", 0.4),      # 40% highway
            ("city", 0.15),        # 15% more city
            ("stopping", 0.05)     # 5% stopping
        ]
        
        for phase_name, phase_ratio in phases:
            phase_samples = int(samples * phase_ratio)
            
            if phase_name == "startup":
                # Gradual acceleration from 0 to 25 mph
                accel = np.linspace(0.1, 0.15, phase_samples)
                accel += np.random.normal(0, 0.002, phase_samples)
                
            elif phase_name == "city":
                # Stop and go traffic, gentle accelerations
                accel = []
                for _ in range(phase_samples):
                    if random.random() < 0.3:  # 30% chance of acceleration/deceleration
                        accel.append(random.uniform(-0.05, 0.15))
                    else:
                        accel.append(random.uniform(-0.05, 0.05))
                        
            elif phase_name == "highway":
                # Steady cruise with minor adjustments
                accel = np.random.normal(0, 0.003, phase_samples)
                
            elif phase_name == "stopping":
                # Gradual deceleration
                accel = np.linspace(-0.15, -0.01, phase_samples)
                accel += np.random.normal(0, 0.02, phase_samples)
                
            accelerations.extend(accel)
            
        return accelerations[:samples]
    
    def _generate_aggressive_driving(self, samples: int) -> List[float]:
        """Generate aggressive driving with hard accelerations and braking"""
        accelerations = []
        
        base_accel = np.random.normal(0, 0.01, samples)
        
        # Add aggressive events
        num_hard_events = int(samples * 0.05)  # 5% of samples have hard events
        
        for i in range(num_hard_events):
            event_idx = random.randint(0, samples - 1)
            
            if random.random() < 0.6:  # 60% hard braking, 40% hard acceleration
                # Hard braking event
                intensity = random.uniform(-0.045, -0.025)  # Hard brake range
                duration = random.randint(5, 15)  # 0.5-1.5 seconds
                
                for j in range(duration):
                    if event_idx + j < samples:
                        base_accel[event_idx + j] = intensity * (1 - j/duration)
            else:
                # Hard acceleration event
                intensity = random.uniform(4.5, 0.040)  # Hard acceleration
                duration = random.randint(10, 25)  # 1-2.5 seconds
                
                for j in range(duration):
                    if event_idx + j < samples:
                        base_accel[event_idx + j] = intensity * (1 - j/duration)
        
        return base_accel.tolist()
    
    def _generate_mixed_driving(self, samples: int) -> List[float]:
        """Generate mixed driving with some aggressive events"""
        # 70% good driving, 30% aggressive
        good_samples = int(samples * 0.7)
        aggressive_samples = samples - good_samples
        
        good_accel = self._generate_good_driving(good_samples)
        aggressive_accel = self._generate_aggressive_driving(aggressive_samples)
        
        # Randomly interleave the patterns
        mixed_accel = good_accel + aggressive_accel
        random.shuffle(mixed_accel)
        
        return mixed_accel
    
    def simulate_trip(self, behavior: DrivingBehavior, duration_minutes: float) -> List[TelematicsEvent]:
        """Simulate a complete trip with given behavior"""
        self.reset_trip()
        
        accelerations = self.generate_driving_scenario(behavior, duration_minutes)
        events = []
        
        current_time = self.trip_start_time
        
        for accel in accelerations:
            # Apply kinematic equations - acceleration is in mph/s
            new_velocity = max(0, self.current_velocity + (accel * self.time_delta))
            # Position: s = ut + (1/2)at² where distances are in miles, time in hours
            velocity_change = (self.current_velocity * self.time_delta / 3600) + \
                            (0.5 * accel * (self.time_delta / 3600) * self.time_delta)
            new_position = self.current_position + velocity_change
            
            # Create telemetry event
            event = TelematicsEvent(
                timestamp=current_time,
                acceleration=accel,
                velocity=new_velocity,
                position=new_position,
                trip_id=self.trip_id,
                behavior_type=behavior
            )
            
            events.append(event)
            
            # Update state
            self.current_velocity = new_velocity
            self.current_position = new_position
            current_time += timedelta(seconds=self.time_delta)
            
        return events
    
    def analyze_trip_metrics(self, events: List[TelematicsEvent]) -> Dict:
        """Analyze trip for driving behavior metrics"""
        metrics = {
            'trip_id': events[0].trip_id if events else None,
            'trip_duration_minutes': len(events) / self.sampling_rate / 60,
            'trip_distance_miles': events[-1].position if events else 0,
            'max_speed_mph': max([e.velocity for e in events]) if events else 0,
            'avg_speed_mph': np.mean([e.velocity for e in events]) if events else 0,
            'speeding_events': 0,
            'hard_accelerations': 0,
            'hard_brakes': 0,
            'total_events': len(events)
        }
        
        speeding_streak = False
        
        for event in events:
            # Count speeding events (continuous speeding counts as one event)
            if event.velocity > self.speeding_threshold:
                if not speeding_streak:
                    metrics['speeding_events'] += 1
                    speeding_streak = True
            else:
                speeding_streak = False
                
            # Count hard events
            if event.acceleration > self.hard_accel_threshold:
                metrics['hard_accelerations'] += 1
            elif event.acceleration < self.hard_brake_threshold:
                metrics['hard_brakes'] += 1
        
        return metrics

def simulate_kafka_producer(events: List[TelematicsEvent], delay_seconds: float = 0.1):
    """Simulate real-time data streaming (like Kafka producer)"""
    print("Starting real-time telemetry stream...")
    print("=" * 50)
    
    for i, event in enumerate(events):
        # Convert to JSON-like format (what would be sent to Kafka)
        kafka_message = {
            'timestamp': event.timestamp.isoformat(),
            'acceleration': round(event.acceleration, 6),
            'velocity': round(event.velocity, 2),
            'position': round(event.position, 4),
            'trip_id': event.trip_id,
            'behavior_type': event.behavior_type.value
        }
        
        print(f"Event {i+1:4d}: {json.dumps(kafka_message, indent=2)}")
        
        if delay_seconds > 0:
            time.sleep(delay_seconds)
            
        # Stop after 20 events for demo
        if i >= 19:
            print("\n... (truncated for demo)")
            break

def main():
    """Main simulation function"""
    simulator = TelematicsSimulator(sampling_rate_hz=1.0)  # 1 Hz for demo
    
    print("Telematics Data Simulator")
    print("=" * 40)
    
    # Simulate different driving behaviors
    behaviors = [
        (DrivingBehavior.GOOD, 30, "Good Driver - City Commute"),
        (DrivingBehavior.AGGRESSIVE,30, "Aggressive Driver - Rush Hour"),
        (DrivingBehavior.MIXED, 30, "Mixed Behavior - Weekend Drive")
    ]
    
    all_metrics = []
    
    for behavior, duration, description in behaviors:
        print(f"\n{description}")
        print("-" * len(description))
        
        # Simulate trip
        events = simulator.simulate_trip(behavior, duration)
        
        # Analyze metrics
        metrics = simulator.analyze_trip_metrics(events)
        all_metrics.append(metrics)
        
        # Print summary
        print(f"Trip Duration: {metrics['trip_duration_minutes']:.1f} minutes")
        print(f"Distance: {metrics['trip_distance_miles']:.2f} miles")
        print(f"Max Speed: {metrics['max_speed_mph']:.1f} mph")
        print(f"Avg Speed: {metrics['avg_speed_mph']:.1f} mph")
        print(f"Speeding Events: {metrics['speeding_events']}")
        print(f"Hard Accelerations: {metrics['hard_accelerations']}")
        print(f"Hard Brakes: {metrics['hard_brakes']}")
        
        # Simulate real-time streaming for first trip
        if behavior == DrivingBehavior.GOOD:
            print(f"\nReal-time stream sample for {description}:")
            simulate_kafka_producer(events[:20], delay_seconds=0.2)
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("TRIP COMPARISON SUMMARY")
    print("=" * 60)
    
    df = pd.DataFrame(all_metrics)
    print(df[['trip_id', 'trip_duration_minutes', 'max_speed_mph', 
              'speeding_events', 'hard_accelerations', 'hard_brakes']].to_string(index=False))

if __name__ == "__main__":
    main()