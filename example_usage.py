# -*- coding: utf-8 -*-
"""
Example usage of GenParkCtripFlightFareVolatilityForecaster
Demonstrates dynamic fare forecasting across differing lead times.
"""

from client import GenParkCtripFlightFareVolatilityForecaster

def main():
    forecaster = GenParkCtripFlightFareVolatilityForecaster()

    cases = [
        {
            "name": "Case A: Shanghai to Tokyo 5 Days Out (High Load & Holiday)",
            "origin": "SHA", "dest": "TYO", "fare": 3200.0, "dtd": 5, "load": 0.88, "holiday": True
        },
        {
            "name": "Case B: Beijing to Bangkok 45 Days Out (Low Off-Season Load)",
            "origin": "PEK", "dest": "BKK", "fare": 2100.0, "dtd": 45, "load": 0.38, "holiday": False
        }
    ]

    print("================================================================")
    print("GenPark Ctrip Flight Fare Volatility Forecaster - Live Runs")
    print("================================================================\n")

    for c in cases:
        res = forecaster.forecast_fare_volatility(
            route_origin=c["origin"],
            route_destination=c["dest"],
            current_fare_cny=c["fare"],
            days_to_departure=c["dtd"],
            current_cabin_load_factor=c["load"],
            is_peak_holiday_travel=c["holiday"]
        )
        print(f"[{c['name']}]")
        print(f"  Route                 : {res['route']}")
        print(f"  Current Fare          : CNY {res['current_fare_cny']:,.2f}")
        print(f"  Projected Fare (7d)   : CNY {res['projected_fare_cny_7d']:,.2f} ({res['expected_price_change_cny']:+,.2f})")
        print(f"  Cabin Sellout Risk    : {res['cabin_sellout_risk_pct']}%")
        print(f"  Recommendation        : {res['recommendation_verdict']} [{res['volatility_tier']}]")
        print(f"  Decision Rationale    : {res['decision_rationale']}\n")

if __name__ == "__main__":
    main()
