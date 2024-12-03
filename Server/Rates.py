# Static exchange rates for testing
static_rates = {
    "USD": {"EUR": 0.85, "GBP": 0.75, "JPY": 110.0},
    "EUR": {"USD": 1.18, "GBP": 0.88, "JPY": 129.53},
    "GBP": {"USD": 1.33, "EUR": 1.14, "JPY": 146.79},
    "JPY": {"USD": 0.0091, "EUR": 0.0077, "GBP": 0.0068}
}

def convert(initial, desired):
    if initial in static_rates and desired in static_rates[initial]:
        rate = static_rates[initial][desired]
        return rate
    else:
        print(f"Conversion rate not found for {initial} to {desired}.")
        return 1
