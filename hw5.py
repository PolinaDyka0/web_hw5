import argparse
from datetime import datetime, timedelta
import asyncio
import aiohttp


API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

async def request(url: str):
       async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    response_data = await response.json()
        
                    return response_data["exchangeRate"]
                else:
                    print(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))
               

async def get_exchange_rates_on_date(date):
    exchange_rates = await request(API_URL + date)
    if exchange_rates:
        euro = list(filter(lambda er: er["currency"] == "EUR", exchange_rates))[0]
        usd = list(filter(lambda er: er["currency"] == "USD", exchange_rates))[0]

        return {
            date: {
                "EUR": {
                    "sale": float(euro["saleRateNB"]),
                    "purchase": float(euro["purchaseRateNB"]),
                },
                "USD": {
                    "sale": float(usd["saleRateNB"]),
                    "purchase": float(usd["purchaseRateNB"]),
                },
            }
        }
    return 'Not found'


async def get_exchange_rates(days):
    tasks = []
    for i in range(days):
        date = (datetime.today() - timedelta(days=i)).strftime("%d.%m.%Y")
        tasks.append(get_exchange_rates_on_date(date))
    
    exchange_rates = await asyncio.gather(*tasks)
    return exchange_rates


async def main(days):
    exchange_rates = await get_exchange_rates(days)
    for exchange_rate in exchange_rates:
        if isinstance(exchange_rate, dict):
            for date, rates in exchange_rate.items():
                print(f"{date}:")
                for currency, values in rates.items():
                    print(f"    {currency}:")
                    for key, value in values.items():
                        print(f"        {key}: {value}")
        else:
            print(exchange_rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get exchange rates of USD and EUR from PrivatBank API.")
    parser.add_argument(
        "days", type=int, help="Number of days for which to get exchange rates. Maximum value is 10."
    )
    args = parser.parse_args()

    if args.days > 10:
        print("Maximum value for days is 10.")
    else:
        asyncio.run(main(args.days))
 
