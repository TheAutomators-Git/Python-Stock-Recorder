import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import re

def getData(ticker):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }  
    
    URL = f'https://finance.yahoo.com/quote/{ticker}'
    AAA = 'https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield'
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Initialize variables
    company_name = 'N/A'
    list_exchange = 'N/A'
    real_time_share_price = 'N/A'
    ytd_return = 'N/A'
    market_cap = 'N/A'
    profit_margin = 'N/A'
    ebitda = 'N/A'
    levered_free_cash_flow = 'N/A'
    fifty_two_week_high = 'N/A'
    fifty_two_week_low = 'N/A'
    pe_ratio = 'N/A'
    eps = 'N/A'
    dividend_payer_status = 'N/A'
    dividend_payer_status_percentage = 'N/A'
    real_time_annual_dividend = 'N/A'
    growth_estimate_last = 'N/A'
    growth_estimate_next = 'N/A'
    share_price_proximity_to_52w_low = 'N/A'
    real_time_dividend_yield = 'N/A'
    aaa_bond_value = 'N/A'
    
    # Safely find company_name
    company_section = soup.find('section', {'class': 'container yf-3a2v0c paddingRight'})
    if company_section:
        company_name_full = company_section.find_all('h1')[0].text
        ticker = company_name_full.split('(')[-1].split(')')[0]
        company_name = f"{company_name_full.split('(')[0].strip()} ({ticker})"
    
    # Safely find list_exchange
    exchange_div = soup.find('div', {'class': "top yf-ezk9pj"})
    if exchange_div:
        list_exchange_full = exchange_div.find_all('span')[0].text
        list_exchange = list_exchange_full.split(' - ')[0]
    
    # Safely find the real-time share price
    price_element = soup.find('fin-streamer', {'class': 'livePrice yf-mgkamr'})
    if price_element:
        real_time_share_price = price_element.text
    
    # Safely find the YTD Return (%)
    perf_info_div = soup.find('div', {'class': 'cards-4 perfInfo yf-12wncuy'})
    if perf_info_div:
        symbol_divs = perf_info_div.find_all('div', {'class': 'symbol yf-12wncuy'})
        perf_divs = perf_info_div.find_all('div', {'class': 'perf positive yf-12wncuy'}) + perf_info_div.find_all('div', {'class': 'perf negative yf-12wncuy'})
        
        for symbol_div, perf_div in zip(symbol_divs, perf_divs):
            if symbol_div.text == ticker:
                ytd_return_value = perf_div.text
                if 'positive' in perf_div['class']:
                    ytd_return = f"+{ytd_return_value}"
                elif 'negative' in perf_div['class']:
                    ytd_return = f"-{ytd_return_value}"
                break
    
    # Safely find the Market Cap (intraday)
    market_cap_element = soup.find('fin-streamer', {'data-field': 'marketCap'})
    if market_cap_element:
        market_cap = market_cap_element['data-value']
    
    # Locate the second section containing the profit margin and levered free cash flow
    sections = soup.find_all('section', {'class': 'card large yf-13ievhf bdr sticky'})
    if len(sections) > 1:
        financial_highlights_section = sections[1]
        
        # Safely find the Profit Margin
        profit_margin_label = financial_highlights_section.find('p', class_='label', string=lambda text: 'Profit Margin' in text if text else False)
        if profit_margin_label:
            profit_margin_value = profit_margin_label.find_next('p', class_='value yf-lc8fp0')
            if profit_margin_value:
                profit_margin = profit_margin_value.text
    
    # Replace the logic for Levered Free Cash Flow
    levered_free_cash_flow_label = soup.find('p', class_='label', string=lambda text: 'Levered Free Cash Flow' in text if text else False)
    if levered_free_cash_flow_label:
        levered_free_cash_flow = levered_free_cash_flow_label.find_next('p', class_='value').text
    
    # Locate the first section containing the EBITDA
    if sections:
        valuation_measures_section = sections[0]
        
        # Safely find the Enterprise Value/EBITDA
        ebitda_label = valuation_measures_section.find('p', class_='label', string=lambda text: 'Enterprise Value/EBITDA' in text if text else False)
        if ebitda_label:
            ebitda_value = ebitda_label.find_next('p', class_='value yf-1n4vnw8')
            if ebitda_value:
                ebitda = ebitda_value.text
    
    # Replace the logic for extracting the 52-week high and low values
    fifty_two_week_range = soup.find('fin-streamer', {'data-field': 'fiftyTwoWeekRange'})
    if fifty_two_week_range:
        range_values = fifty_two_week_range.text.split(' - ')
        fifty_two_week_low = float(range_values[0].strip())
        fifty_two_week_high = float(range_values[1].strip())
    
    # Add the logic to find the P/E ratio
    pe_ratio_element = soup.find('fin-streamer', {'data-field': 'trailingPE'})
    if pe_ratio_element:
        pe_ratio = pe_ratio_element.text.strip()

    # Query to extract the entire <div> with data-testid="quote-statistics"
    quote_statistics_div = soup.find('div', {'data-testid': 'quote-statistics'})
    if quote_statistics_div:
        li_elements = quote_statistics_div.find_all('li')
        if len(li_elements) > 11:
            spans = li_elements[11].find_all('span')
            if len(spans) > 1:
                eps = spans[1].text
    
    # Safely find dividend_payer_status
    if quote_statistics_div:
        li_elements = quote_statistics_div.find_all('li')
        if len(li_elements) > 13:
            spans = li_elements[13].find_all('span')
            if len(spans) > 1:
                dividend_payer_status = spans[1].text
    
    # Safely handle dividend_payer_status
    if dividend_payer_status != "N/A":
        split_dividend_status = dividend_payer_status.split(" ")
        if len(split_dividend_status) > 1:  # Ensure there are at least two elements
            percentage_with_parens = split_dividend_status[1]
            percentage_string = percentage_with_parens[1:-1]  # Remove parentheses
            dividend_payer_status_percentage = percentage_string
            dividend_per_share = split_dividend_status[0]
            real_time_annual_dividend = dividend_per_share
        else:
            # Handle case where the split doesn't return the expected format
            dividend_payer_status_percentage = "N/A"
            real_time_annual_dividend = "N/A"

    # Calculate Share Price Proximity to 52W Low
    if real_time_share_price != 'N/A' and fifty_two_week_low != 'N/A':
        real_time_share_price = float(real_time_share_price.replace(',', ''))
        share_price_proximity_to_52w_low = (real_time_share_price - fifty_two_week_low) / real_time_share_price
    
    # Calculate Real Time Dividend Yield as a percentage
    if real_time_share_price != 'N/A' and real_time_annual_dividend != 'N/A':
        real_time_annual_dividend = float(real_time_annual_dividend.replace(',', ''))
        real_time_dividend_yield = (real_time_annual_dividend / real_time_share_price) * 100
        real_time_dividend_yield = f"{real_time_dividend_yield:.2f}%"
    
    URL2 = f'https://finance.yahoo.com/quote/{ticker}/analysis/'
    r2 = requests.get(URL2, headers=headers)
    if r2.status_code == 200:
        soup2 = BeautifulSoup(r2.content, 'html.parser')
        # Safely find the growth estimate section
        growth_estimate_section = soup2.find('section', {'data-testid': 'growthEstimate'})
        if growth_estimate_section:
            try:
                growth_estimate_last = growth_estimate_section.find_all('tr')[5].find_all('td')[1].text
                growth_estimate_next = growth_estimate_section.find_all('tr')[4].find_all('td')[1].text
            except IndexError:
                growth_estimate_last = "N/A"
                growth_estimate_next = "N/A"
    else:
        growth_estimate_last = "N/A"
        growth_estimate_next = "N/A"

    #Recieve AAA Bond Value for Ticker [Same for All]
    RESPONSE = requests.get(AAA, headers=headers)
    soup = BeautifulSoup(RESPONSE.text, "html.parser")
    bond_value = soup.find("div", class_="key-stat-title").text
    aaa_bond_value = float(re.search(r"\d+\.\d+", bond_value).group())

    data_dict = {
        "ticker": ticker,
        "company_name": company_name,
        "list_exchange": list_exchange,
        "real_time_share_price": real_time_share_price,
        "ytd_return": ytd_return,
        "market_cap": market_cap,
        "profit_margin": profit_margin,
        "ebitda": ebitda,
        "levered_free_cash_flow": levered_free_cash_flow,
        "fifty_two_week_high": fifty_two_week_high,
        "fifty_two_week_low": fifty_two_week_low,
        "share_price_proximity_to_52w_low": share_price_proximity_to_52w_low,
        "pe_ratio": pe_ratio,
        "eps": eps,
        "dividend_payer_status": dividend_payer_status,
        "dividend_payer_status_percentage": dividend_payer_status_percentage,
        "real_time_annual_dividend": real_time_annual_dividend,
        "growth_estimate_last": growth_estimate_last,
        "real_time_dividend_yield": real_time_dividend_yield,
        "growth_estimate_next": growth_estimate_next,
        "aaa_bond_value": aaa_bond_value
    }

    return data_dict

