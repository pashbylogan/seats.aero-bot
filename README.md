# Seats.aero Flight Finder

A Python script to find the cheapest award flights using the seats.aero API. Search for one-way flights across multiple loyalty programs and calculate the value you're getting with cents per point (CPP).

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A seats.aero Pro subscription ($9.99/month)
- Your seats.aero API key (get it from https://seats.aero/apikey)

## Installation

1. Clone or download this repository

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

3. Copy the example configuration and add your API key:
```bash
cp config.example.yaml config.yaml
```

4. Edit `config.yaml` with your API key and search preferences

## Configuration

Edit `config.yaml` to customize your search:

### Required Settings

- **api_key**: Your seats.aero API key
- **origin**: Departure airport (e.g., "SFO" or "JFK,EWR,LGA" for multiple)
- **destination**: Arrival airport (e.g., "NRT" or "NRT,HND" for multiple)
- **cabin**: Cabin class ("economy", "business", or "first")
- **start_date**: Start of date range (YYYY-MM-DD)
- **end_date**: End of date range (YYYY-MM-DD)

### Optional Settings

- **max_results**: Number of results to display (default: 10)
- **credit_card**: Automatically search all transfer partners for your card
- **sources**: Manually filter by specific mileage programs (leave empty for all)
- **baseline_cash_price**: Cash price in USD for CPP calculation
- **min_cpp**: Minimum cents per point threshold
- **sort_by**: Sort results by "miles", "cpp", or "date"
- **show_segments**: Show detailed flight segments
- **nonstop_only**: Show only nonstop flights

### Credit Card Integration (New!)

Instead of manually specifying loyalty programs, simply specify your credit card and the script will automatically search all its transfer partners:

**Supported Credit Cards:**
- `capital-one` - Capital One Venture, VentureX, Spark Miles (18 airline partners)
- `chase` - Chase Sapphire, Freedom, Ink (9+ airline partners)
- `amex` - American Express Membership Rewards (14+ airline partners)
- `citi` - Citi Premier, Prestige, Rewards+ (10+ airline partners)
- `bilt` - Bilt Rewards (10 airline partners)

**Example config:**
```yaml
search:
  credit_card: "capital-one"
```

This automatically searches:
- Air Canada Aeroplan
- Air France-KLM Flying Blue
- British Airways Executive Club
- Cathay Pacific Asia Miles
- Emirates Skywards
- Etihad Guest
- Finnair Plus
- Qantas Frequent Flyer
- Qatar Airways Privilege Club
- Singapore KrisFlyer
- Turkish Airlines Miles & Smiles
- And more!

### Manual Program Selection

You can also manually filter by specific loyalty programs if you prefer:

```yaml
search:
  sources:
    - aeroplan
    - flying-blue
    - krisflyer
```

**Available Program Codes:**
- `aa` - American Airlines AAdvantage
- `aeroplan` - Air Canada Aeroplan
- `alaska` - Alaska Airlines Mileage Plan
- `delta` - Delta SkyMiles
- `etihad` - Etihad Guest
- `flying-blue` - Air France-KLM Flying Blue
- `krisflyer` - Singapore Airlines KrisFlyer
- `qantas` - Qantas Frequent Flyer
- `turkish` - Turkish Airlines Miles & Smiles
- `united` - United MileagePlus
- `virgin-atlantic` - Virgin Atlantic Flying Club
- And many more...

## Usage

Run the script with default configuration:
```bash
uv run python flight_finder.py
```

Or if installed with pip:
```bash
python flight_finder.py
```

Specify a custom configuration file:
```bash
uv run python flight_finder.py -c my_search.yaml
```

## Understanding Cents Per Point (CPP)

CPP measures the value you get from your points:

```
CPP = (Cash Price - Taxes) / Miles × 100
```

**Example:**
- Flight costs $500 cash or 25,000 miles + $50 taxes
- CPP = ($500 - $50) / 25,000 × 100 = 1.8 cents per point

**General Guidelines:**
- 1+ CPP: Decent value
- 1.5+ CPP: Good value
- 2+ CPP: Excellent value
- Economy flights: aim for 1-1.5 CPP
- Business/First class: aim for 2+ CPP

### How to Find Cash Prices

Currently, you need to manually check cash prices and set `baseline_cash_price` in your config. Recommended tools:

- **Google Flights**: https://www.google.com/travel/flights - Best for quick price checks
- **Kayak**: https://www.kayak.com/flights - Good for price comparisons
- **ITA Matrix**: https://matrix.itasoftware.com/ - Detailed fare analysis

> **Note**: Automatic price fetching requires flight price APIs which typically need partner approval or paid subscriptions. If you have access to a flight price API, you could integrate it to automate CPP calculation.

## Example Output

```
Searching for flights...
  Route: SFO → LAX
  Dates: 2025-12-01 to 2025-12-15
  Cabin: economy

Found 45 flights. Showing top 10:

+-----+-----------------+----------------------+----------------------+-----------+-----------+----------+----------+---------+-----------+
|   # | Program         | Departure            | Arrival              | Duration  | Stops     | Miles    | Taxes    | Seats   | Flights   |
+=====+=================+======================+======================+===========+===========+==========+==========+=========+===========+
|   1 | alaska          | 2025-12-01 08:00     | 2025-12-01 10:15     | 2h 15m    | Nonstop   | 5,000    | $5.60    | 9+      | AS123     |
+-----+-----------------+----------------------+----------------------+-----------+-----------+----------+----------+---------+-----------+
|   2 | united          | 2025-12-01 10:30     | 2025-12-01 12:45     | 2h 15m    | Nonstop   | 6,500    | $5.60    | 4       | UA456     |
+-----+-----------------+----------------------+----------------------+-----------+-----------+----------+----------+---------+-----------+
```

## Tips

1. **Use date flexibility**: Set a wider date range to find better deals
2. **Try multiple airports**: Use comma-separated codes for origin/destination
3. **Filter by programs**: Only search programs where you have points
4. **Sort by CPP**: If you know cash prices, sort by value instead of just miles
5. **Check segments**: Enable segment details to understand routing

## API Limits

- Pro subscribers get 1,000 API calls per day
- Each search counts as one API call
- Searches are cached by seats.aero for faster results

## Troubleshooting

**Authentication Error:**
- Verify your API key is correct
- Make sure you have an active Pro subscription

**No Results Found:**
- Try a wider date range
- Try different cabin classes
- Remove source filters to search all programs
- Some routes may have limited award availability

**Connection Errors:**
- Check your internet connection
- seats.aero may be experiencing downtime

## License

This project is provided as-is for personal use. The seats.aero API is subject to their terms of service. Commercial use requires written agreement with seats.aero.

## Disclaimer

This tool is not affiliated with seats.aero. You must comply with seats.aero's API terms of service when using this script.
