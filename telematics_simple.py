#!/usr/bin/env python3
"""
Simple Telematics Data Simulation System (No Kafka Dependencies)
Generates realistic driving data with good/bad behaviors
"""

import json
import random
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import List, Tuple, Dict
import logging

import numpy as np

def moving_average(data, window_size):
    # Create a boxcar kernel (all ones) and normalize it
    kernel = np.ones(window_size) / window_size
    # Convolve the data with the kernel
    # 'same' mode ensures the output array has the same length as the input
    smoothed_data = np.convolve(data, kernel, mode='same')
    return smoothed_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TelematicsDataPoint:
    """Represents a single telematics data point"""
    timestamp: str
    latitude: float
    longitude: float
    speed_mph: float
    acceleration_g: float
    driver_id: str
    trip_id: str

class TelematicsSimulator:
    """Simulates realistic telematics data for different driver behaviors"""
    
    def __init__(self):
        # Physics constants
        self.GRAVITY = 9.81  # m/s²
        self.MPH_TO_MS = 0.44704  # conversion factor
        
        # Driver behavior parameters
        self.good_driver_params = {
            'max_speed': 28,  # mph
            'ave_speed': 26,  # mph
            'avg_acceleration': 0.15,  # g
            'max_acceleration': 0.25,  # g
            'speeding_probability': 0.05,
            'hard_event_probability': 0.2
        }
        
        self.bad_driver_params = {
            'max_speed': 45,  # mph
            'ave_speed': 29,  # mph
            'avg_acceleration': 0.25,  # g
            'max_acceleration': 0.50,  # g
            'speeding_probability': 0.15,
            'hard_event_probability': 0.8
        }
    
    def generate_trip_route(self, start_lat: float, start_lon: float, 
                          trip_distance_miles: float) -> List[Tuple[float, float]]:
        """
        
        Generate a realistic geospatial trip path
        
        Determines how many measurements will be taken, based on distance traveled.

        # First need to determine milage of trip, then run an independent timer

        Will use this as measurement hertz, and run a timer.

        int(trip_distance_miles * 3)

        measurement_rate = points / time
        points = time * measurement_rate

        if I want to have a measurement rate of 1 measurement per .33 seconds then (3 measurements/sec)

        """

        num_points = int(trip_distance_miles * 3)  # ~3 points per mile originally trip_distance_miles=600


        # Starting lat, long
        route = [(start_lat, start_lon)]
        
        current_lat, current_lon = start_lat, start_lon
        bearing = random.uniform(0, 360)  # Initial direction
        
        for _ in range(num_points):
            # Add some randomness to simulate turns
            bearing += random.uniform(-10, 10)
            
            # Distance per segment (roughly)
            distance_per_point = trip_distance_miles / num_points
            
            # Convert to lat/lon change (approximate)
            lat_change = distance_per_point * 0.0145 * math.cos(math.radians(bearing))
            lon_change = distance_per_point * 0.0145 * math.sin(math.radians(bearing))
            
            current_lat += lat_change
            current_lon += lon_change
            route.append((current_lat, current_lon))
        
        return route
    
    def simulate_speed_profile(self, route_length: int, driver_type: str) -> List[float]:
        """
        Generate realistic speed profile for the trip
        params:
        driver_type: 'good' or 'bad'
        route_length: number of points in the route, one measurement per .3 seconds
        Returns a list of speeds in mph
        1. Start at 0 mph (idle)
        2. Gradually accelerate to cruising speed
        3. Introduce variability for traffic, stops, and driver behavior
        4. End at 0 mph (stop)
        5. Apply moving average to smooth out the speed profile

        """

        params = self.good_driver_params if driver_type == 'good' else self.bad_driver_params


        # Start trip at idle
        speeds = [0]

        # print(route_length)

        # Gradually accelerate to cruising speed within 5 seconds
        # for k in range(route_length//15):
        ramp_up_time = 20  # seconds to reach cruising speed X*.3
        for k in range(ramp_up_time):
            speeds.append(min(params['ave_speed'], speeds[-1] + random.uniform(1, 3)))

        


        for i in range(ramp_up_time, route_length-ramp_up_time):
            # Base speed with some variation
            # base_speed = random.uniform(15, params['ave_speed'])
            base_speed = random.uniform(params['ave_speed']*.85, params['ave_speed'])

            # Add speeding events
            if random.random() < params['speeding_probability']:
                base_speed = random.uniform(31, 45)  # Speeding over 30 mph


            # Add traffic patterns (slower at intersections)
            if i > route_length//4 and i<route_length//2:  # Simulate intersections/traffic lights
            #     # reduce speed by 20 to 50 percent
                # base_speed *= random.uniform(0.75, 1.0)
                base_speed = random.uniform(15, 20)
                

                # Simulate hard_events
                if i % 50 == 0 and random.random() < params['hard_event_probability']:  # Simulate intersections/traffic lights
                    base_speed *= .10  # Speeding over 30 mph
                
            
            speeds.append(max(0, base_speed))
        


        # Gradually decelerate to stop
        for k in range(ramp_up_time):
            speeds.append(max(0, speeds[-1] - random.uniform(1, 3)))

        

        # window = route_length//30
        window = 10
        speeds = moving_average(speeds, window)
        # print(len(speeds))

        return speeds
    
    def calculate_acceleration(self, speeds: List[float], time_delta: float = 1.0) -> List[float]:
        """Calculate acceleration from speed profile"""
        accelerations = [0]  # First point has zero acceleration
        
        for i in range(1, len(speeds)):
            # Convert mph to m/s and calculate acceleration
            v1_ms = speeds[i-1]
            v2_ms = speeds[i]
            
            accel_ms2 = self.MPH_TO_MS* (v2_ms - v1_ms) / time_delta
            accel_g = accel_ms2 / self.GRAVITY
            
            # Add some noise to make it more realistic
            # noise = random.uniform(-0.01, 0.01)
            # accel_g += noise
            
            accelerations.append(accel_g)

        
        return accelerations
    
    def add_hard_events(self, accelerations: List[float], speeds: List[float], driver_type: str) -> List[float]:
        """Add hard braking and acceleration events based on context"""
        params = self.good_driver_params if driver_type == 'good' else self.bad_driver_params
        modified_accelerations = accelerations.copy()
        
        for i in range(len(modified_accelerations)):
            if random.random() < params['hard_event_probability']:
                # Context-aware hard events
                current_speed = speeds[i] if i < len(speeds) else 0
                
                if random.random() < 0.6:  # 60% chance of hard braking
                    if current_speed > 20:  # Only hard brake at higher speeds
                        # Hard braking event (negative acceleration)
                        intensity = random.uniform(-0.45, -0.35)
                        if driver_type == 'bad':
                            intensity = random.uniform(-0.60, -0.40)  # More aggressive
                        modified_accelerations[i] = intensity
                else:
                    # Hard acceleration event
                    if current_speed < 35:  # Only hard accelerate when not already fast
                        intensity = random.uniform(0.35, 0.50)
                        if driver_type == 'bad':
                            intensity = random.uniform(0.40, 0.65)  # More aggressive
                        modified_accelerations[i] = intensity
        
        return modified_accelerations
    
    def generate_trip_data(self, driver_id: str, trip_id: str, driver_type: str,
                          trip_distance_miles: float = 5.0) -> List[TelematicsDataPoint]:
        """Generate complete trip data"""
        # Starting location (Lawndale, California area)
        start_lat = 33.8870 + random.uniform(-0.05, 0.05)
        start_lon = -118.3526 + random.uniform(-0.05, 0.05)
        
        # Generate route
        route = self.generate_trip_route(start_lat, start_lon, trip_distance_miles)
        
        # Generate speed profile
        speeds = self.simulate_speed_profile(len(route), driver_type)
        
        # Calculate accelerations
        accelerations = self.calculate_acceleration(speeds, time_delta=.3)
        
        # Add hard events, this is artificial, so comment out, want ACTUAL hard events
        # accelerations = self.add_hard_events(accelerations, speeds, driver_type)
        
        # Create data points
        trip_data = []
        start_time = datetime.now()

        for _ in range(20):
            route.insert(0, route[0])  # Extend route for idle at start
            route.append(route[-1])  # Extend route for idle at end

        timestamp = start_time
        for i, ((lat, lon), speed, accel) in enumerate(zip(route, speeds, accelerations)):
            timestamp += timedelta(seconds=.33)  # 2-second intervals
            
            data_point = TelematicsDataPoint(
                timestamp=timestamp.isoformat(),
                latitude=lat,
                longitude=lon,
                speed_mph=speed,
                acceleration_g=accel,
                driver_id=driver_id,
                trip_id=trip_id
            )
            
            trip_data.append(data_point)
        
        return trip_data

