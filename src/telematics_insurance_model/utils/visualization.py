

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
