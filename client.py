# -*- coding: utf-8 -*-
"""
GenPark Ctrip Flight Fare Volatility Forecaster Client
Predicts airline dynamic ticket fare fluctuations and outputs optimal Buy-Now vs Wait-and-Freeze recommendations.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class GenParkCtripFlightFareVolatilityForecaster:
    """
    Evaluates airline revenue management pricing curves (EMSRb) based on
    Days-to-Departure (DTD), historical cabin load factors, and seasonal demand.
    """

    def __init__(self, inflection_dtd_days: float = 14.0):
        self.inflection_dtd = inflection_dtd_days

    def calculate_pricing_hazard(self, days_to_departure: int, load_factor: float, is_holiday: bool) -> float:
        """
        Calculates projected percentage price change over next 7 days.
        Returns positive for expected surge, negative for expected drop.
        """
        # When departure is far (> 28 days) and load factor is low (< 0.50), airlines may discount
        if days_to_departure > 28 and load_factor < 0.45 and not is_holiday:
            return -0.08

        # When DTD <= 14, exponential pricing surge
        urgency_factor = math.exp(-max(0, days_to_departure - 2) / self.inflection_dtd)
        load_pressure = (load_factor ** 2.2) * 0.45
        holiday_premium = 0.35 if is_holiday else 0.0

        surge = (urgency_factor * 0.40) + load_pressure + holiday_premium
        return round(surge, 4)

    def calculate_sellout_risk(self, days_to_departure: int, load_factor: float) -> float:
        """Sigmoid sellout probability index (0.0 to 1.0)."""
        x = (load_factor * 10.0) - (days_to_departure / 4.0)
        prob = 1.0 / (1.0 + math.exp(-0.75 * (x - 3.0)))
        return round(max(0.02, min(0.98, prob)), 3)

    def forecast_fare_volatility(
        self,
        route_origin: str,
        route_destination: str,
        current_fare_cny: float,
        days_to_departure: int,
        current_cabin_load_factor: float = 0.65,
        is_peak_holiday_travel: bool = False
    ) -> Dict[str, Any]:
        """
        Forecasts 7-day fare trajectory and determines booking action.
        """
        hazard_rate = self.calculate_pricing_hazard(days_to_departure, current_cabin_load_factor, is_peak_holiday_travel)
        sellout_risk = self.calculate_sellout_risk(days_to_departure, current_cabin_load_factor)

        projected_fare = round(current_fare_cny * (1.0 + hazard_rate), 2)
        fare_delta_cny = round(projected_fare - current_fare_cny, 2)

        # Decision thresholding
        if days_to_departure <= 7 or sellout_risk >= 0.70 or hazard_rate >= 0.15:
            recommendation = "BUY_NOW_PRICE_LOCKED"
            rationale = "Imminent departure and tight cabin capacity indicate high surge and sellout probability."
            volatility_tier = "CRITICAL_SURGE"
        elif hazard_rate <= -0.04 and sellout_risk < 0.35:
            recommendation = "WAIT_AND_SET_PRICE_FREEZE"
            rationale = "Cabin load is low with over 4 weeks to departure; dynamic price drop expected."
            volatility_tier = "COOLING_OFF"
        else:
            recommendation = "MONITOR_STABLE_WINDOW"
            rationale = "Pricing is currently range-bound. Set Ctrip Smart Price Alert."
            volatility_tier = "MODERATE_STABLE"

        return {
            "route": f"{route_origin.upper()} -> {route_destination.upper()}",
            "current_fare_cny": current_fare_cny,
            "days_to_departure": days_to_departure,
            "projected_fare_cny_7d": projected_fare,
            "expected_price_change_cny": fare_delta_cny,
            "projected_change_rate_pct": round(hazard_rate * 100.0, 1),
            "cabin_sellout_risk_pct": round(sellout_risk * 100.0, 1),
            "recommendation_verdict": recommendation,
            "volatility_tier": volatility_tier,
            "decision_rationale": rationale,
            "recommended_protection": "CTRIP_PRICE_FREEZE_GUARANTEE" if recommendation == "WAIT_AND_SET_PRICE_FREEZE" else "INSTANT_TICKET_ISSUANCE"
        }