class TripAnalyzer:
    """Analyzes trip data for risk scoring metrics"""
    
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
        trip_duration_hours = len(trip_data) * 1 / 3600  # 2 seconds per point
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
            'trip_duration_minutes': round(len(trip_data) * 2 / 60, 1),
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

class TripVisualizer:
    """Creates visualizations for trip data"""
    
    def __init__(self):
        plt.style.use('default')
        
    def plot_trip_overview(self, trip_data: List[TelematicsDataPoint], analysis: Dict):
        """Create comprehensive trip visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Trip Analysis - {analysis['driver_id']} ({analysis['trip_id']})\n" +
                     f"Risk Score: {analysis['risk_score']:.1f} | " +
                     f"Distance: {analysis['trip_length_miles']} miles | " +
                     f"Duration: {analysis['trip_duration_minutes']} min", 
                     fontsize=14, fontweight='bold')
        
        # Extract data
        timestamps = [datetime.fromisoformat(point.timestamp) for point in trip_data]
        speeds = [point.speed_mph for point in trip_data]
        accelerations = [point.acceleration_g for point in trip_data]
        lats = [point.latitude for point in trip_data]
        lons = [point.longitude for point in trip_data]
        
        # Speed over time
        axes[0, 0].plot(timestamps, speeds, 'b-', alpha=0.7, linewidth=1.5)
        speeding_mask = [s > 30 for s in speeds]
        if any(speeding_mask):
            speeding_times = [t for t, mask in zip(timestamps, speeding_mask) if mask]
            speeding_speeds = [s for s, mask in zip(speeds, speeding_mask) if mask]
            axes[0, 0].scatter(speeding_times, speeding_speeds, color='red', s=20, alpha=0.8, label='Speeding Events')
        axes[0, 0].axhline(y=30, color='r', linestyle='--', alpha=0.7, label='Speed Limit (30 mph)')
        axes[0, 0].set_title('Speed Over Time', fontweight='bold')
        axes[0, 0].set_ylabel('Speed (mph)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Acceleration over time
        axes[0, 1].plot(timestamps, accelerations, 'g-', alpha=0.7, linewidth=1.5)
        # Highlight hard events
        hard_braking_mask = [a <= -0.35 for a in accelerations]
        hard_accel_mask = [a >= 0.35 for a in accelerations]
        
        if any(hard_braking_mask):
            braking_times = [t for t, mask in zip(timestamps, hard_braking_mask) if mask]
            braking_accels = [a for a, mask in zip(accelerations, hard_braking_mask) if mask]
            axes[0, 1].scatter(braking_times, braking_accels, color='red', s=30, alpha=0.8, label='Hard Braking')
            
        if any(hard_accel_mask):
            accel_times = [t for t, mask in zip(timestamps, hard_accel_mask) if mask]
            accel_accels = [a for a, mask in zip(accelerations, hard_accel_mask) if mask]
            axes[0, 1].scatter(accel_times, accel_accels, color='orange', s=30, alpha=0.8, label='Hard Acceleration')
        
        axes[0, 1].axhline(y=-0.35, color='r', linestyle='--', alpha=0.7, label='Hard Braking Threshold')
        axes[0, 1].axhline(y=0.35, color='orange', linestyle='--', alpha=0.7, label='Hard Accel Threshold')
        axes[0, 1].set_title('Acceleration Over Time', fontweight='bold')
        axes[0, 1].set_ylabel('Acceleration (g)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Route map
        axes[1, 0].plot(lons, lats, 'b-', alpha=0.6, linewidth=2)
        axes[1, 0].scatter(lons[0], lats[0], color='green', s=150, label='Start', zorder=5, marker='o', edgecolors='black')
        axes[1, 0].scatter(lons[-1], lats[-1], color='red', s=150, label='End', zorder=5, marker='s', edgecolors='black')
        axes[1, 0].set_title('Route Map', fontweight='bold')
        axes[1, 0].set_xlabel('Longitude')
        axes[1, 0].set_ylabel('Latitude')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Event summary and metrics
        events = ['Speeding\nEvents', 'Hard\nBraking', 'Hard\nAcceleration']
        counts = [analysis['speeding_events'], analysis['hard_braking_events'], 
                 analysis['hard_acceleration_events']]
        colors = ['#ff4444', '#ff8800', '#aa44ff']
        
        bars = axes[1, 1].bar(events, counts, color=colors, alpha=0.8, edgecolor='black')
        axes[1, 1].set_title('Risk Events Summary', fontweight='bold')
        axes[1, 1].set_ylabel('Event Count')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{count}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{analysis['driver_id']}_{analysis['trip_id']}.png")
        plt.show()

    
    def plot_driver_comparison(self, analyses: List[Dict]):
        """Compare multiple drivers' risk metrics"""
        if not analyses:
            return
        
        df = pd.DataFrame(analyses)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Multi-Driver Risk Analysis Comparison', fontsize=16, fontweight='bold')
        
        # Risk scores comparison
        sns.barplot(data=df, x='driver_id', y='risk_score', ax=axes[0, 0], palette='viridis')
        axes[0, 0].set_title('Risk Scores by Driver', fontweight='bold')
        axes[0, 0].set_ylabel('Risk Score (0-100)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Event comparison
        event_cols = ['speeding_events', 'hard_braking_events', 'hard_acceleration_events']
        df_events = df[['driver_id'] + event_cols].melt(
            id_vars='driver_id', 
            value_vars=event_cols,
            var_name='event_type', 
            value_name='count'
        )
        
        sns.barplot(data=df_events, x='driver_id', y='count', hue='event_type', 
                   ax=axes[0, 1], palette=['#ff4444', '#ff8800', '#aa44ff'])
        axes[0, 1].set_title('Risk Events by Driver', fontweight='bold')
        axes[0, 1].set_ylabel('Event Count')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        axes[0, 1].legend(title='Event Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Speed comparison
        sns.boxplot(data=df, x='driver_id', y='max_speed', ax=axes[1, 0], palette='coolwarm')
        axes[1, 0].axhline(y=30, color='r', linestyle='--', alpha=0.7, label='Speed Limit')
        axes[1, 0].set_title('Max Speed Distribution', fontweight='bold')
        axes[1, 0].set_ylabel('Max Speed (mph)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Risk score distribution
        axes[1, 1].hist(df['risk_score'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        axes[1, 1].axvline(df['risk_score'].mean(), color='red', linestyle='--', 
                          label=f'Average: {df["risk_score"].mean():.1f}')
        axes[1, 1].set_title('Risk Score Distribution', fontweight='bold')
        axes[1, 1].set_xlabel('Risk Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"all_driver_data.png")
        plt.show()

def export_trip_data(trip_data: List[TelematicsDataPoint], filename: str):
    """Export trip data to CSV file"""
    data_dict = []
    for point in trip_data:
        data_dict.append({
            'timestamp': point.timestamp,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'speed_mph': point.speed_mph,
            'acceleration_g': point.acceleration_g,
            'driver_id': point.driver_id,
            'trip_id': point.trip_id
        })
    
    df = pd.DataFrame(data_dict)
    df.to_csv(filename, index=False)
    logger.info(f"Trip data exported to {filename}")


def generate_trips(num_trips: int, distance:int, simulator, analyzer, all_analyses, all_trip_data):
    # Generate multiple good driver trips
    logger.info("Generating good driver trips...")
    for i in range(num_trips):
        trip_id = f"GOOD_TRIP_{i+1:03d}"
        driver_id = f"GOOD_DRIVER_{i+1:03d}"
        trip_data = simulator.generate_trip_data(driver_id, trip_id, "good", distance)
                                            #    random.uniform(10.0, 30.0))
        analysis = analyzer.analyze_trip(trip_data)
        all_analyses.append(analysis)
        all_trip_data.append((trip_data, analysis))
        
        # Export individual trip data
        export_trip_data(trip_data, f"data/{trip_id}_data.csv")
    
    # Generate multiple bad driver trips
    logger.info("Generating bad driver trips...")
    for i in range(num_trips):
        trip_id = f"BAD_TRIP_{i+1:03d}"
        driver_id = f"BAD_DRIVER_{i+1:03d}"
        trip_data = simulator.generate_trip_data(driver_id, trip_id, "bad", distance )
                                            #    random.uniform(10.0, 30.0))
        analysis = analyzer.analyze_trip(trip_data)
        all_analyses.append(analysis)
        all_trip_data.append((trip_data, analysis))
        
        # Export individual trip data
        export_trip_data(trip_data, f"data/{trip_id}_data.csv")

def main():
    """Main function to run the telematics simulation"""
    logger.info("Starting Simple Telematics Data Simulation System")
    
    # Initialize components
    simulator = TelematicsSimulator()
    analyzer = TripAnalyzer()
    visualizer = TripVisualizer()
    
    # Generate sample trips
    all_analyses = []
    all_trip_data = []
    

    num_trips = 31
    distance = 600 # Seconds so 10 minutes
    generate_trips(num_trips, distance, simulator, analyzer, all_analyses, all_trip_data)
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Export all analyses
    analyses_df = pd.DataFrame(all_analyses)
    analyses_df.to_csv('data/trip_analyses.csv', index=False)
    
    # Print summary analyses
    print("\n" + "="*70)
    print("TELEMATICS TRIP ANALYSIS RESULTS")
    print("="*70)
    
    for analysis in all_analyses:
        driver_type = "🟢 GOOD" if "GOOD" in analysis['driver_id'] else "🔴 BAD"
        print(f"\n{driver_type} | Trip: {analysis['trip_id']}")
        print(f"├─ Driver: {analysis['driver_id']}")
        print(f"├─ Risk Score: {analysis['risk_score']:.1f}/100")
        print(f"├─ Trip Distance: {analysis['trip_length_miles']} miles")
        print(f"├─ Duration: {analysis['trip_duration_minutes']} minutes")
        print(f"├─ Max Speed: {analysis['max_speed']:.1f} mph")
        print(f"├─ Speeding Events: {analysis['speeding_events']}")
        print(f"├─ Hard Braking Events: {analysis['hard_braking_events']}")
        print(f"└─ Hard Acceleration Events: {analysis['hard_acceleration_events']}")
    
    # Summary statistics
    good_scores = [a['risk_score'] for a in all_analyses if 'GOOD' in a['driver_id']]
    bad_scores = [a['risk_score'] for a in all_analyses if 'BAD' in a['driver_id']]
    
    print(f"\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Good Drivers - Average Risk Score: {np.mean(good_scores):.1f}")
    print(f"Bad Drivers - Average Risk Score: {np.mean(bad_scores):.1f}")
    print(f"Risk Score Difference: {np.mean(bad_scores) - np.mean(good_scores):.1f} points")
    
    # Create visualizations
    logger.info("Creating visualizations...")
    
    # Show individual trip details for first good and bad driver
    good_trip_data, good_analysis = next(td for td in all_trip_data if 'GOOD' in td[1]['driver_id'])
    bad_trip_data, bad_analysis = next(td for td in all_trip_data if 'BAD' in td[1]['driver_id'])
    
    visualizer.plot_trip_overview(good_trip_data, good_analysis)
    visualizer.plot_trip_overview(bad_trip_data, bad_analysis)
    visualizer.plot_driver_comparison(all_analyses)
    
    logger.info("Simulation completed successfully!")
    logger.info("Data files saved to 'data/' directory")

if __name__ == "__main__":
    main()