def save_data_to_csv(data, filename):
    # Check if the CSV file exists
    file_exists = os.path.isfile(filename)
    
    # Open the file in append mode
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        
        # Write the header if the file does not exist
        writer.writeheader()
        
        # Write the data
        for item in data:
            writer.writerow(item)



import json
import os

def save_data_to_json(data, filename):
    if os.path.exists(filename):
        # If file exists, read the existing data
        with open(filename, 'r+') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
            # Ensure existing_data is a list
            if not isinstance(existing_data, list):
                existing_data = []
            # Append new data to existing data
            existing_data.extend(data)
            # Write updated data back to file
            file.seek(0)
            json.dump(existing_data, file, indent=4)
            file.truncate()  # Remove any remaining part after the new data
    else:
        # If file does not exist, initialize with new data
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

def get_data_for_tickers(tickers):
    all_data = []
    for ticker in tickers:
        data = getData(ticker)
        all_data.append(data)
    return all_data

# Example usage
tickers = ['AAPL', 'MSFT', 'GOOGL', 'LI']
all_data = get_data_for_tickers(tickers)

# Save data to CSV and JSON
save_data_to_csv(all_data, 'stock_data.csv')
save_data_to_json(all_data, 'stock_data.json')

# Print the data
for data in all_data:
    print(data)

get_data_for_tickers(['AAPL', 'MSFT', 'GOOGL', 'LI'])