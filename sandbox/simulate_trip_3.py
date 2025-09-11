#!/usr/bin/env python3
"""
Telematics Data Simulation System
Generates realistic driving data with good/bad behaviors and processes through Kafka
"""

import json
import time
import random
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import List, Tuple, Dict
import threading
import logging

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
            'avg_acceleration': 0.15,  # g
            'max_acceleration': 0.25,  # g
            'speeding_probability': 0.02,
            'hard_event_probability': 0.01
        }
        
        self.bad_driver_params = {
            'max_speed': 45,  # mph
            'avg_acceleration': 0.25,  # g
            'max_acceleration': 0.50,  # g
            'speeding_probability': 0.15,
            'hard_event_probability': 0.08
        }
    
    def generate_trip_route(self, start_lat: float, start_lon: float, 
                          trip_distance_miles: float) -> List[Tuple[float, float]]:
        """Generate a realistic trip route"""
        num_points = int(trip_distance_miles * 10)  # ~10 points per mile
        route = [(start_lat, start_lon)]
        
        current_lat, current_lon = start_lat, start_lon
        bearing = random.uniform(0, 360)  # Initial direction
        
        for _ in range(num_points):
            # Add some randomness to simulate turns
            bearing += random.uniform(-15, 15)
            
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
        """Generate realistic speed profile for the trip"""
        params = self.good_driver_params if driver_type == 'good' else self.bad_driver_params
        speeds = []
        
        for i in range(route_length):
            # Base speed with some variation
            base_speed = random.uniform(15, params['max_speed'])
            
            # Add traffic patterns (slower at intersections, faster on straights)
            if i % 20 == 0:  # Simulate intersections
                base_speed *= 0.3
            
            # Add speeding events
            if random.random() < params['speeding_probability']:
                base_speed = random.uniform(31, 45)  # Speeding over 30 mph
            
            speeds.append(max(0, base_speed))
        
        return speeds
    
    def calculate_acceleration(self, speeds: List[float], time_delta: float = 1.0) -> List[float]:
        """Calculate acceleration from speed profile"""
        accelerations = [0]  # First point has zero acceleration
        
        for i in range(1, len(speeds)):
            # Convert mph to m/s and calculate acceleration
            v1_ms = speeds[i-1] * self.MPH_TO_MS
            v2_ms = speeds[i] * self.MPH_TO_MS
            
            accel_ms2 = (v2_ms - v1_ms) / time_delta
            accel_g = accel_ms2 / self.GRAVITY
            
            accelerations.append(accel_g)
        
        return accelerations
    
    def add_hard_events(self, accelerations: List[float], driver_type: str) -> List[float]:
        """Add hard braking and acceleration events"""
        params = self.good_driver_params if driver_type == 'good' else self.bad_driver_params
        modified_accelerations = accelerations.copy()
        
        for i in range(len(modified_accelerations)):
            if random.random() < params['hard_event_probability']:
                if random.random() < 0.5:
                    # Hard braking event (negative acceleration)
                    modified_accelerations[i] = random.uniform(-0.45, -0.35)
                else:
                    # Hard acceleration event
                    modified_accelerations[i] = random.uniform(0.35, 0.50)
        
        return modified_accelerations
    
    def generate_trip_data(self, driver_id: str, trip_id: str, driver_type: str,
                          trip_distance_miles: float = 5.0) -> List[TelematicsDataPoint]:
        """Generate complete trip data"""
        # Starting location (somewhere in California)
        start_lat = 34.0522 + random.uniform(-0.1, 0.1)
        start_lon = -118.2437 + random.uniform(-0.1, 0.1)
        
        # Generate route
        route = self.generate_trip_route(start_lat, start_lon, trip_distance_miles)
        
        # Generate speed profile
        speeds = self.simulate_speed_profile(len(route), driver_type)
        
        # Calculate accelerations
        accelerations = self.calculate_acceleration(speeds)
        
        # Add hard events
        accelerations = self.add_hard_events(accelerations, driver_type)
        
        # Create data points
        trip_data = []
        start_time = datetime.now()
        
        for i, ((lat, lon), speed, accel) in enumerate(zip(route, speeds, accelerations)):
            timestamp = start_time + timedelta(seconds=i)
            
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

