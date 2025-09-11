import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum

class DriverType(Enum):
    GOOD = "good"
    BAD = "bad"

class EventType(Enum):
    SPEEDING = "speeding"
    HARD_ACCELERATION = "hard_acceleration"
    HARD_BRAKING = "hard_braking"
    SHARP_TURN = "sharp_turn"

@dataclass
class TelematicsReading:
    timestamp: datetime
    acceleration_x: float  # longitudinal (m/s²)
    acceleration_y: float  # lateral (m/s²)
    acceleration_z: float  # vertical (m/s²)
    velocity: float        # mph
    position_x: float      # meters
    position_y: float      # meters
    engine_on: bool
    trip_id: str

@dataclass
class DrivingEvent:
    event_type: EventType
    timestamp: datetime
    severity: float
    trip_id: str
    velocity: float
    acceleration: float

class NeighborhoodDrivingSimulator:
    def __init__(self, driver_type: DriverType):
        self.driver_type = driver_type
        self.dt = 0.1  # 10Hz sampling rate
        self.g = 9.81  # gravity constant
        
        # Neighborhood driving parameters
        self.max_safe_speed = 30.0  # mph
        self.typical_speed_range = (15, 25) if driver_type == DriverType.GOOD else (20, 35)
        self.stop_sign_frequency = 0.02  # probability per time step
        self.turn_frequency = 0.015
        
        # Driver behavior profiles
        if driver_type == DriverType.GOOD:
            self.speed_compliance = 0.95  # 95% compliance with speed limits
            self.gentle_accel_range = (-0.2, 0.25)  # g-force range
            self.gentle_turn_range = (-0.3, 0.3)   # lateral g-force
        else:
            self.speed_compliance = 0.7   # 70% compliance
            self.aggressive_accel_range = (-0.5, 0.4)
            self.aggressive_turn_range = (-0.45, 0.45)
    
    def generate_trip(self, duration_minutes: int = 15) -> Tuple[List[TelematicsReading], List[DrivingEvent]]:
        """Generate a complete neighborhood driving trip"""
        trip_id = f"trip_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        total_samples = int(duration_minutes * 60 / self.dt)
        readings = []
        events = []
        
        # Initialize state
        current_time = datetime.now()
        velocity = 0.0  # mph
        position_x, position_y = 0.0, 0.0
        engine_on = True
        
        # Trip phases: start, cruise, end
        startup_samples = int(30 / self.dt)  # 30 seconds startup
        shutdown_samples = int(20 / self.dt)  # 20 seconds shutdown
        
        for i in range(total_samples):
            # Determine current phase
            if i < startup_samples:
                phase = "startup"
            elif i > total_samples - shutdown_samples:
                phase = "shutdown"
            else:
                phase = "cruise"
            
            # Generate driving behavior based on phase and driver type
            accel_x, accel_y = self._generate_acceleration(velocity, phase, i)
            
            # Update velocity using kinematic equation (convert acceleration to mph/s)
            accel_x_mph_per_s = accel_x * self.g * 2.237  # convert g to mph/s
            velocity += accel_x_mph_per_s * self.dt
            velocity = max(0, velocity)  # Can't go backwards
            
            # Update position (simplified 2D movement)
            velocity_ms = velocity * 0.44704  # mph to m/s
            position_x += velocity_ms * np.cos(np.radians(self._get_heading(accel_y))) * self.dt
            position_y += velocity_ms * np.sin(np.radians(self._get_heading(accel_y))) * self.dt
            
            # Add some vertical acceleration (road bumps)
            accel_z = np.random.normal(0, 0.05)  # small road vibrations
            
            # Create reading
            reading = TelematicsReading(
                timestamp=current_time,
                acceleration_x=accel_x,
                acceleration_y=accel_y,
                acceleration_z=accel_z,
                velocity=velocity,
                position_x=position_x,
                position_y=position_y,
                engine_on=engine_on,
                trip_id=trip_id
            )
            readings.append(reading)
            
            # Detect events
            trip_events = self._detect_events(reading)
            events.extend(trip_events)
            
            current_time += timedelta(seconds=self.dt)
        
        return readings, events
    
    def _generate_acceleration(self, current_velocity: float, phase: str, sample_idx: int) -> Tuple[float, float]:
        """Generate realistic acceleration patterns"""
        
        if phase == "startup":
            # Gradual acceleration from stop
            if self.driver_type == DriverType.GOOD:
                accel_x = np.random.uniform(0.1, 0.25)  # gentle start
            else:
                accel_x = np.random.uniform(0.2, 0.4)   # aggressive start
            accel_y = np.random.normal(0, 0.05)
            
        elif phase == "shutdown":
            # Gradual deceleration to stop
            if current_velocity > 5:
                if self.driver_type == DriverType.GOOD:
                    accel_x = np.random.uniform(-0.25, -0.1)  # gentle braking
                else:
                    accel_x = np.random.uniform(-0.35, -0.15) # harder braking
            else:
                accel_x = -current_velocity * 0.44704 / (self.g * self.dt)  # come to complete stop
            accel_y = np.random.normal(0, 0.02)
            
        else:  # cruise phase
            # Simulate neighborhood driving scenarios
            scenario = self._get_driving_scenario(current_velocity, sample_idx)
            
            if scenario == "stop_sign":
                # Approaching stop sign
                accel_x = self._generate_stop_sign_behavior(current_velocity)
                accel_y = np.random.normal(0, 0.05)
                
            elif scenario == "turn":
                # Making a turn
                accel_x = np.random.uniform(-0.1, 0.1)  # slight speed adjustment
                accel_y = self._generate_turn_behavior()
                
            elif scenario == "speed_up":
                # Accelerating to target speed
                target_speed = np.random.uniform(*self.typical_speed_range)
                if current_velocity < target_speed:
                    if self.driver_type == DriverType.GOOD:
                        accel_x = np.random.uniform(0.05, 0.2)
                    else:
                        accel_x = np.random.uniform(0.1, 0.35)
                else:
                    accel_x = np.random.uniform(-0.1, 0.05)
                accel_y = np.random.normal(0, 0.03)
                
            else:  # maintain speed
                # Small variations in acceleration
                accel_x = np.random.normal(0, 0.05)
                accel_y = np.random.normal(0, 0.02)
        
        return accel_x, accel_y
    
    def _get_driving_scenario(self, velocity: float, sample_idx: int) -> str:
        """Determine current driving scenario"""
        rand = np.random.random()
        
        if rand < self.stop_sign_frequency:
            return "stop_sign"
        elif rand < self.stop_sign_frequency + self.turn_frequency:
            return "turn"
        elif velocity < self.typical_speed_range[0]:
            return "speed_up"
        else:
            return "maintain"
    
    def _generate_stop_sign_behavior(self, velocity: float) -> float:
        """Generate braking behavior for stop signs"""
        if velocity > 15:  # Far from stop
            if self.driver_type == DriverType.GOOD:
                return np.random.uniform(-0.2, -0.1)  # gradual braking
            else:
                return np.random.uniform(-0.3, -0.15) # moderate braking
        elif velocity > 5:  # Close to stop
            if self.driver_type == DriverType.GOOD:
                return np.random.uniform(-0.25, -0.15)
            else:
                return np.random.uniform(-0.45, -0.25) # hard braking (bad driver waits too long)
        else:
            return np.random.uniform(-0.1, 0.1)  # final approach
    
    def _generate_turn_behavior(self) -> float:
        """Generate lateral acceleration for turns"""
        if self.driver_type == DriverType.GOOD:
            return np.random.uniform(*self.gentle_turn_range)
        else:
            return np.random.uniform(*self.aggressive_turn_range)
    
    def _get_heading(self, lateral_accel: float) -> float:
        """Convert lateral acceleration to approximate heading change"""
        # Simplified heading calculation
        return lateral_accel * 10  # degrees
    
    def _detect_events(self, reading: TelematicsReading) -> List[DrivingEvent]:
        """Detect driving events from telemetry reading"""
        events = []
        
        # Speeding event
        if reading.velocity > self.max_safe_speed:
            events.append(DrivingEvent(
                event_type=EventType.SPEEDING,
                timestamp=reading.timestamp,
                severity=reading.velocity - self.max_safe_speed,
                trip_id=reading.trip_id,
                velocity=reading.velocity,
                acceleration=reading.acceleration_x
            ))
        
        # Hard braking event
        if reading.acceleration_x < -0.35:  # -0.35g threshold
            events.append(DrivingEvent(
                event_type=EventType.HARD_BRAKING,
                timestamp=reading.timestamp,
                severity=abs(reading.acceleration_x),
                trip_id=reading.trip_id,
                velocity=reading.velocity,
                acceleration=reading.acceleration_x
            ))
        
        # Hard acceleration event
        if reading.acceleration_x > 0.35:  # +0.35g threshold
            events.append(DrivingEvent(
                event_type=EventType.HARD_ACCELERATION,
                timestamp=reading.timestamp,
                severity=reading.acceleration_x,
                trip_id=reading.trip_id,
                velocity=reading.velocity,
                acceleration=reading.acceleration_x
            ))
        
        # Sharp turn event
        if abs(reading.acceleration_y) > 0.4:  # ±0.4g threshold
            events.append(DrivingEvent(
                event_type=EventType.SHARP_TURN,
                timestamp=reading.timestamp,
                severity=abs(reading.acceleration_y),
                trip_id=reading.trip_id,
                velocity=reading.velocity,
                acceleration=reading.acceleration_y
            ))
        
        return events

