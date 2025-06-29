import requests
from bs4 import BeautifulSoup

# --- Konfigurasi ---
# Ganti dengan username dan password Anda jika diperlukan
USERNAME = "ipulsnutz"
PASSWORD = "bangsat31"

# URL target
LOGIN_URL = "http://tmtunnels.id/login.php"
DASHBOARD_URL = "http://tmtunnels.id/dashboard?success"

# --- Headers untuk Request ---
# Header ini meniru browser Firefox di Windows
LOGIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://tmtunnels.id/",
}

DASHBOARD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "http://tmtunnels.id/",
    "Upgrade-Insecure-Requests": "1",
}

# --- Payload untuk Login ---
login_payload = {
    "username": USERNAME,
    "password": PASSWORD
}

# 1. Membuat Session
# Session object akan menyimpan cookies secara otomatis setelah login,
# sehingga kita tetap "ter-autentikasi" untuk request selanjutnya.
session = requests.Session()

try:
    # 2. Melakukan POST Request untuk Login
    print(f"🚀 Mencoba login sebagai '{USERNAME}'...")
    response_login = session.post(LOGIN_URL, headers=LOGIN_HEADERS, data=login_payload)
    response_login.raise_for_status() # Cek jika ada error HTTP (spt 404, 500)

    # 3. Memeriksa Hasil Login
    if "Login Success" in response_login.text:
        print("✅ Login Berhasil!")

        # 4. Mengakses Halaman Dashboard
        print("\n🔄 Mengakses halaman dashboard...")
        response_dashboard = session.get(DASHBOARD_URL, headers=DASHBOARD_HEADERS)
        response_dashboard.raise_for_status()

        # 5. Memverifikasi dan Menampilkan Konten Dashboard
        # Menggunakan BeautifulSoup untuk parsing HTML
        soup = BeautifulSoup(response_dashboard.text, 'html.parser')
        
        # Cari elemen yang menandakan kita berada di dashboard
        dashboard_heading = soup.find('h1', class_='h6', text='Dashboard')
        username_display = soup.find('medium', text='username login')

        if dashboard_heading and username_display:
            print("✅ Berhasil masuk ke Dashboard.")
            print("\n--- Konten Dashboard ---")
            # Menampilkan div yang berisi info dashboard untuk verifikasi
            dashboard_content = soup.find('div', class_='lh-1')
            if dashboard_content:
                print(dashboard_content.get_text(strip=True, separator='\n'))
            else:
                print("Tidak dapat menemukan konten spesifik dashboard.")
            print("------------------------")
        else:
            print("❌ Gagal memverifikasi halaman dashboard. Mungkin dialihkan kembali ke halaman login.")
            print("Response Dashboard:\n", response_dashboard.text)

    elif "Login Failed" in response_login.text:
        print("❌ Login Gagal! Periksa kembali username dan password Anda.")
        # Menampilkan pesan error dari server
        soup = BeautifulSoup(response_login.text, 'html.parser')
        error_div = soup.find('div', class_='alert-danger')
        if error_div:
            print(f"Pesan Server: {error_div.get_text(strip=True)}")

    else:
        print("❓ Respons login tidak dikenali.")
        print("Response Login:\n", response_login.text)

except requests.exceptions.RequestException as e:
    print(f"Terjadi error saat melakukan request: {e}")
