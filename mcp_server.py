# -*- coding: utf-8 -*-
"""
GenPark Ctrip Flight Fare Volatility Forecaster MCP Server
Exposes airline fare volatility and Buy-or-Wait decision tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkCtripFlightFareVolatilityForecaster

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-ctrip-flight-fare-volatility-forecaster", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "forecast_fare_volatility",
                        "description": "Predicts airline dynamic ticket fare fluctuations and outputs optimal Buy-Now vs Wait-and-Freeze recommendations.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "route_origin": {"type": "string", "description": "Origin IATA or city (e.g. SHA)"},
                                "route_destination": {"type": "string", "description": "Destination IATA or city (e.g. TYO)"},
                                "current_fare_cny": {"type": "number", "description": "Current listed ticket fare in CNY"},
                                "days_to_departure": {"type": "integer", "description": "Days remaining until flight departure"},
                                "current_cabin_load_factor": {"type": "number", "description": "Estimated cabin occupancy ratio (0.0 - 1.0)"},
                                "is_peak_holiday_travel": {"type": "boolean", "description": "True if travel occurs during holiday peak"}
                            },
                            "required": ["route_origin", "route_destination", "current_fare_cny", "days_to_departure"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "forecast_fare_volatility":
            forecaster = GenParkCtripFlightFareVolatilityForecaster()
            res = forecaster.forecast_fare_volatility(
                route_origin=args.get("route_origin", "SHA"),
                route_destination=args.get("route_destination", "BKK"),
                current_fare_cny=args.get("current_fare_cny", 1850.0),
                days_to_departure=args.get("days_to_departure", 10),
                current_cabin_load_factor=args.get("current_cabin_load_factor", 0.72),
                is_peak_holiday_travel=args.get("is_peak_holiday_travel", False)
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        f = GenParkCtripFlightFareVolatilityForecaster()
        test_res = f.forecast_fare_volatility("PVG", "HND", 2600.0, 5, 0.85, True)
        print(f"Test Rec: {test_res['recommendation_verdict']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
