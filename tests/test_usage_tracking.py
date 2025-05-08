"""Test Usage Tracking and Cost Optimization"""
from src.usage_tracker import UsageTracker
from datetime import datetime, timedelta

def main():
    tracker = UsageTracker()
    
    print("\nSimulating API Usage and Cost Tracking")
    print("=====================================")
    
    # Simulate some API calls
    test_cases = [
        ("property_details", "123 Main St", True),
        ("avm", "123 Main St", True),
        ("market_trends", "90210", True),
        ("property_details", "456 Oak Ave", False),  # Simulated failed call
        ("owner_info", "123 Main St", True)
    ]
    
    print("\n1. Tracking API Calls...")
    for solution, address, success in test_cases:
        tracker.track_api_call(solution, address, success)
        print(f"Tracked {solution} call for {address} - Success: {success}")
    
    # Simulate data usage from cache
    print("\n2. Tracking Data Usage...")
    tracker.track_data_usage("property_details", ["market_value", "beds", "baths"])
    tracker.track_data_usage("market_trends", ["median_price", "price_trend"])
    
    # Generate cost analysis
    print("\n3. Cost Analysis Report")
    print("--------------------")
    costs = tracker.analyze_costs()
    for solution_cost in costs:
        print(f"\nSolution: {solution_cost['solution']}")
        print(f"Total Cost: ${solution_cost['cost']:.2f}")
        print(f"Success Rate: {solution_cost['success_rate']*100:.1f}%")
        print(f"Cost per Successful Call: ${solution_cost['cost_per_success']:.2f}")
    
    # Calculate ROI metrics
    print("\n4. ROI Metrics")
    print("------------")
    roi = tracker.calculate_roi_metrics()
    print(f"Total API Calls: {roi.get('total_api_calls', 0)}")
    print(f"Cache Hits: {roi.get('total_cache_hits', 0)}")
    print(f"Cache Hit Ratio: {roi.get('cache_hit_ratio', 0)*100:.1f}%")
    print(f"Estimated Savings: ${roi.get('estimated_savings', 0):.2f}")
    
    # Get optimization recommendations
    print("\n5. Usage Recommendations")
    print("---------------------")
    recommendations = tracker.get_usage_recommendations()
    
    if recommendations['high_cost_solutions']:
        print("\nHigh Cost Solutions to Optimize:")
        for solution in recommendations['high_cost_solutions']:
            print(f"• {solution['solution']}: ${solution['current_cost']:.2f}")
            print(f"  Suggestion: {solution['suggestion']}")
    
    if recommendations['optimization_tips']:
        print("\nOptimization Tips:")
        for tip in recommendations['optimization_tips']:
            print(f"• {tip['solution'] if 'solution' in tip else tip['area']}")
            print(f"  Issue: {tip['issue']}")
            print(f"  Suggestion: {tip['suggestion']}")
    
    # Generate detailed cost report
    print("\n6. Monthly Cost Report")
    print("-------------------")
    start_date = datetime.now() - timedelta(days=30)
    report = tracker.generate_cost_report(start_date)
    
    print(f"\nDate Range: {report['date_range']['start']} to {report['date_range']['end']}")
    print(f"Total Cost: ${report['total_cost']:.2f}")
    print(f"Daily Average Cost: ${report['daily_average_cost']:.2f}")
    print(f"Total API Calls: {report['total_calls']}")

if __name__ == "__main__":
    main()