class TelematicsAnalyzer:
    @staticmethod
    def analyze_trip(readings: List[TelematicsReading], events: List[DrivingEvent]) -> Dict:
        """Analyze trip data and generate summary statistics"""
        if not readings:
            return {}
        
        trip_duration = (readings[-1].timestamp - readings[0].timestamp).total_seconds() / 60  # minutes
        max_speed = max(r.velocity for r in readings)
        avg_speed = np.mean([r.velocity for r in readings if r.velocity > 1])  # exclude stopped time
        distance = TelematicsAnalyzer._calculate_distance(readings)
        
        # Event counts
        event_counts = {}
        for event_type in EventType:
            event_counts[event_type.value] = len([e for e in events if e.event_type == event_type])
        
        return {
            "trip_id": readings[0].trip_id,
            "duration_minutes": trip_duration,
            "distance_miles": distance,
            "max_speed_mph": max_speed,
            "avg_speed_mph": avg_speed,
            "total_events": len(events),
            "event_breakdown": event_counts,
            "safety_score": TelematicsAnalyzer._calculate_safety_score(events, trip_duration)
        }
    
    @staticmethod
    def _calculate_distance(readings: List[TelematicsReading]) -> float:
        """Calculate total distance traveled in miles"""
        total_distance_m = 0
        for i in range(1, len(readings)):
            dx = readings[i].position_x - readings[i-1].position_x
            dy = readings[i].position_y - readings[i-1].position_y
            total_distance_m += np.sqrt(dx**2 + dy**2)
        return total_distance_m * 0.000621371  # meters to miles
    
    @staticmethod
    def _calculate_safety_score(events: List[DrivingEvent], trip_duration: float) -> float:
        """Calculate safety score (0-100, higher is better)"""
        base_score = 100
        
        # Deduct points for each event type
        for event in events:
            if event.event_type == EventType.SPEEDING:
                base_score -= min(event.severity * 2, 10)  # up to 10 points per event
            elif event.event_type == EventType.HARD_BRAKING:
                base_score -= 5
            elif event.event_type == EventType.HARD_ACCELERATION:
                base_score -= 3
            elif event.event_type == EventType.SHARP_TURN:
                base_score -= 4
        
        return max(0, base_score)

