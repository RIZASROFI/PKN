# 🌤️ E-CUACA - Website Monitoring Cuaca Real-Time

## 📋 Deskripsi Proyek

**E-Cuaca** adalah website monitoring cuaca real-time yang dibangun khusus untuk **KKN (Kuliah Kerja Nyata)** di **Desa Sumberejo, Kecamatan Pagelaran, Kabupaten Pringsewu, Lampung**.

Website ini menampilkan informasi cuaca terkini dengan desain modern, responsif, dan mudah digunakan oleh masyarakat desa.

### ✨ Fitur Utama

- ✅ **Real-Time Weather Data** - Data cuaca diperbarui setiap kali halaman dimuat
- ✅ **Tanpa Database** - Sesuai dengan requirement KKN (tidak menyimpan data)
- ✅ **Responsive Design** - Sempurna untuk mobile, tablet, dan desktop
- ✅ **Modern UI** - Menggunakan Flexbox & CSS Grid
- ✅ **Informasi Lengkap**:
  - Suhu (°C)
  - Kelembaban (%)
  - Kecepatan Angin (m/s)
  - Tekanan Udara (hPa)
  - Visibilitas (km)
  - Tutupan Awan (%)
  - Kondisi Cuaca + Emoji

---

## 🚀 SETUP & INSTALASI

### Prerequisites

