
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

# Supress warning messages for hue in seaborn visualizations
import warnings
warnings.filterwarnings("ignore")


def main():
    """
    A script that will simulate the telematics data for good and bad drivers,
    analyze the trips for risk metrics, and create visualizations.
    The results will be logged and saved to CSV files.

    The simulation models good and bad driver behaviour in non-highway conditions.
    travelling down streets with a speed limit of 30mph.

    The situation simulated is a driver travelling for 10 minutes, that encounters a slow
    down about a quarter way through the trip forcing a slowdown. Data points are
    recorded every 1/3 second (3Hz). Good drivers will generally obey speed limits
    and avoid hard braking/acceleration events, while bad drivers will exhibit
    more risky behaviour (hard breaks and accelerations).

    Figures of the trip data and summary statistics are saved to the 'figures' directory.
    Trip data and analyses are saved to the 'data/trip_records' directory.
    

    """


    logger.info("Starting Simple Telematics Data Simulation System")
    print("\nStarting Simple Telematics Data Simulation System")

    # Initialize components
    simulator = TelematicsSimulator()
    analyzer = TripAnalyzer()
    visualizer = TripVisualizer()
    
    # Where to store trips and trip analysis
    all_analyses = []
    all_trip_data = []
    
    # Ensure that data and figures directory exist
    os.makedirs('data/trip_records', exist_ok=True)
    os.makedirs('figures', exist_ok=True)

    # Number of good and bad drivers to simulate, choose 31 for a months worth of data 
    num_trips = 365

    # Seconds so 10 minutes
    time = 600 

    logger.info(f"Simulating {num_trips} trips of {time/60:.1f} minutes each...")
    print(f"Simulating {num_trips} trips of {time/60:.1f} minutes each...\n")

    generate_trips(num_trips, time, simulator, analyzer, all_analyses, all_trip_data)
    

    
    # Export all analyses
    analyses_df = pd.DataFrame(all_analyses)
    analyses_df.to_csv('data/trip_records/trip_analyses.csv', index=False)

    logger.info("Trip analyses saved to 'data/trip_records/trip_analyses.csv'")
    print("Trip analyses saved to 'data/trip_records/trip_analyses.csv'\n")
    
    # Print summary analyses
    logger.info("\n" + "="*70)
    logger.info("TELEMATICS TRIP ANALYSIS RESULTS")
    logger.info("="*70)
    
    for analysis in all_analyses:
        driver_type = "🟢 GOOD" if "GOOD" in analysis['driver_id'] else "🔴 BAD"
        logger.info(f"\n{driver_type} | Trip: {analysis['trip_id']}")
        logger.info(f"├─ Driver: {analysis['driver_id']}")
        logger.info(f"├─ Risk Score: {analysis['risk_score']:.1f}/100")
        logger.info(f"├─ Duration: {analysis['trip_duration_minutes']} minutes")
        logger.info(f"├─ Max Speed: {analysis['max_speed']:.1f} mph")
        logger.info(f"├─ Hard Braking Events: {analysis['hard_brakes']}")
        logger.info(f"└─ Hard Acceleration Events: {analysis['hard_accel']}")
        logger.info(f"├─ Speeding Events: {analysis['speeding_events']}")
        logger.info(f"├─ Trip Distance: {analysis['trip_len']} miles")
    
    # Summary statistics
    good_scores = [a['risk_score'] for a in all_analyses if 'GOOD' in a['driver_id']]
    bad_scores = [a['risk_score'] for a in all_analyses if 'BAD' in a['driver_id']]
    
    logger.info(f"\n" + "="*70)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*70)
    logger.info(f"Good Drivers - Average Risk Score: {np.mean(good_scores):.1f}")
    logger.info(f"Bad Drivers - Average Risk Score: {np.mean(bad_scores):.1f}")
    logger.info(f"Risk Score Difference: {np.mean(bad_scores) - np.mean(good_scores):.1f} points")
    
    # Create visualizations
    logger.info("Creating visualizations...")
    print("Creating visualizations...")
    
    # Show individual trip details for first good and bad driver
    good_trip_data, good_analysis = next(td for td in all_trip_data if 'GOOD' in td[1]['driver_id'])
    bad_trip_data, bad_analysis = next(td for td in all_trip_data if 'BAD' in td[1]['driver_id'])
    
    visualizer.plot_trip_overview(good_trip_data, good_analysis)
    visualizer.plot_trip_overview(bad_trip_data, bad_analysis)
    visualizer.plot_driver_comparison(all_analyses)
    
    logger.info("Simulation completed successfully!")
    logger.info("Data files saved to 'data/trip_records/' directory")
    logger.info("Figures saved to 'figures/' directory")

    print("Simulation completed successfully!")
    print("Data files saved to 'data/trip_records/' directory")
    print("Figures saved to 'figures/' directory\n\n")

    logger.info(f"Simulated Telematics data for all {num_trips} trips stored in 'data/trip_records/trip_analyses.csv'")
    print(f"Simulated Telematics data for all {num_trips} trips stored in 'data/trip_records/trip_analyses.csv'")


if __name__ == "__main__":
    main()