class KafkaProcessor:
    """Handles Kafka operations for telematics data"""
    
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = 'telematics-data'
        self.producer = None
        self.consumer = None
        self.kafka_type = None
        
    def create_producer(self):
        """Create Kafka producer"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka not available. Running in simulation mode.")
            return
            
        try:
            # Try confluent-kafka first
            from confluent_kafka import Producer
            conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'client.id': 'telematics-producer'
            }
            self.producer = Producer(conf)
            self.kafka_type = 'confluent'
            logger.info("Confluent Kafka producer created successfully")
        except ImportError:
            try:
                # Fall back to kafka-python
                from kafka import KafkaProducer
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.bootstrap_servers],
                    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                    key_serializer=lambda x: x.encode('utf-8') if x else None
                )
                self.kafka_type = 'kafka-python'
                logger.info("Kafka-python producer created successfully")
            except Exception as e:
                logger.warning(f"Kafka producer not available: {e}. Running in simulation mode.")
                self.producer = None
    
    def create_consumer(self, group_id='telematics-consumer'):
        """Create Kafka consumer"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka not available. Running in simulation mode.")
            return
            
        try:
            # Try confluent-kafka first
            from confluent_kafka import Consumer
            conf = {
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group_id,
                'auto.offset.reset': 'earliest'
            }
            self.consumer = Consumer(conf)
            self.consumer.subscribe([self.topic_name])
            self.kafka_type = 'confluent'
            logger.info("Confluent Kafka consumer created successfully")
        except ImportError:
            try:
                # Fall back to kafka-python
                from kafka import KafkaConsumer
                self.consumer = KafkaConsumer(
                    self.topic_name,
                    bootstrap_servers=[self.bootstrap_servers],
                    group_id=group_id,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    auto_offset_reset='earliest'
                )
                self.kafka_type = 'kafka-python'
                logger.info("Kafka-python consumer created successfully")
            except Exception as e:
                logger.warning(f"Kafka consumer not available: {e}. Running in simulation mode.")
                self.consumer = None
    
    def send_data(self, data_point: TelematicsDataPoint):
        """Send data to Kafka topic"""
        if not self.producer:
            return False
            
        message = {
            'timestamp': data_point.timestamp,
            'latitude': data_point.latitude,
            'longitude': data_point.longitude,
            'speed_mph': data_point.speed_mph,
            'acceleration_g': data_point.acceleration_g,
            'driver_id': data_point.driver_id,
            'trip_id': data_point.trip_id
        }
        
        try:
            if self.kafka_type == 'confluent':
                key = f"{data_point.driver_id}_{data_point.trip_id}"
                self.producer.produce(
                    self.topic_name,
                    key=key,
                    value=json.dumps(message)
                )
                self.producer.flush()
            else:  # kafka-python
                self.producer.send(
                    self.topic_name,
                    key=f"{data_point.driver_id}_{data_point.trip_id}",
                    value=message
                )
            return True
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {e}")
            return False
    
    def consume_data(self, timeout_ms=1000):
        """Consume data from Kafka topic"""
        if not self.consumer:
            return []
            
        data_points = []
        
        try:
            if self.kafka_type == 'confluent':
                msgs = self.consumer.consume(num_messages=10, timeout=timeout_ms/1000)
                for msg in msgs:
                    if msg.error():
                        continue
                    data = json.loads(msg.value().decode('utf-8'))
                    data_points.append(data)
            else:  # kafka-python
                messages = self.consumer.poll(timeout_ms=timeout_ms)
                for topic_partition, records in messages.items():
                    for record in records:
                        data_points.append(record.value)
        except Exception as e:
            logger.error(f"Error consuming data from Kafka: {e}")
            
        return data_points

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
        
        # Calculate trip length (simplified - using number of points)
        trip_length_points = len(trip_data)
        
        # Speeding events
        speeding_events = sum(1 for speed in speeds if speed > self.speeding_threshold)
        
        # Hard braking events
        hard_braking_events = sum(1 for accel in accelerations 
                                if accel <= self.hard_braking_threshold)
        
        # Hard acceleration events
        hard_acceleration_events = sum(1 for accel in accelerations 
                                     if accel >= self.hard_acceleration_threshold)
        
        # Trip statistics
        analysis = {
            'trip_id': trip_data[0].trip_id,
            'driver_id': trip_data[0].driver_id,
            'trip_length_points': trip_length_points,
            'max_speed': max(speeds),
            'avg_speed': np.mean(speeds),
            'speeding_events': speeding_events,
            'hard_braking_events': hard_braking_events,
            'hard_acceleration_events': hard_acceleration_events,
            'max_acceleration': max(accelerations),
            'min_acceleration': min(accelerations),
            'risk_score': self.calculate_risk_score(
                speeding_events, hard_braking_events, hard_acceleration_events, trip_length_points
            )
        }
        
        return analysis
    
    def calculate_risk_score(self, speeding_events: int, hard_braking_events: int,
                           hard_acceleration_events: int, trip_length: int) -> float:
        """Calculate a simple risk score"""
        if trip_length == 0:
            return 0
        
        # Normalize by trip length
        speeding_rate = speeding_events / trip_length
        hard_braking_rate = hard_braking_events / trip_length
        hard_acceleration_rate = hard_acceleration_events / trip_length
        
        # Weighted risk score (0-100)
        risk_score = (
            speeding_rate * 40 +  # 40% weight for speeding
            hard_braking_rate * 30 +  # 30% weight for hard braking
            hard_acceleration_rate * 30  # 30% weight for hard acceleration
        ) * 100
        
        return min(100, risk_score)  # Cap at 100