Pastikan Anda sudah install:
- **Python 3.8+** → [Download](https://www.python.org/downloads/)
- **pip** (biasanya sudah included dengan Python)
- **Git** (optional, untuk version control)

### Step 1: Clone/Download Project

Jika sudah ter-setup folder `ecuana`, masuk ke folder tersebut:

```powershell
cd "e:\Semester 6\Project PKN\ecuana"
```

### Step 2: Setup Virtual Environment

```powershell
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# Jika ada error "execution policy", jalankan:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Setelah aktif, command prompt akan menunjukkan prefix `(venv)`.

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

Atau manual:
```powershell
pip install Django==4.2.8
pip install requests==2.31.0
```

### Step 4: Verify Django Installation

```powershell
python manage.py --version
```

---

## 📌 SETUP API OpenWeatherMap

### Cara Mendapatkan API Key:

1. **Buka** → https://openweathermap.org/api
2. **Klik** → "Sign Up" → Buat akun gratis
3. **Login** → Ke dashboard Anda
4. **Buka** → "API keys" tab
5. **Copy** → Default API Key Anda
6. **Edit file** → `cuaca/views.py`
7. **Cari** → `OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE'`
8. **Ganti** → `OPENWEATHER_API_KEY = 'your_actual_api_key_here'`

### Contoh:
```python
# Sebelum:
OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE'

# Sesudah:
OPENWEATHER_API_KEY = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
```

⚠️ **PENTING**: Jangan share API key Anda ke publik!

---

## ▶️ MENJALANKAN WEBSITE

### Terminal 1: Aktifkan Virtual Environment

```powershell
cd "e:\Semester 6\Project PKN\ecuana"
.\venv\Scripts\Activate.ps1
```

### Terminal 2: Jalankan Development Server

```powershell
python manage.py runserver
```

Output akan seperti ini:

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Akses Website:

Buka browser Anda dan pergi ke:
- **Main Page**: http://127.0.0.1:8000/
- **Debug Page**: http://127.0.0.1:8000/debug/

---

## 📁 Struktur File & Penjelasan

```
ecuana/
├── ecuana/                 # Folder config project Django
│   ├── settings.py        # ⚙️ Konfigurasi Django
│   ├── urls.py            # 🔗 Routing halaman utama
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
├── cuaca/                  # 🌤️ Folder app "cuaca"
│   ├── views.py           # 📄 Fungsi view & API request
│   ├── urls.py            # 🔗 Routing untuk app
│   ├── apps.py            # ⚙️ Konfigurasi app
│   ├── migrations/        # Database migrations (unused)
│   ├── __init__.py
│   └── tests.py
│
├── templates/              # 🎨 Folder HTML files
│   └── index.html         # 📄 Halaman utama
│
├── static/                 # 📦 Static assets
│   ├── css/
│   │   └── style.css      # 🎨 Stylesheet (Flexbox & Grid)
│   └── js/                # (Placeholder untuk JS future)
│
├── manage.py              # 🔧 Django management script
├── requirements.txt       # 📋 List dependencies
└── README.md              # 📖 Dokumentasi ini
```

---

## 📄 Penjelasan File-File Penting

### 1. **ecuana/settings.py** ⚙️

File konfigurasi Django. Berisi:
- `INSTALLED_APPS` - List app yang aktif (hanya `cuaca`)
- `TEMPLATES` - Konfigurasi folder templates
- `STATIC_URL` - Path ke static files (CSS, JS)
- `LANGUAGE_CODE` - Bahasa (id-ID untuk Indonesia)
- `TIME_ZONE` - Zona waktu (Asia/Jakarta)

**TIDAK ADA DATABASE CONFIGURATION** ✅

### 2. **cuaca/views.py** 📄

File utama yang berisi:
- `get_weather_data()` - Fungsi untuk request ke OpenWeatherMap API
- `parse_weather_data()` - Fungsi untuk parse response API ke format user-friendly
- `index()` - View function untuk halaman utama
- `debug_api()` - View untuk debugging API response

**Alur:**
1. User akses `/` → View `index()` dipanggil
2. `index()` memanggil `get_weather_data()` → Request ke API
3. Response di-parse oleh `parse_weather_data()`
4. Data dikirim ke template `index.html` sebagai `context`

### 3. **templates/index.html** 🎨

HTML Template dengan:
- **Location Info** - Menampilkan nama desa & lokasi
- **Weather Main Card** - Menampilkan suhu & kondisi cuaca besar
- **Weather Grid** - 6 stat card (kelembaban, angin, tekanan, dll)
- **Update Info** - Waktu update terakhir
- **Error Handling** - Tampilan jika API error

Template menggunakan **Django Template Tags**:
```html
{{ variable }}          # Tampilkan variable
{% if condition %}      # Conditional
{% for item in list %}  # Loop
```

### 4. **static/css/style.css** 🎨

CSS dengan fitur:
- **CSS Variables** - Untuk warna, spacing, font
- **Flexbox Layout** - Untuk header, main card
- **CSS Grid** - Untuk weather grid (responsive)
- **Animations** - Slide, fade, float effects
- **Responsive Design**:
  - Mobile (< 600px)
  - Tablet (768px - 1024px)
  - Desktop (1024px+)
- **Dark Mode Support** - Automatic detection
- **Media Queries** - Untuk different screen sizes

---

## 🔧 Troubleshooting

### ❌ Error: `ModuleNotFoundError: No module named 'requests'`

**Solusi:**
```powershell
pip install requests
```

### ❌ Error: `No module named 'django'`

**Solusi:**
```powershell
pip install Django
```

### ❌ Error: `Failed to connect to API`

**Kemungkinan penyebab:**
1. ✗ Internet tidak terhubung
2. ✗ API key salah/belum diganti
3. ✗ API key belum di-approve OpenWeatherMap

**Solusi:**
1. Periksa koneksi internet
2. Periksa kembali API key di `cuaca/views.py`
3. Tunggu 10 menit setelah daftar (API key OpenWeatherMap butuh waktu aktif)

### ❌ Error: `TemplateDoesNotExist at /`

**Solusi:**
- Pastikan folder `templates/` ada di level yang sama dengan `manage.py`
- Pastikan file `templates/index.html` ada

### ❌ Virtual Environment tidak aktif

**Ciri-ciri:**
- Tidak ada prefix `(venv)` di command prompt
- `pip list` menunjukkan packages dari global Python

**Solusi:**
```powershell
.\venv\Scripts\Activate.ps1
```

Jika masih error, cek execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📊 Response API Format

Contoh response dari OpenWeatherMap API yang di-parse:

```python
{
    'location_name': 'Desa Sumberejo, Kecamatan Pagelaran',
    'location_full': 'Desa Sumberejo, Kecamatan Pagelaran, Kabupaten Pringsewu, Lampung, Indonesia',
    'temperature': 28,              # Suhu saat ini
    'feels_like': 32,               # Suhu terasa
    'humidity': 75,                 # Kelembaban %
    'pressure': 1013,               # Tekanan udara hPa
    'condition': 'Partly cloudy',   # Kondisi cuaca
    'description': 'overcast clouds',
    'wind_speed': 5.2,              # Kecepatan angin m/s
    'wind_degree': 180,             # Arah angin derajat
    'cloudiness': 65,               # Tutupan awan %
    'visibility': 10.0,             # Visibilitas km
    'temperature_min': 26,
    'temperature_max': 31,
    'weather_emoji': '🌤️',
    'update_time': '22 Januari 2026, 14:30 WIB',
    'error': None
}
```

---

## 🌍 Lokasi Monitoring

**Desa:** Sumberejo  
**Kecamatan:** Pagelaran  
**Kabupaten:** Pringsewu  
**Provinsi:** Lampung, Indonesia  

**Koordinat:**
- Latitude: -5.3667
- Longitude: 104.9833

Koordinat dapat diubah di `cuaca/views.py`:
```python
LOCATION = {
    'latitude': -5.3667,
    'longitude': 104.9833,
}
```

---

## 📱 QR Code Integration

Untuk membuat QR Code yang mengarah ke website:

1. Akses → https://qr-server.com/
2. Input URL → `http://127.0.0.1:8000/` (untuk local)
3. Atau input URL public jika sudah di-deploy

Untuk production, ganti dengan URL domain/IP publik yang actual.

---

## ✅ Checklist Setup

Sebelum submit ke dosen, pastikan:

- [ ] Virtual environment sudah setup
- [ ] Django & requests sudah install
- [ ] API key OpenWeatherMap sudah dimasukkan
- [ ] Folder `templates/`, `static/`, `cuaca/` sudah ada
- [ ] File `settings.py`, `views.py`, `index.html`, `style.css` sudah lengkap
- [ ] Tidak ada database (sesuai requirement)
- [ ] Website bisa diakses di `http://127.0.0.1:8000/`
- [ ] Data cuaca tampil dengan benar
- [ ] Desain responsive (coba resize browser)
- [ ] Tidak ada error di console/terminal

---

## 📚 Resources & References

- [Django Documentation](https://docs.djangoproject.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [MDN Web Docs - CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/)
- [MDN Web Docs - HTML](https://developer.mozilla.org/en-US/docs/Web/HTML/)
- [Python Requests Library](https://requests.readthedocs.io/)

---

## 🎓 KKN Project Information

**Program:** Kuliah Kerja Nyata (KKN)  
**Lokasi:** Desa Sumberejo, Kecamatan Pagelaran, Kabupaten Pringsewu  
**Tahun:** 2026  
**Tema:** Teknologi Informasi untuk Masyarakat Desa  

Semoga website ini memberikan manfaat bagi masyarakat Desa Sumberejo! 🌾

---

**Selamat menggunakan E-Cuaca! 🌤️**
