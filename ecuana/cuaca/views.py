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


def get_forecast_data():
    """
    Ambil forecast cuaca 5 hari dari OpenWeatherMap API
    
    Returns:
        dict: Data forecast atau error message
    """
    try:
        # Endpoint API forecast (5 hari dengan interval 3 jam)
        url = (
            f"https://api.openweathermap.org/data/2.5/forecast?"
            f"lat={LOCATION['latitude']}&"
            f"lon={LOCATION['longitude']}&"
            f"appid={OPENWEATHER_API_KEY}&"
            f"units=metric&"
            f"lang=id"
        )
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.Timeout:
        return {'error': 'Forecast API Timeout'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Gagal terhubung ke Forecast API'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'Error Forecast API: {e.response.status_code}'}
    except Exception as e:
        return {'error': f'Error Forecast: {str(e)}'}


def parse_forecast_data(api_data):
    """
    Parse forecast data dan ambil 1 data per hari (hari siang ~ 12:00)
    
    Args:
        api_data (dict): Response dari OpenWeatherMap Forecast API
        
    Returns:
        list: List forecast per hari
    """
    if 'error' in api_data or 'list' not in api_data:
        return []
    
    try:
        # Map weather icon ke emoji
        weather_icon_map = {
            '01d': '☀️', '01n': '🌙',
            '02d': '🌤️', '02n': '🌤️',
            '03d': '☁️', '03n': '☁️',
            '04d': '🌥️', '04n': '🌥️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌦️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️',
        }
        
        # Group data by hari
        daily_forecasts = {}
        
        for item in api_data.get('list', []):
            # Ambil waktu
            timestamp = item.get('dt', 0)
            dt_obj = datetime.fromtimestamp(timestamp)
            date_str = dt_obj.strftime('%Y-%m-%d')
            hour = dt_obj.hour
            
            # Jika belum ada data untuk hari ini, atau jika ini data siang (12:00)
            if date_str not in daily_forecasts or (12 <= hour < 15):
                main = item.get('main', {})
                weather = item.get('weather', [{}])[0]
                wind = item.get('wind', {})
                
                weather_code = weather.get('icon', '01d')
                weather_emoji = weather_icon_map.get(weather_code, '🌡️')
                
                # Hitung rata-rata temperatur
                temp_avg = round((main.get('temp_min', 0) + main.get('temp_max', 0)) / 2)
                
                daily_forecasts[date_str] = {
                    'date': dt_obj.strftime('%a, %d %b'),  # Format: Mon, 27 Jan
                    'day_name': dt_obj.strftime('%A'),  # Format: Monday
                    'date_full': dt_obj.strftime('%d %B %Y'),
                    'timestamp': timestamp,
                    'temperature': round(main.get('temp', 0)),
                    'temperature_min': round(main.get('temp_min', 0)),
                    'temperature_max': round(main.get('temp_max', 0)),
                    'temperature_avg': temp_avg,
                    'feels_like': round(main.get('feels_like', 0)),
                    'humidity': main.get('humidity', 0),
                    'pressure': main.get('pressure', 0),
                    'condition': weather.get('main', 'Unknown'),
                    'description': weather.get('description', '').capitalize(),
                    'wind_speed': round(wind.get('speed', 0), 1),
                    'wind_degree': wind.get('deg', 0),
                    'cloudiness': item.get('clouds', {}).get('all', 0),
                    'rain': item.get('rain', {}).get('3h', 0),
                    'precipitation': round(item.get('pop', 0) * 100),  # Convert to percentage and round
                    'weather_emoji': weather_emoji,
                    'sunrise': '06:00',  # Will be updated from API if available
                    'sunset': '18:00',   # Will be updated from API if available
                }
        
        # Urutkan berdasarkan tanggal dan ambil 7 hari pertama
        sorted_forecasts = sorted(daily_forecasts.items())[:7]
        return [forecast for _, forecast in sorted_forecasts]
    
    except Exception as e:
        print(f"Error parsing forecast: {str(e)}")
        return []


def check_weather_warnings(weather_data):
    """
    Cek apakah ada kondisi cuaca berbahaya yang memerlukan peringatan
    
    Args:
        weather_data (dict): Data cuaca yang sudah di-parse
        
    Returns:
        dict: Dictionary berisi warning info
    """
    warnings = {
        'has_warning': False,
        'warning_type': None,
        'warning_message': '',
        'warning_icon': '',
        'warning_class': '',
    }
    
    if 'error' in weather_data or weather_data.get('error'):
        return warnings
    
    condition = weather_data.get('condition', '').lower()
    description = weather_data.get('description', '').lower()
    wind_speed = weather_data.get('wind_speed', 0)
    humidity = weather_data.get('humidity', 0)
    
    # Cek Badai/Thunderstorm (paling urgent)
    if 'thunderstorm' in condition or 'thunderstorm' in description:
        warnings['has_warning'] = True
        warnings['warning_type'] = 'thunderstorm'
        warnings['warning_icon'] = '⚡'
        warnings['warning_message'] = 'PERINGATAN BADAI! Warga disarankan segera berlindung di tempat aman. Hindari berada di luar ruangan.'
        warnings['warning_class'] = 'danger'
    
    # Cek Hujan Lebat
    elif ('rain' in condition and 'heavy' in description) or 'heavy rain' in description:
        warnings['has_warning'] = True
        warnings['warning_type'] = 'heavy_rain'
        warnings['warning_icon'] = '🌧️'
        warnings['warning_message'] = 'Hujan Lebat! Diperkirakan hujan lebat hari ini. Warga diimbau berhati-hati saat beraktivitas di luar rumah.'
        warnings['warning_class'] = 'warning'
    
    # Cek Angin Kencang (≥ 10 m/s)
    elif wind_speed >= 10:
        warnings['has_warning'] = True
        warnings['warning_type'] = 'strong_wind'
        warnings['warning_icon'] = '🌬️'
        warnings['warning_message'] = f'Angin Kencang! Kecepatan angin mencapai {wind_speed} m/s. Hati-hati saat berada di luar rumah.'
        warnings['warning_class'] = 'warning'
    
    return warnings


def get_activity_recommendation(weather_data):
    """
    Berikan rekomendasi aktivitas warga berdasarkan kondisi cuaca
    Rekomendasi komprehensif untuk berbagai jenis aktivitas
    
    Args:
        weather_data (dict): Data cuaca yang sudah di-parse
        
    Returns:
        dict: Rekomendasi aktivitas dengan tips detail
    """
    recommendation = {
        'activity': '',
        'description': '',
        'icon': '',
        'tips': [],
        'cautions': [],
        'best_time': '',
        'recommendations': [],
    }
    
    if 'error' in weather_data or weather_data.get('error'):
        return recommendation
    
    condition = weather_data.get('condition', '').lower()
    description = weather_data.get('description', '').lower()
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    temperature = weather_data.get('temperature', 0)
    cloudiness = weather_data.get('cloudiness', 0)
    
    # ========== BADAI - PERINGATAN TINGKAT TERTINGGI ==========
    if 'thunderstorm' in condition or 'thunderstorm' in description:
        recommendation['activity'] = '⚡ LARANGAN AKTIVITAS - BADAI'
        recommendation['icon'] = '⚡'
        recommendation['description'] = 'BERBAHAYA! Badai sedang terjadi - warga HARUS berada di dalam rumah.'
        recommendation['cautions'] = [
            '🚫 JANGAN berada di luar rumah',
            '🚫 JANGAN menyentuh benda logam',
            '🚫 JANGAN menggunakan listrik yang tidak perlu',
            '⚠️ Matikan peralatan elektronik jika ada petir dekat',
        ]
        recommendation['tips'] = [
            '✓ Berlindunglah di tempat aman (rumah/bangunan tertutup)',
            '✓ Hindarkan jendela dan pintu',
            '✓ Tunggu sampai badai berlalu sebelum keluar',
            '✓ Siaga untuk bencana alam (banjir/angin kencang)',
        ]
        return recommendation
    
    # ========== HUJAN LEBAT - PERINGATAN LEVEL TINGGI ==========
    elif 'rain' in condition and ('heavy' in description or 'moderate' in description and wind_speed > 7):
        recommendation['activity'] = '🌧️ BATASI AKTIVITAS LUAR RUMAH'
        recommendation['icon'] = '🌧️'
        recommendation['description'] = 'Hujan lebat sedang berlangsung - aktivitas luar rumah sangat berisiko.'
        recommendation['cautions'] = [
            '⚠️ Hindari berjalan/berkendara di jalan banjir',
            '⚠️ Waspada petir dan angin kencang',
            '⚠️ Jangan membiarkan anak-anak bermain di luar',
        ]
        recommendation['tips'] = [
            '✓ Tunda aktivitas bertani untuk sekarang',
            '✓ Siapkan barang-barang berharga di tempat tinggi',
            '✓ Manfaatkan waktu untuk pekerjaan dalam rumah',
            '✓ Pastikan sistem drainase rumah berfungsi baik',
            '✓ Periksa kondisi atap rumah',
        ]
        recommendation['recommendations'] = [
            '🏠 Aktivitas Indoor: Membersihkan, memasak, belajar',
            '🐔 Ternak: Pastikan kandang tertutup dan kering',
            '👨‍🌾 Pertanian: Istirahat dan persiapan untuk musim cerah',
        ]
        recommendation['best_time'] = 'Tunggu cuaca membaik (15+ jam ke depan)'
        return recommendation
    
    # ========== HUJAN RINGAN - PERHATIAN ==========
    elif 'rain' in condition or 'drizzle' in description:
        recommendation['activity'] = '🌧️ Aktivitas Terbatas'
        recommendation['icon'] = '🌧️'
        recommendation['description'] = 'Hujan ringan - aktivitas outdoor bisa dilanjutkan dengan hati-hati.'
        recommendation['cautions'] = [
            '⚠️ Gunakan payung atau jas hujan',
            '⚠️ Hati-hati di jalan yang licin',
        ]
        recommendation['tips'] = [
            '✓ Masih bisa melakukan aktivitas ringan di luar rumah',
            '✓ Gunakan alat pelindung (payung, jas hujan)',
            '✓ Hindari area yang rawan banjir/genangan',
            '✓ Kurangi penyiraman tanaman (sudah dapat air dari hujan)',
        ]
        recommendation['recommendations'] = [
            '👨‍🌾 Pertanian: Perawatan tanaman ringan (pemangkasan)',
            '🚴 Olahraga: Tunda aktivitas ekstrem seperti lari jauh',
            '🌾 Panen: Tunda panen hingga tanah kering',
        ]
        recommendation['best_time'] = 'Beberapa jam lagi (setelah hujan berhenti)'
        return recommendation
    
    # ========== CERAH/CLEAR - KONDISI TERBAIK ==========
    if condition in ['clear', 'sunny'] or 'clear' in description or 'sunny' in description:
        recommendation['activity'] = '☀️ WAKTU TERBAIK - AKTIVITAS OPTIMAL'
        recommendation['icon'] = '☀️'
        recommendation['description'] = 'Cuaca cerah sempurna untuk semua aktivitas luar rumah!'
        
        # Sub-rekomendasi berdasarkan suhu
        if temperature > 30:
            recommendation['tips'] = [
                '✓ Waktu IDEAL untuk bertani dan menjemur',
                '✓ Gunakan sunscreen SPF 30+ untuk perlindungan UV',
                '✓ Bawa air minum 1-2 liter',
                '✓ Gunakan topi atau payung untuk naungan',
                '✓ Istirahat di tempat teduh setiap 1-2 jam',
            ]
            recommendation['cautions'] = [
                '⚠️ Suhu tinggi (' + str(temperature) + '°C) - risiko heat stress',
                '⚠️ Hindari bekerja saat siang terik (11:00-15:00)',
            ]
        else:
            recommendation['tips'] = [
                '✓ Waktu TERBAIK untuk semua aktivitas outdoor',
                '✓ Sempurna untuk bertani, olahraga, dan jemur pakaian',
                '✓ Tingkat kenyamanan tinggi',
                '✓ Manfaatkan cuaca ini untuk aktivitas yang tertunda',
            ]
        
        recommendation['recommendations'] = [
            '👨‍🌾 Bertani: Waktu optimal - mulai penyiraman pagi/sore',
            '👕 Menjemur: Hasil maksimal dengan cahaya matahari penuh',
            '🏃 Olahraga: Lari pagi/sore adalah waktu terbaik',
            '🚜 Panen: Kondisi sempurna untuk panen padi/sayur',
            '🔧 Perbaikan: Renovasi rumah atau perbaikan atap',
        ]
        recommendation['best_time'] = 'Sekarang! Pagi hingga sore jam 15:00'
        
        return recommendation
    
    # ========== BERAWAN - AKTIVITAS NORMAL ==========
    elif 'cloud' in condition or 'cloud' in description or 'overcast' in description:
        recommendation['activity'] = '☁️ Aktivitas Normal'
        recommendation['icon'] = '☁️'
        recommendation['description'] = 'Cuaca berawan - aktivitas luar rumah dapat dilanjutkan dengan nyaman.'
        recommendation['tips'] = [
            '✓ Tidak perlu khawatir sinar UV berlebihan',
            '✓ Aktivitas outdoor lebih nyaman (tidak terlalu panas)',
            '✓ Monitor perubahan cuaca setiap jam',
            '✓ Bawa air minum secukupnya',
        ]
        recommendation['cautions'] = [
            '⚠️ Cuaca bisa berubah menjadi hujan mendadak',
            '⚠️ Siapkan payung sebagai persiapan',
        ]
        recommendation['recommendations'] = [
            '👨‍🌾 Bertani: Waktu baik untuk kerja lapangan',
            '🌾 Pembibitan: Ideal tanpa sinar UV langsung',
            '🏃 Olahraga: Kondisi ideal tanpa kelelahan panas',
            '🚴 Aktivitas Komunitas: Bisa dijalankan dengan nyaman',
        ]
        recommendation['best_time'] = 'Sepanjang hari'
        return recommendation
    
    # ========== ANGIN KENCANG ==========
    if wind_speed >= 10:
        if not recommendation['cautions']:
            recommendation['cautions'] = []
        recommendation['cautions'].append(
            f'🌬️ Angin kencang ({wind_speed} m/s) - potensi kerusakan'
        )
        recommendation['tips'].append(
            '⚠️ Amankan barang-barang yang mudah terbang (pot, atap)'
        )
    
    # ========== KELEMBAPAN TINGGI - WASPADA PENYAKIT TANAMAN ==========
    if humidity > 85:
        recommendation['activity'] = '💧 Waspada Kelembapan Sangat Tinggi'
        recommendation['icon'] = '💧'
        recommendation['description'] = f'Kelembapan udara SANGAT TINGGI ({humidity}%) - risiko tinggi penyakit tanaman dan jamur.'
        recommendation['cautions'] = [
            f'🍄 Kelembapan {humidity}% = risiko jamur & penyakit tanaman',
            '⚠️ Potensi bercak penyakit pada daun',
            '⚠️ Pembusukan pada akar',
        ]
        recommendation['tips'] = [
            '✓ TINGKATKAN ventilasi di sekitar tanaman',
            '✓ Kurangi frekuensi penyiraman',
            '✓ Pastikan sistem drainase berfungsi optimal',
            '✓ Buang daun yang terinfeksi penyakit',
            '✓ Semprotkan fungisida pencegahan jika perlu',
            '✓ Periksa tanaman setiap pagi dan sore',
        ]
        recommendation['recommendations'] = [
            '🌱 Tanaman: Perbaikan sirkulasi udara (potong daun lebat)',
            '🚜 Operasional: Aplikasi fungisida preventif',
            '💨 Ventilasi: Buka pintu & jendela untuk sirkulasi',
        ]
        return recommendation
    
    elif humidity > 75:
        if not recommendation['cautions']:
            recommendation['cautions'] = []
        recommendation['cautions'].append(
            f'💧 Kelembapan tinggi ({humidity}%) - monitor penyakit tanaman'
        )
    
    # ========== KELEMBAPAN RENDAH ==========
    if humidity < 50:
        if not recommendation['cautions']:
            recommendation['cautions'] = []
        recommendation['cautions'].append(
            f'🏜️ Kelembapan rendah ({humidity}%) - tanah mudah kering'
        )
        if 'tips' not in recommendation or not recommendation['tips']:
            recommendation['tips'] = []
        recommendation['tips'].append(
            '✓ Tambah frekuensi penyiraman untuk mencegah kekeringan'
        )
    
    return recommendation


def calculate_weekly_stats(forecast_data):
    """
    Hitung statistik mingguan dari data forecast
    
    Args:
        forecast_data (list): List data forecast
        
    Returns:
        dict: Statistik mingguan
    """
    stats = {
        'hottest_day': None,
        'rainiest_day': None,
        'average_temperature': 0,
        'coldest_day': None,
        'total_forecast_days': len(forecast_data),
    }
    
    if not forecast_data:
        return stats
    
    try:
        # Cari hari terpanas
        hottest = max(forecast_data, key=lambda x: x.get('temperature_max', 0))
        stats['hottest_day'] = {
            'day_name': hottest.get('day_name', ''),
            'temperature': hottest.get('temperature_max', 0),
            'emoji': '🔥',
        }
        
        # Cari hari terdingin
        coldest = min(forecast_data, key=lambda x: x.get('temperature_min', 0))
        stats['coldest_day'] = {
            'day_name': coldest.get('day_name', ''),
            'temperature': coldest.get('temperature_min', 0),
            'emoji': '❄️',
        }
        
        # Hitung rata-rata suhu
        temps = [f.get('temperature_avg', 0) for f in forecast_data]
        avg_temp = round(sum(temps) / len(temps)) if temps else 0
        stats['average_temperature'] = avg_temp
        
        # Cari hari paling hujan
        rainy_days = [f for f in forecast_data if f.get('rain', 0) > 0]
        if rainy_days:
            rainiest = max(rainy_days, key=lambda x: x.get('rain', 0))
            stats['rainiest_day'] = {
                'day_name': rainiest.get('day_name', ''),
                'rain': rainiest.get('rain', 0),
                'condition': rainiest.get('description', ''),
                'emoji': '🌧️',
            }
        
    except Exception as e:
        print(f"Error calculating weekly stats: {str(e)}")
    
    return stats


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
    Mengambil data cuaca real-time, forecast, peringatan, dan rekomendasi
    """
    # Ambil data dari API
    api_data = get_weather_data()
    
    # Parse data ke format yang dimengerti template
    weather_data = parse_weather_data(api_data)
    
    # Ambil forecast data
    forecast_api_data = get_forecast_data()
    forecast_data = parse_forecast_data(forecast_api_data)
    
    # Cek warning cuaca
    weather_warning = check_weather_warnings(weather_data)
    
    # Dapatkan rekomendasi aktivitas
    activity_recommendation = get_activity_recommendation(weather_data)
    
    # Hitung forecast summary
    forecast_summary = {
        'avg_temp': '-',
        'hottest_day': '-',
        'total_rainfall': '0'
    }
    
    # Hitung statistik mingguan
    weekly_stats = calculate_weekly_stats(forecast_data)
    
    # Dapatkan rekomendasi detail untuk pop-up modal
    detailed_recommendations = get_detailed_recommendations(weather_data)
    
    if forecast_data:
        # Hitung rata-rata suhu
        temps = [f.get('temperature_avg', 0) for f in forecast_data]
        avg_temp = round(sum(temps) / len(temps)) if temps else 0
        forecast_summary['avg_temp'] = avg_temp
        
        # Cari hari terpanas
        hottest = max(forecast_data, key=lambda x: x.get('temperature_max', 0), default=None)
        if hottest:
            forecast_summary['hottest_day'] = f"{hottest['day_name']} ({hottest['temperature_max']}°C)"
        
        # Hitung total curah hujan
        total_rain = sum([f.get('rain', 0) for f in forecast_data])
        forecast_summary['total_rainfall'] = f"{total_rain:.1f}"
    
    # Context untuk template
    context = {
        'weather': weather_data,
        'forecast': forecast_data,
        'forecast_summary': forecast_summary,
        'weather_warning': weather_warning,
        'activity_recommendation': activity_recommendation,
        'weekly_stats': weekly_stats,
        'detailed_recommendations': detailed_recommendations,
        'api_status': 'connected' if not weather_data.get('error') else 'error',
    }
    
    # Render template dengan context
    return render(request, 'index.html', context)


def tentang(request):
    """
    View halaman Tentang Sistem E-Cuaca
    Menampilkan informasi tentang E-Cuaca dan manfaatnya
    """
    context = {
        'location_name': LOCATION['name'],
        'location_full': f"{LOCATION['name']}, {LOCATION['district']}, {LOCATION['city']}, {LOCATION['province']}",
    }
    return render(request, 'tentang.html', context)


# ================== DETAILED ACTIVITY RECOMMENDATIONS ==================

def get_detailed_recommendations(weather_data):
    """
    Berikan rekomendasi aktivitas detail berdasarkan kategori
    Rekomendasi berdasarkan kondisi cuaca REAL-TIME hari ini
    
    Args:
        weather_data (dict): Data cuaca yang sudah di-parse
        
    Returns:
        dict: Rekomendasi detail per kategori aktivitas
    """
    recommendations = {
        'agriculture': {
            'title': '👨‍🌾 Pertanian & Perkebunan',
            'activities': [],
            'cautions': [],
            'best_timing': '',
            'priority': 'normal'
        },
        'sports': {
            'title': '🏃 Olahraga & Aktivitas Fisik',
            'activities': [],
            'cautions': [],
            'best_timing': '',
            'priority': 'normal'
        },
        'household': {
            'title': '🏠 Pekerjaan Rumah Tangga',
            'activities': [],
            'cautions': [],
            'best_timing': '',
            'priority': 'normal'
        },
        'construction': {
            'title': '🔨 Perbaikan & Konstruksi',
            'activities': [],
            'cautions': [],
            'best_timing': '',
            'priority': 'normal'
        },
        'animal_care': {
            'title': '🐔 Peternakan & Hewan Ternak',
            'activities': [],
            'cautions': [],
            'best_timing': '',
            'priority': 'normal'
        }
    }
    
    if 'error' in weather_data or weather_data.get('error'):
        return recommendations
    
    condition = weather_data.get('condition', '').lower()
    description = weather_data.get('description', '').lower()
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    temperature = weather_data.get('temperature', 0)
    cloudiness = weather_data.get('cloudiness', 0)
    
    # ===== BADAI / THUNDERSTORM - LARANGAN SEMUA AKTIVITAS =====
    if 'thunderstorm' in condition or 'thunderstorm' in description:
        for cat in recommendations.values():
            cat['priority'] = 'danger'
            cat['activities'] = ['🚫 SEMUA AKTIVITAS DILARANG SAAT BADAI']
            cat['cautions'] = [
                'WAJIB berada di dalam rumah/bangunan tertutup',
                'Jangan keluar rumah dalam kondisi apapun',
                'Matikan peralatan elektronik jika ada petir dekat',
            ]
        return recommendations
    
    # ===== HUJAN LEBAT - AKTIVITAS DIBATASI =====
    elif 'rain' in condition and ('heavy' in description or 'moderate' in description and wind_speed > 7):
        # PERTANIAN
        recommendations['agriculture']['priority'] = 'warning'
        recommendations['agriculture']['activities'] = [
            'Tunda operasional lapangan sementara',
            'Persiapan benih untuk musim cerah',
            'Perawatan di greenhouse/area tertutup',
            'Inventori alat pertanian',
            'Pembuatan pupuk kompos',
        ]
        recommendations['agriculture']['cautions'] = [
            'Hindari pekerjaan di lahan basah (tergelincir)',
            'Jangan panen saat hujan (hasil berkurang)',
            'Waspada banjir di lahan rendah',
        ]
        recommendations['agriculture']['best_timing'] = 'Tunggu cuaca cerah (12+ jam)'
        
        # OLAHRAGA
        recommendations['sports']['priority'] = 'warning'
        recommendations['sports']['activities'] = [
            'Aktivitas indoor: gym, yoga, senam rumahan',
            'Renang di kolam tertutup/indoor',
            'Pelatihan teknik (tidak butuh lapangan)',
            'Bersepeda statis/indoor cycling',
        ]
        recommendations['sports']['cautions'] = [
            'Hindari lari di jalan yang licin',
            'Tidak ada aktivitas outdoor',
            'Hati-hati jika harus berjalan di hujan',
        ]
        recommendations['sports']['best_timing'] = 'Setelah hujan berhenti'
        
        # PEKERJAAN RUMAH
        recommendations['household']['priority'] = 'normal'
        recommendations['household']['activities'] = [
            'Membersihkan dan mengorganisir rumah',
            'Memasak dan menyiapkan makanan',
            'Mencuci dan merapikan pakaian',
            'Belajar dan pekerjaan administratif',
            'Perawatan tanaman hias indoor',
            'Perbaikan interior rumah',
        ]
        recommendations['household']['cautions'] = [
            'Pastikan ventilasi rumah cukup',
            'Waspada kelembapan tinggi (jamur)',
        ]
        recommendations['household']['best_timing'] = 'Sepanjang hari'
        
        # PERBAIKAN
        recommendations['construction']['priority'] = 'warning'
        recommendations['construction']['activities'] = [
            'Interior finishing (pengecatan dalam)',
            'Perbaikan plumbing/pipa air',
            'Perbaikan listrik yang aman',
            'Penggantian furniture',
        ]
        recommendations['construction']['cautions'] = [
            'HINDARI pekerjaan atap saat hujan',
            'Tidak ada penggalian/pekerjaan tanah',
            'Material dapat rusak karena air',
        ]
        recommendations['construction']['best_timing'] = 'Tunggu cuaca cerah'
        
        # PETERNAKAN
        recommendations['animal_care']['priority'] = 'normal'
        recommendations['animal_care']['activities'] = [
            'Pembersihan kandang & alas tidur hewan',
            'Pengecekkan kesehatan hewan',
            'Pemberian pakan di dalam kandang',
            'Penyiapan cadangan pakan/air',
            'Pemeriksaan sistem ventilasi kandang',
        ]
        recommendations['animal_care']['cautions'] = [
            'Pastikan kandang tidak kebanjiran',
            'Periksa sistem drainase kandang',
            'Kurangi stress pada hewan (kebisingan)',
        ]
        recommendations['animal_care']['best_timing'] = 'Pagi hari setelah hujan berkurang'
        
        return recommendations
    
    # ===== HUJAN RINGAN =====
    elif 'rain' in condition or 'drizzle' in description:
        # PERTANIAN
        recommendations['agriculture']['priority'] = 'normal'
        recommendations['agriculture']['activities'] = [
            'Pemeliharaan tanaman ringan (penyiangan)',
            'Pengobatan penyakit tanaman',
            'Pemberian pupuk daun',
            'Pemangkasan daun/ranting yang rusak',
            'Pengecekan sistem irigasi',
        ]
        recommendations['agriculture']['cautions'] = [
            'Gunakan payung/jas hujan',
            'Hindari area yang tergenang air',
            'Kurangi penyiraman (sudah dapat air hujan)',
        ]
        recommendations['agriculture']['best_timing'] = 'Sore hari, setelah hujan berhenti'
        
        # OLAHRAGA
        recommendations['sports']['priority'] = 'normal'
        recommendations['sports']['activities'] = [
            'Jogging dengan payung (intensitas rendah)',
            'Bersepeda untuk transportasi (hati-hati)',
            'Latihan kecepatan pendek',
            'Aktivitas indoor tetap ideal',
        ]
        recommendations['sports']['cautions'] = [
            'Gunakan payung dan perlengkapan hujan',
            'Hati-hati di area licin',
            'Kurangi intensitas latihan',
        ]
        recommendations['sports']['best_timing'] = 'Setelah hujan berhenti, lebih baik sore'
        
        # PEKERJAAN RUMAH
        recommendations['household']['priority'] = 'normal'
        recommendations['household']['activities'] = [
            'Semua pekerjaan rumah tangga bisa dilakukan',
            'Hari ideal untuk mencuci (banyak water supply)',
            'Memasak makanan yang hangat',
            'Belajar dan bekerja dari rumah',
        ]
        recommendations['household']['cautions'] = [
            'Monitor kelembapan rumah',
        ]
        recommendations['household']['best_timing'] = 'Sepanjang hari'
        
        # PERBAIKAN
        recommendations['construction']['priority'] = 'warning'
        recommendations['construction']['activities'] = [
            'Interior finishing & pengecatan',
            'Perbaikan furnitur',
            'Pekerjaan plumbing',
            'Pekerjaan listrik indoor',
        ]
        recommendations['construction']['cautions'] = [
            'HINDARI pekerjaan atap',
            'Tidak ada pekerjaan yang butuh material kering',
        ]
        recommendations['construction']['best_timing'] = 'Interior saja, hindari eksterior'
        
        # PETERNAKAN
        recommendations['animal_care']['priority'] = 'normal'
        recommendations['animal_care']['activities'] = [
            'Pemberian pakan & air minum normal',
            'Pembersihan kandang (lebih sering)',
            'Pengecekan kesehatan hewan',
            'Persiapan alas kandang yang kering',
        ]
        recommendations['animal_care']['cautions'] = [
            'Pastikan kandang tetap kering',
            'Periksa sistem drainase kandang',
        ]
        recommendations['animal_care']['best_timing'] = 'Pagi & sore hari'
        
        return recommendations
    
    # ===== CERAH / CLEAR - KONDISI OPTIMAL =====
    if condition in ['clear', 'sunny'] or 'clear' in description or 'sunny' in description:
        # PERTANIA
        recommendations['agriculture']['priority'] = 'success'
        recommendations['agriculture']['activities'] = [
            '🏆 WAKTU TERBAIK untuk semua aktivitas pertanian',
            'Penyiraman pagi hari (efisiensi air maksimal)',
            'Panen sayuran/buah (hasil optimal)',
            'Pengolahan lahan untuk musim berikutnya',
            'Penyemprotan pestisida/fungisida',
            'Jemur hasil pertanian (bumbu, biji-bijian)',
        ]
        recommendations['agriculture']['cautions'] = [
            f'Suhu tinggi ({temperature}°C) - istirahat berkala',
            'Minum air banyak saat bekerja',
            'Gunakan sunscreen dan topi',
        ] if temperature > 30 else [
            'Kondisi ideal tanpa risiko panas berlebihan',
        ]
        recommendations['agriculture']['best_timing'] = 'Pagi (06:00-10:00) atau sore (15:00-18:00)'
        
        # OLAHRAGA
        recommendations['sports']['priority'] = 'success'
        recommendations['sports']['activities'] = [
            '🏆 KONDISI SEMPURNA untuk semua olahraga outdoor',
            'Jogging/lari pagi atau sore',
            'Bersepeda santai atau marathon',
            'Olahraga tim (sepak bola, bola basket, voli)',
            'Senam pagi komunitas',
            'Aktivitas outdoor family gathering',
        ]
        recommendations['sports']['cautions'] = [
            f'Suhu tinggi ({temperature}°C) - minum air teratur',
            'Gunakan sunscreen SPF 30+',
            'Istirahat di tempat teduh setiap 30-45 menit',
        ] if temperature > 30 else [
            'Kondisi ideal untuk aktivitas intensif',
        ]
        recommendations['sports']['best_timing'] = 'Pagi (06:00-10:00) atau sore (16:00-18:00)'
        
        # PEKERJAAN RUMAH
        recommendations['household']['priority'] = 'success'
        recommendations['household']['activities'] = [
            'Menjemur pakaian (hasil maksimal)',
            'Membersihkan halaman/teras',
            'Mencuci mobil/kendaraan',
            'Perawatan tanaman outdoor',
            'Aktivitas berkebun & dekorasi taman',
            'Mencuci aksesoris rumah tangga',
        ]
        recommendations['household']['cautions'] = [
            'Gunakan perlindungan dari sinar UV',
        ]
        recommendations['household']['best_timing'] = 'Sepanjang hari, terutama siang'
        
        # PERBAIKAN
        recommendations['construction']['priority'] = 'success'
        recommendations['construction']['activities'] = [
            '🏆 KONDISI SEMPURNA untuk semua pekerjaan konstruksi',
            'Pengecatan exterior/interior',
            'Perbaikan atap (paling ideal)',
            'Pengecatan dan finishing',
            'Pekerjaan kayu & furniture',
            'Renovasi rumah (full)',
            'Pengeringan material sebelum finishing',
        ]
        recommendations['construction']['cautions'] = [
            f'Suhu tinggi ({temperature}°C) - istirahat teratur',
            'Pengecatan best pada sore hari',
        ] if temperature > 30 else [
            'Kondisi ideal untuk semua pekerjaan',
        ]
        recommendations['construction']['best_timing'] = 'Pagi (sebelum terlalu panas) untuk pekerjaan berat'
        
        # PETERNAKAN
        recommendations['animal_care']['priority'] = 'normal'
        recommendations['animal_care']['activities'] = [
            'Pemberian pakan normal',
            'Pembersihan kandang',
            'Olahraga hewan ternak (pasturing)',
            'Penyiangan rumput untuk pakan',
            'Penjemuran tempat tidur hewan',
            'Vaksinasi/pemeriksaan kesehatan',
        ]
        recommendations['animal_care']['cautions'] = [
            f'Suhu tinggi ({temperature}°C) - sediakan air minum banyak',
            'Pastikan kandang ada naungan (heat stress)',
        ] if temperature > 30 else [
            'Kondisi ideal untuk manajemen ternak',
        ]
        recommendations['animal_care']['best_timing'] = 'Pagi awal atau sore hari'
        
        return recommendations
    
    # ===== BERAWAN / CLOUDY - NORMAL =====
    elif 'cloud' in condition or 'cloud' in description or 'overcast' in description:
        # PERTANIAN
        recommendations['agriculture']['priority'] = 'normal'
        recommendations['agriculture']['activities'] = [
            'Penyiraman tanaman tanpa stress UV',
            'Pengobatan penyakit tanaman',
            'Pemberian pupuk',
            'Penyiangan dan pemeliharaan',
            'Panen jenis tanaman tertentu (ideal)',
            'Pembibitan tanaman',
        ]
        recommendations['agriculture']['cautions'] = [
            'Monitor perubahan cuaca (bisa hujan)',
            'Siapkan payung sebagai backup',
        ]
        recommendations['agriculture']['best_timing'] = 'Sepanjang hari'
        
        # OLAHRAGA
        recommendations['sports']['priority'] = 'normal'
        recommendations['sports']['activities'] = [
            'Semua aktivitas olahraga outdoor ideal',
            'Kondisi nyaman tanpa panas berlebihan',
            'Jogging, bersepeda, olahraga tim',
            'Aktivitas intensitas tinggi aman dilakukan',
        ]
        recommendations['sports']['cautions'] = [
            'Siapkan payung jika ingin main lama',
            'Monitor perubahan cuaca',
        ]
        recommendations['sports']['best_timing'] = 'Sepanjang hari, ideal untuk durasi panjang'
        
        # PEKERJAAN RUMAH
        recommendations['household']['priority'] = 'normal'
        recommendations['household']['activities'] = [
            'Menjemur pakaian (hasil cukup baik)',
            'Semua pekerjaan outdoor bisa dilakukan',
            'Aktivitas berkebun',
            'Perawatan rumah exterior',
        ]
        recommendations['household']['cautions'] = [
            'Hasil penjemuran tidak maksimal',
            'Monitor perubahan cuaca',
        ]
        recommendations['household']['best_timing'] = 'Sepanjang hari'
        
        # PERBAIKAN
        recommendations['construction']['priority'] = 'normal'
        recommendations['construction']['activities'] = [
            'Semua pekerjaan konstruksi bisa dilakukan',
            'Kondisi nyaman untuk kerja lapangan',
            'Tidak terlalu panas untuk intensitas tinggi',
        ]
        recommendations['construction']['cautions'] = [
            'Monitor cuaca jika ada pekerjaan yang sensitif air',
        ]
        recommendations['construction']['best_timing'] = 'Sepanjang hari'
        
        # PETERNAKAN
        recommendations['animal_care']['priority'] = 'normal'
        recommendations['animal_care']['activities'] = [
            'Semua aktivitas peternakan normal',
            'Kondisi nyaman untuk hewan ternak',
            'Olahraga hewan optimal (tidak terlalu panas)',
        ]
        recommendations['animal_care']['cautions'] = [
            'Monitor perubahan cuaka secara berkala',
        ]
        recommendations['animal_care']['best_timing'] = 'Sepanjang hari'
        
        return recommendations
    
    # ===== KABUT / MIST / FOG =====
    elif 'mist' in condition or 'fog' in description or 'haze' in description:
        # PERTANIAN
        recommendations['agriculture']['priority'] = 'warning'
        recommendations['agriculture']['activities'] = [
            'Kerja lapangan dengan hati-hati (visibilitas rendah)',
            'Pemberian pupuk/obat tanaman (terukur)',
            'Pengecekan sistem irigasi',
            'Perawatan tanaman yang tidak butuh cahaya langsung',
            'Panen sayuran daun (cocok dengan kelembapan tinggi)',
        ]
        recommendations['agriculture']['cautions'] = [
            'Visibilitas rendah - hati-hati saat berkendara',
            'Kelembapan tinggi - waspada penyakit tanaman',
            'Monitor perubahan cuaca mendadak',
        ]
        recommendations['agriculture']['best_timing'] = 'Saat kabut mulai terangkat (pagi terlambat/siang)'
        
        # OLAHRAGA
        recommendations['sports']['priority'] = 'warning'
        recommendations['sports']['activities'] = [
            'Aktivitas indoor lebih disarankan',
            'Jogging di area terbuka dengan hati-hati',
            'Latihan dengan intensitas rendah',
            'Cycling pada rute familiar saja',
        ]
        recommendations['sports']['cautions'] = [
            'Visibilitas rendah - risiko kecelakaan',
            'Gunakan pakaian berwarna cerah',
            'Hindari jalan berlebih lalu lintas',
        ]
        recommendations['sports']['best_timing'] = 'Setelah kabut terangkat (siang/sore)'
        
        # PEKERJAAN RUMAH
        recommendations['household']['priority'] = 'normal'
        recommendations['household']['activities'] = [
            'Pekerjaan rumah tangga biasa',
            'Penjemuran pakaian (hasil tidak optimal)',
            'Belajar dan pekerjaan indoor',
            'Pembersihan rumah',
            'Perawatan taman indoor',
        ]
        recommendations['household']['cautions'] = [
            'Kelembapan tinggi - ventilasi rumah dengan baik',
            'Hasil penjemuran kurang baik',
        ]
        recommendations['household']['best_timing'] = 'Siang hari setelah kabut terangkat'
        
        # PERBAIKAN
        recommendations['construction']['priority'] = 'warning'
        recommendations['construction']['activities'] = [
            'Pekerjaan interior finishing',
            'Perbaikan plumbing dan listrik',
            'Pekerjaan yang tidak sensitif kelembapan',
        ]
        recommendations['construction']['cautions'] = [
            'Hindari pekerjaan exterior (visibilitas rendah)',
            'Material dapat menyerap kelembapan',
            'Pengeringan material butuh waktu lebih lama',
        ]
        recommendations['construction']['best_timing'] = 'Interior saja, tunggu siang hari'
        
        # PETERNAKAN
        recommendations['animal_care']['priority'] = 'normal'
        recommendations['animal_care']['activities'] = [
            'Pemberian pakan dan air minum normal',
            'Pembersihan kandang',
            'Pengecekan kesehatan hewan',
            'Persiapan kandang yang lebih ventilasi',
        ]
        recommendations['animal_care']['cautions'] = [
            'Kelembapan tinggi - risiko penyakit hewan',
            'Ventilasi kandang harus optimal',
            'Hindari memindahkan hewan ke area basah',
        ]
        recommendations['animal_care']['best_timing'] = 'Pagi dan sore'
        
        return recommendations
    
    # ===== SALJU / SNOW - JARANG DI INDONESIA =====
    elif 'snow' in condition or 'snow' in description:
        # Kondisi ekstrem - semua aktivitas outdoor dibatasi
        for cat in recommendations.values():
            cat['priority'] = 'danger'
            cat['activities'] = ['⚠️ Aktivitas outdoor sangat terbatas/berbahaya']
            cat['cautions'] = [
                'JARANG TERJADI di Indonesia',
                'Berbahaya untuk semua aktivitas outdoor',
                'Tetap di dalam rumah',
            ]
        return recommendations
    
    # ===== HOT & DRY CONDITIONS (SUHU TINGGI, KELEMBAPAN RENDAH) =====
    if temperature > 35 and humidity < 40:
        recommendations['agriculture']['priority'] = 'warning'
        if not recommendations['agriculture']['activities']:
            recommendations['agriculture']['activities'] = [
                'Penyiraman intensif pagi dan sore',
                'Hindari kerja saat siang terik (11:00-14:00)',
                'Mulsa tanaman untuk retensi air',
                'Pengecekan status kesehatan tanaman',
            ]
        if not recommendations['agriculture']['cautions']:
            recommendations['agriculture']['cautions'] = [
                f'⚠️ SUHU SANGAT TINGGI ({temperature}°C) - heat stress risk',
                f'Kelembapan sangat rendah ({humidity}%) - tanah cepat kering',
                'Risiko kebakaran - pastikan area aman',
            ]
        recommendations['agriculture']['best_timing'] = 'Pagi pukul 5-8 atau sore 16-18'
    
    # ===== VERY HIGH HUMIDITY (KELEMBAPAN SANGAT TINGGI) =====
    if humidity > 85 and 'rain' not in condition:
        recommendations['agriculture']['priority'] = 'warning'
        if not recommendations['agriculture']['cautions']:
            recommendations['agriculture']['cautions'] = []
        recommendations['agriculture']['cautions'].append(
            f'🍄 Kelembapan SANGAT TINGGI ({humidity}%) - risiko jamur & penyakit tanaman'
        )
        if not recommendations['agriculture']['activities']:
            recommendations['agriculture']['activities'] = [
                'TINGKATKAN ventilasi di sekitar tanaman',
                'Kurangi frekuensi penyiraman',
                'Buang daun yang terinfeksi',
                'Aplikasi fungisida preventif',
            ]
    
    # ===== STRONG WIND (ANGIN KENCANG) =====
    if wind_speed >= 10:
        for key in ['agriculture', 'construction', 'animal_care']:
            if recommendations[key]['priority'] not in ['danger', 'warning']:
                recommendations[key]['priority'] = 'warning'
            if not recommendations[key]['cautions']:
                recommendations[key]['cautions'] = []
            recommendations[key]['cautions'].insert(0,
                f'🌬️ ANGIN KENCANG ({wind_speed} m/s) - potensi kerusakan'
            )
        
        if not recommendations['agriculture']['activities']:
            recommendations['agriculture']['activities'] = [
                'Amankan tanaman yang mudah terbang',
                'Periksa ikatan tanaman (terutama pohon muda)',
                'Tunda penyemprotan pestisida',
                'Persiapkan perlindungan untuk tanaman sensitif',
            ]
        
        if not recommendations['construction']['cautions']:
            recommendations['construction']['cautions'] = []
        recommendations['construction']['cautions'].insert(0,
            f'HINDARI pekerjaan tinggi (angin {wind_speed} m/s berbahaya)'
        )
    
    return recommendations


def rekomendasi(request):
    """
    View halaman rekomendasi aktivitas detail
    Menampilkan rekomendasi untuk berbagai kategori aktivitas
    """
    # Ambil data cuaca
    api_data = get_weather_data()
    weather_data = parse_weather_data(api_data)
    
    # Ambil rekomendasi detail
    detailed_recommendations = get_detailed_recommendations(weather_data)
    
    # Cek warning
    weather_warning = check_weather_warnings(weather_data)
    
    # Context
    context = {
        'weather': weather_data,
        'recommendations': detailed_recommendations,
        'weather_warning': weather_warning,
        'has_warning': weather_warning.get('has_warning', False),
    }
    
    return render(request, 'rekomendasi.html', context)


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