def run_simulation_comparison():
    """Run simulation for both good and bad drivers and compare results"""
    print("=== Neighborhood Driving Telematics Simulation ===\n")
    
    # Simulate good driver
    good_sim = NeighborhoodDrivingSimulator(DriverType.GOOD)
    good_readings, good_events = good_sim.generate_trip(duration_minutes=12)
    good_analysis = TelematicsAnalyzer.analyze_trip(good_readings, good_events)
    
    # Simulate bad driver
    bad_sim = NeighborhoodDrivingSimulator(DriverType.BAD)
    bad_readings, bad_events = bad_sim.generate_trip(duration_minutes=12)
    bad_analysis = TelematicsAnalyzer.analyze_trip(bad_readings, bad_events)
    
    # Print comparison
    print("GOOD DRIVER RESULTS:")
    print(f"  Trip Duration: {good_analysis['duration_minutes']:.1f} minutes")
    print(f"  Distance: {good_analysis['distance_miles']:.2f} miles")
    print(f"  Max Speed: {good_analysis['max_speed_mph']:.1f} mph")
    print(f"  Avg Speed: {good_analysis['avg_speed_mph']:.1f} mph")
    print(f"  Total Events: {good_analysis['total_events']}")
    print(f"  Safety Score: {good_analysis['safety_score']:.1f}/100")
    print(f"  Event Breakdown: {good_analysis['event_breakdown']}\n")
    
    print("BAD DRIVER RESULTS:")
    print(f"  Trip Duration: {bad_analysis['duration_minutes']:.1f} minutes")
    print(f"  Distance: {bad_analysis['distance_miles']:.2f} miles")
    print(f"  Max Speed: {bad_analysis['max_speed_mph']:.1f} mph")
    print(f"  Avg Speed: {bad_analysis['avg_speed_mph']:.1f} mph")
    print(f"  Total Events: {bad_analysis['total_events']}")
    print(f"  Safety Score: {bad_analysis['safety_score']:.1f}/100")
    print(f"  Event Breakdown: {bad_analysis['event_breakdown']}\n")
    
    # Generate sample data for Kafka (JSON format)
    print("=== Sample Telemetry Data (for Kafka) ===")
    sample_readings = good_readings[:5]  # First 5 readings
    for reading in sample_readings:
        kafka_message = {
            "timestamp": reading.timestamp.isoformat(),
            "vehicle_id": "vehicle_001",
            "trip_id": reading.trip_id,
            "acceleration": {
                "x": round(reading.acceleration_x, 4),
                "y": round(reading.acceleration_y, 4),
                "z": round(reading.acceleration_z, 4)
            },
            "velocity_mph": round(reading.velocity, 2),
            "position": {
                "x": round(reading.position_x, 2),
                "y": round(reading.position_y, 2)
            },
            "engine_on": reading.engine_on
        }
        print(json.dumps(kafka_message, indent=2))
        print("---")
    
    return good_readings, good_events, bad_readings, bad_events

