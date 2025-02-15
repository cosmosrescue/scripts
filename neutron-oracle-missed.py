import requests
import re

# this script will grab oracle metrics from neutron node

validator = "neutronvalcons1.." #replace

def fetch_metrics_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_tickers_with_numbers_for_validator(data, validator):
    pattern = re.compile(r'status="(missing_price|absent)".*?ticker="([^"]+)".*?validator="([^"]+)".*?(\d+)$', re.MULTILINE)
    matches = pattern.findall(data)
    
    missed = {}
    absent = {}
    
    for status, ticker, val, number in matches:
        if val == validator:
            if status == 'missing_price':
                if ticker in missed:
                    missed[ticker].append(int(number))  
                else:
                    missed[ticker] = [int(number)]
            elif status == 'absent':
                if ticker in absent:
                    absent[ticker].append(int(number))  
                else:
                    absent[ticker] = [int(number)]
    
    def sort_tickers(ticker_dict):
        return dict(sorted(ticker_dict.items(), key=lambda x: max(x[1]), reverse=True))
    
    missed = sort_tickers(missed)
    absent = sort_tickers(absent)

    def format_tickers(dict_of_tickers):
        formatted_tickers = []
        for ticker, numbers in dict_of_tickers.items():
            numbers_str = ', '.join(map(str, sorted(numbers, reverse=True)))
            formatted_tickers.append(f"{ticker} ({numbers_str})")
        return formatted_tickers

    return format_tickers(missed), format_tickers(absent)

metrics_url = "http://localhost:26660/metrics"

metrics_data = fetch_metrics_data(metrics_url)

if metrics_data:
    missed_tickers, absent_tickers = get_tickers_with_numbers_for_validator(metrics_data, validator)
    print(f"Missed tickers for {validator}: {missed_tickers}")
    print(f"Absent tickers for {validator}: {absent_tickers}")
else:
    print("Failed to fetch metrics data.")
