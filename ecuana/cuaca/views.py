"""
Views untuk E-Cuaca
Mengambil data cuaca real-time dari OpenWeatherMap API
Tanpa database - data langsung dari API setiap kali halaman dimuat
"""

from django.shortcuts import render
import requests
import json
from datetime import datetime

# ================== KONFIGURASI API ==================
# Gunakan OpenWeatherMap API (free tier)
# 1. Daftar di: https://openweathermap.org/api
# 2. Ambil API Key dari dashboard Anda
# 3. Ganti 'YOUR_API_KEY_HERE' dengan API key Anda

OPENWEATHER_API_KEY = 'cc6f6022507f7698047677773e57ec53'  # GANTI DENGAN API KEY ANDA

# Lokasi Desa Sumberejo
LOCATION = {
    'name': 'Desa Sumberejo',
    'district': 'Kecamatan Pagelaran',
    'city': 'Kabupaten Pringsewu',
    'province': 'Lampung, Indonesia',
    'latitude': -5.3667,  # Koordinat Pringsewu (perkiraan)
    'longitude': 104.9833,
}

# ================== HELPER FUNCTIONS ==================

def get_weather_data():
    """
    Ambil data cuaca dari OpenWeatherMap API
    
    Returns:
        dict: Data cuaca atau error message
    """
    try:
        # Endpoint API (menggunakan koordinat)
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={LOCATION['latitude']}&"
            f"lon={LOCATION['longitude']}&"
            f"appid={OPENWEATHER_API_KEY}&"
            f"units=metric&"  # Gunakan Celsius
            f"lang=id"  # Response dalam Bahasa Indonesia
        )
        
        # Request ke API dengan timeout
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise exception jika status bukan 200
        
        return response.json()
    
    except requests.exceptions.Timeout:
        return {'error': 'API Timeout - koneksi lambat'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Gagal terhubung ke API - periksa koneksi internet'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'Error API: {e.response.status_code} - Periksa API Key'}
    except Exception as e:
        return {'error': f'Error: {str(e)}'}


def parse_weather_data(api_data):
    """
    Parse data dari API ke format yang user-friendly
    
    Args:
        api_data (dict): Response dari OpenWeatherMap API
        
    Returns:
        dict: Data cuaca yang sudah diformat
    """
    if 'error' in api_data:
        return {
            'error': api_data['error'],
            'location_name': f"{LOCATION['name']}, {LOCATION['district']}",
            'location_full': f"{LOCATION['name']}, {LOCATION['district']}, {LOCATION['city']}, {LOCATION['province']}",
        }
    
    try:
        main = api_data.get('main', {})
        weather = api_data.get('weather', [{}])[0]
        wind = api_data.get('wind', {})
        clouds = api_data.get('clouds', {})
        
        # Map weather icon ke emoji/deskripsi
        weather_icon_map = {
            '01d': '☀️',  # Cerah siang
            '01n': '🌙',  # Cerah malam
            '02d': '🌤️',  # Berawan sedikit siang
            '02n': '🌤️',  # Berawan sedikit malam
            '03d': '☁️',  # Berawan siang
            '03n': '☁️',  # Berawan malam
            '04d': '🌥️',  # Mendung siang
            '04n': '🌥️',  # Mendung malam
            '09d': '🌧️',  # Hujan ringan siang
            '09n': '🌧️',  # Hujan ringan malam
            '10d': '🌦️',  # Hujan siang
            '10n': '🌦️',  # Hujan malam
            '11d': '⛈️',  # Badai siang
            '11n': '⛈️',  # Badai malam
            '13d': '❄️',  # Salju siang
            '13n': '❄️',  # Salju malam
            '50d': '🌫️',  # Kabut siang
            '50n': '🌫️',  # Kabut malam
        }
        
        weather_code = api_data.get('weather', [{}])[0].get('icon', '01d')
        weather_emoji = weather_icon_map.get(weather_code, '🌡️')
        
        # Format waktu update
        timestamp = api_data.get('dt', 0)
        update_time = datetime.fromtimestamp(timestamp).strftime('%d %B %Y, %H:%M WIB')
        
        return {
            'error': None,
            'location_name': f"{LOCATION['name']}, {LOCATION['district']}",
            'location_full': f"{LOCATION['name']}, {LOCATION['district']}, {LOCATION['city']}, {LOCATION['province']}",
            'temperature': round(main.get('temp', 0)),
            'feels_like': round(main.get('feels_like', 0)),
            'humidity': main.get('humidity', 0),
            'pressure': main.get('pressure', 0),
            'condition': weather.get('main', 'Unknown'),
            'description': weather.get('description', '').capitalize(),
            'wind_speed': round(wind.get('speed', 0), 1),
            'wind_degree': wind.get('deg', 0),
            'cloudiness': clouds.get('all', 0),
            'visibility': api_data.get('visibility', 0) / 1000,  # Convert ke km
            'temperature_min': round(main.get('temp_min', 0)),
            'temperature_max': round(main.get('temp_max', 0)),
            'weather_emoji': weather_emoji,
            'update_time': update_time,
            'raw_data': api_data,  # Simpan raw data untuk debugging
        }
    
    except KeyError as e:
        return {
            'error': f'Format data tidak dikenali: {str(e)}',
            'location_name': f"{LOCATION['name']}, {LOCATION['district']}",
            'location_full': f"{LOCATION['name']}, {LOCATION['district']}, {LOCATION['city']}, {LOCATION['province']}",
        }


# ================== MAIN VIEW ==================

def index(request):
    """
    View halaman utama E-Cuaca
    Mengambil data cuaca real-time dan menampilkannya
    """
    # Ambil data dari API
    api_data = get_weather_data()
    
    # Parse data ke format yang dimengerti template
    weather_data = parse_weather_data(api_data)
    
    # Context untuk template
    context = {
        'weather': weather_data,
        'api_status': 'connected' if not weather_data.get('error') else 'error',
    }
    
    # Render template dengan context
    return render(request, 'index.html', context)


def debug_api(request):
    """
    View untuk debugging API (optional)
    Akses di: http://127.0.0.1:8000/api/debug
    """
    api_data = get_weather_data()
    
    context = {
        'raw_api_response': json.dumps(api_data, indent=2, ensure_ascii=False),
        'weather': parse_weather_data(api_data),
    }
    
    return render(request, 'debug.html', context)