if __name__ == "__main__":
    # Run the simulation
    good_data, good_events, bad_data, bad_events = run_simulation_comparison()
    
    # Optional: Create visualization
    try:
        import matplotlib.pyplot as plt
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Speed over time
        good_times = [(r.timestamp - good_data[0].timestamp).total_seconds() for r in good_data]
        bad_times = [(r.timestamp - bad_data[0].timestamp).total_seconds() for r in bad_data]
        
        ax1.plot(good_times, [r.velocity for r in good_data], 'g-', label='Good Driver', alpha=0.7)
        ax1.plot(bad_times, [r.velocity for r in bad_data], 'r-', label='Bad Driver', alpha=0.7)
        ax1.axhline(y=30, color='orange', linestyle='--', label='Speed Limit')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Speed (mph)')
        ax1.set_title('Speed Profile Comparison')
        ax1.legend()
        ax1.grid(True)
        
        # Acceleration over time
        ax2.plot(good_times, [r.acceleration_x for r in good_data], 'g-', label='Good Driver', alpha=0.7)
        ax2.plot(bad_times, [r.acceleration_x for r in bad_data], 'r-', label='Bad Driver', alpha=0.7)
        ax2.axhline(y=0.35, color='orange', linestyle='--', label='Hard Accel Threshold')
        ax2.axhline(y=-0.35, color='orange', linestyle='--', label='Hard Brake Threshold')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Acceleration (g)')
        ax2.set_title('Longitudinal Acceleration')
        ax2.legend()
        ax2.grid(True)
        
        # Route visualization
        ax3.plot([r.position_x for r in good_data], [r.position_y for r in good_data], 'g-', label='Good Driver', alpha=0.7)
        ax3.plot([r.position_x for r in bad_data], [r.position_y for r in bad_data], 'r-', label='Bad Driver', alpha=0.7)
        ax3.set_xlabel('X Position (m)')
        ax3.set_ylabel('Y Position (m)')
        ax3.set_title('Driving Route')
        ax3.legend()
        ax3.grid(True)
        ax3.axis('equal')
        
        # Event comparison
        good_event_types = [e.event_type.value for e in good_events]
        bad_event_types = [e.event_type.value for e in bad_events]
        
        all_event_types = list(set(good_event_types + bad_event_types))
        good_counts = [good_event_types.count(et) for et in all_event_types]
        bad_counts = [bad_event_types.count(et) for et in all_event_types]
        
        x = range(len(all_event_types))
        width = 0.35
        
        ax4.bar([i - width/2 for i in x], good_counts, width, label='Good Driver', color='green', alpha=0.7)
        ax4.bar([i + width/2 for i in x], bad_counts, width, label='Bad Driver', color='red', alpha=0.7)
        ax4.set_xlabel('Event Type')
        ax4.set_ylabel('Event Count')
        ax4.set_title('Driving Events Comparison')
        ax4.set_xticks(x)
        ax4.set_xticklabels(all_event_types, rotation=45)
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Matplotlib not available. Skipping visualization.")
        print("Install with: pip install matplotlib")