class TripVisualizer:
    """Creates visualizations for trip data"""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        
    def plot_trip_overview(self, trip_data: List[TelematicsDataPoint], analysis: Dict):
        """Create comprehensive trip visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"Trip Analysis - {analysis['trip_id']}\nRisk Score: {analysis['risk_score']:.2f}", 
                     fontsize=16)
        
        # Extract data
        timestamps = [datetime.fromisoformat(point.timestamp) for point in trip_data]
        speeds = [point.speed_mph for point in trip_data]
        accelerations = [point.acceleration_g for point in trip_data]
        lats = [point.latitude for point in trip_data]
        lons = [point.longitude for point in trip_data]
        
        # Speed over time
        axes[0, 0].plot(timestamps, speeds, 'b-', alpha=0.7)
        axes[0, 0].axhline(y=30, color='r', linestyle='--', label='Speed Limit (30 mph)')
        axes[0, 0].set_title('Speed Over Time')
        axes[0, 0].set_ylabel('Speed (mph)')
        axes[0, 0].legend()
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Acceleration over time
        axes[0, 1].plot(timestamps, accelerations, 'g-', alpha=0.7)
        axes[0, 1].axhline(y=-0.35, color='r', linestyle='--', label='Hard Braking Threshold')
        axes[0, 1].axhline(y=0.35, color='r', linestyle='--', label='Hard Acceleration Threshold')
        axes[0, 1].set_title('Acceleration Over Time')
        axes[0, 1].set_ylabel('Acceleration (g)')
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Route map
        axes[1, 0].plot(lons, lats, 'b-', alpha=0.7)
        axes[1, 0].scatter(lons[0], lats[0], color='g', s=100, label='Start', zorder=5)
        axes[1, 0].scatter(lons[-1], lats[-1], color='r', s=100, label='End', zorder=5)
        axes[1, 0].set_title('Route Map')
        axes[1, 0].set_xlabel('Longitude')
        axes[1, 0].set_ylabel('Latitude')
        axes[1, 0].legend()
        
        # Event summary
        events = ['Speeding', 'Hard Braking', 'Hard Acceleration']
        counts = [analysis['speeding_events'], analysis['hard_braking_events'], 
                 analysis['hard_acceleration_events']]
        colors = ['red', 'orange', 'purple']
        
        axes[1, 1].bar(events, counts, color=colors)
        axes[1, 1].set_title('Risk Events Summary')
        axes[1, 1].set_ylabel('Event Count')
        
        plt.tight_layout()
        plt.show()
    
    def plot_driver_comparison(self, analyses: List[Dict]):
        """Compare multiple drivers' risk metrics"""
        if not analyses:
            return
        
        df = pd.DataFrame(analyses)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Driver Comparison Analysis', fontsize=16)
        
        # Risk scores
        sns.barplot(data=df, x='driver_id', y='risk_score', ax=axes[0, 0])
        axes[0, 0].set_title('Risk Scores by Driver')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Event comparison
        event_cols = ['speeding_events', 'hard_braking_events', 'hard_acceleration_events']
        df_events = df[['driver_id'] + event_cols].melt(id_vars='driver_id', 
                                                       value_vars=event_cols,
                                                       var_name='event_type', 
                                                       value_name='count')
        sns.barplot(data=df_events, x='driver_id', y='count', hue='event_type', ax=axes[0, 1])
        axes[0, 1].set_title('Risk Events by Driver')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Speed distribution
        sns.boxplot(data=df, x='driver_id', y='max_speed', ax=axes[1, 0])
        axes[1, 0].set_title('Max Speed Distribution')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Risk score distribution
        sns.histplot(data=df, x='risk_score', bins=10, ax=axes[1, 1])
        axes[1, 1].set_title('Risk Score Distribution')
        
        plt.tight_layout()
        plt.show()

