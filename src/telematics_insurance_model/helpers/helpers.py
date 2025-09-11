

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
