
import os
import logging
import pandas as pd
import numpy as np

# Imnport a singleton instance of logger
from telematics_insurance_model.helpers.logger import initialize_logger
logger = initialize_logger()


from telematics_insurance_model.helpers.processing import TripAnalyzer
from telematics_insurance_model.utils.visualization import TripVisualizer
from telematics_insurance_model.utils.simulate import TelematicsSimulator, generate_trips




def main():
    """Main function to run the telematics simulation"""
    logger.info("Starting Simple Telematics Data Simulation System")
    
    # Initialize components
    simulator = TelematicsSimulator()
    analyzer = TripAnalyzer()
    visualizer = TripVisualizer()
    
    # Where to store trips and trip analysis
    all_analyses = []
    all_trip_data = []
    
    os.makedirs('data/trip_records', exist_ok=True)

    # Number of good and bad drivers to simulate, choose 31 for a months worth of data 
    num_trips = 31

    # Seconds so 10 minutes
    time = 600 

    generate_trips(num_trips, time, simulator, analyzer, all_analyses, all_trip_data)
    

    
    # Export all analyses
    analyses_df = pd.DataFrame(all_analyses)
    analyses_df.to_csv('data/trip_records/trip_analyses.csv', index=False)
    
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
    logger.info("Data files saved to 'data/trip_records/' directory")

if __name__ == "__main__":
    main()