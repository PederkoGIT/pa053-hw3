from flask import Flask, request, Response
import requests
import re

app = Flask(__name__)

def get_airport_temp(iata):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        ap_url = f"https://www.airport-data.com/api/ap_info.json?iata={iata}"
        ap_res = requests.get(ap_url, headers=headers).json()
        
        if 'latitude' not in ap_res or 'longitude' not in ap_res:
            return None
            
        lat, lon = ap_res['latitude'], ap_res['longitude']
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_res = requests.get(weather_url, headers=headers).json()
        
        return weather_res['current_weather']['temperature']
    except Exception:
        return None

def get_stock_price(ticker):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        res = requests.get(url, headers=headers).json()
        return res['chart']['result'][0]['meta']['regularMarketPrice']
    except Exception:
        return None

def evaluate_expression(expr):
    try:
        clean_expr = re.sub(r'[^0-9+\-*/().]', '', expr)
        return eval(clean_expr)
    except Exception:
        return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def api_handler(path):
    val = None
    
    if 'queryAirportTemp' in request.args:
        val = get_airport_temp(request.args.get('queryAirportTemp'))
    elif 'queryStockPrice' in request.args:
        val = get_stock_price(request.args.get('queryStockPrice'))
    elif 'queryEval' in request.args:
        expr = request.args.get('queryEval').replace(' ', '+')
        val = evaluate_expression(expr)
        
    if val is None:
        return Response("undefined", status=400)

    accept_header = request.headers.get('Accept', '')
    if 'xml' in accept_header.lower():
        xml_data = f'<?xml version="1.0" encoding="UTF-8"?><result>{val}</result>'
        return Response(xml_data, mimetype='application/xml')
    else:
        return Response(str(val), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)