def main():
    """Main function to run the telematics simulation"""
    logger.info("Starting Telematics Data Simulation System")
    
    # Initialize components
    simulator = TelematicsSimulator()
    kafka_processor = KafkaProcessor()
    analyzer = TripAnalyzer()
    visualizer = TripVisualizer()
    
    # Create Kafka producer
    kafka_processor.create_producer()
    
    # Generate sample trips
    all_analyses = []
    
    # Good driver trip
    logger.info("Generating good driver trip...")
    good_trip = simulator.generate_trip_data("DRIVER_001", "TRIP_001", "good", 3.0)
    good_analysis = analyzer.analyze_trip(good_trip)
    all_analyses.append(good_analysis)
    
    # Bad driver trip
    logger.info("Generating bad driver trip...")
    bad_trip = simulator.generate_trip_data("DRIVER_002", "TRIP_002", "bad", 3.0)
    bad_analysis = analyzer.analyze_trip(bad_trip)
    all_analyses.append(bad_analysis)
    
    # Send data to Kafka (if available)
    logger.info("Sending data to Kafka...")
    for trip_data in [good_trip, bad_trip]:
        for data_point in trip_data:
            kafka_processor.send_data(data_point)
    
    # Print analyses
    print("\n" + "="*50)
    print("TRIP ANALYSIS RESULTS")
    print("="*50)
    
    for analysis in all_analyses:
        print(f"\nTrip: {analysis['trip_id']}")
        print(f"Driver: {analysis['driver_id']}")
        print(f"Risk Score: {analysis['risk_score']:.2f}")
        print(f"Max Speed: {analysis['max_speed']:.1f} mph")
        print(f"Speeding Events: {analysis['speeding_events']}")
        print(f"Hard Braking Events: {analysis['hard_braking_events']}")
        print(f"Hard Acceleration Events: {analysis['hard_acceleration_events']}")
    
    # Create visualizations
    logger.info("Creating visualizations...")
    visualizer.plot_trip_overview(good_trip, good_analysis)
    visualizer.plot_trip_overview(bad_trip, bad_analysis)
    visualizer.plot_driver_comparison(all_analyses)
    
    logger.info("Simulation completed successfully!")

if __name__ == "__main__":
    main() p