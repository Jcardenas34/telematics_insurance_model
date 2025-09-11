import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import pandas as pd

from telematics_insurance_model.helpers.logger import logger


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
        export_trip_data(trip_data, f"data/trip_records/{trip_id}_data.csv")
    
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
        export_trip_data(trip_data, f"data/trip_records/{trip_id}_data.csv")




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



def moving_average(data, window_size):
    # Create a boxcar kernel (all ones) and normalize it
    kernel = np.ones(window_size) / window_size
    # Convolve the data with the kernel
    # 'same' mode ensures the output array has the same length as the input
    smoothed_data = np.convolve(data, kernel, mode='same')
    return smoothed_data


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
