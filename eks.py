import requests
import json
import random
import time

# --- KONFIGURASI ---
# Cookie (dapat diubah jika kedaluwarsa)
# PASTIKAN COOKIE ANDA YANG TERBARU DAN VALID
VNSHARE_COOKIE = 'cf_clearance=99PwEcEEF2eiC7lQJRgNvO85I0uS7oPda5YWzSxiny4-1751052813-1.2.1.1-bdEzbiHz6YXxHV0uCzVhJ2InE6LclVnOJGm6ByKEUO9Mz2wyFPP1U77KGkfEVQD5aNZTJazjhwTtkw0JopRddfN6VDxkr8yJes2na9BSfNbH1zA3JqzkDxP8dRlKbnx20unAMTiAHvL1qRB2.1UlWg09fKoSbdlIeETh4UN.JvR.3qSGpWE.2kDh_XMlVqTsTVZMNnvYDoqJxYTrEOxGmNur2VstBHk_3X.sxg_xZy7uRE04CQ7F5G_xoczVfkEcWU0wAIif4I.J6Er97PJoLcgLVfGDz1OoGghhMdMOnTyrqoZVOJ9y.05dfrVuEKbQLxE35pxwl3gmHpSBr9USgjeuOuM79X4Fb1wYMj8HPMPnsHvJU0iL5sZkV61lgIRM'

# Konfigurasi Notifikasi Telegram
TELEGRAM_BOT_TOKEN = "8108942782:AAG_Bm3Olvx3VrvPVsPjtpPIFpBLTdfWlhw"
TELEGRAM_CHAT_ID = "932518771"

# Jeda waktu (dalam detik) antara setiap pembuatan akun
DELAY_SECONDS = 60
# --------------------

def generate_username():
    """Menghasilkan username dengan format 'ipul' diikuti angka random 5 digit."""
    return f"ipul{random.randint(10000, 99999)}"

def get_auth_token():
    """Mendapatkan token otentikasi dari ilovepariz.net."""
    url = 'https://ilovepariz.net/api/login'
    headers = {'authority': 'ilovepariz.net', 'accept': '*/*', 'content-type': 'application/json', 'origin': 'https://ilovepariz.net', 'referer': 'https://ilovepariz.net/', 'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Pixel C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Safari/537.36 EdgA/45.03.4.4955'}
    print("1. Meminta token otentikasi...")
    try:
        response = requests.post(url, headers=headers, json={}, timeout=10)
        response.raise_for_status()
        token = response.json().get('token')
        print("   -> Token berhasil didapatkan.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"   -> GAGAL: {e}")
        return None

def get_activation_code(token):
    """Mendapatkan kode aktivasi menggunakan token otentikasi."""
    if not token: return None
    url = 'https://ilovepariz.net/api/code'
    headers = {'authority': 'ilovepariz.net', 'accept': '*/*', 'authorization': f'Bearer {token}', 'referer': 'https://ilovepariz.net/', 'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Pixel C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Safari/537.36 EdgA/45.03.4.4955'}
    print("2. Meminta kode aktivasi...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        code = response.json().get('code')
        print(f"   -> Kode aktivasi berhasil didapatkan: {code}")
        return code
    except requests.exceptions.RequestException as e:
        print(f"   -> GAGAL: {e}")
        return None

def create_account(code):
    """Membuat akun di vnshare.top menggunakan kode aktivasi."""
    if not code: return None
    url = 'https://vnshare.top/getOffice'
    headers = {'authority': 'vnshare.top', 'accept': '*/*', 'content-type': 'text/plain;charset=UTF-8', 'cookie': VNSHARE_COOKIE, 'origin': 'https://vnshare.top', 'referer': 'https://vnshare.top/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
    username = generate_username()
    payload = {"subscription": "314c4481-f395-4525-be8b-2ec4bb1e9d91", "email": {"username": username, "domain": "mail.dangminhhoa.edu.vn"}, "code": code}
    print(f"3. Mencoba membuat akun dengan username '{username}'...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            print("   -> SUKSES: Akun berhasil dibuat!")
            return result.get('account')
        else:
            print(f"   -> GAGAL: {result.get('msg', 'Tidak ada pesan error dari server')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   -> GAGAL: {e}")
        return None

# --- FUNGSI YANG DIMODIFIKASI ---
def send_to_telegram(message):
    """Mengirim pesan notifikasi ke Telegram dengan mekanisme coba lagi (retry)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("   -> Variabel Telegram tidak diatur. Melewatkan notifikasi.")
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    
    max_retries = 3
    retry_delay = 5  # detik

    print("4. Mengirim notifikasi ke Telegram...")
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            if response.json().get('ok'):
                print("   -> Notifikasi berhasil dikirim.")
                return  # Keluar dari fungsi jika berhasil
            else:
                print(f"   -> Gagal mengirim notifikasi (Percobaan {attempt + 1}/{max_retries}): {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   -> Gagal (Percobaan {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            print(f"   -> Mencoba lagi dalam {retry_delay} detik...")
            time.sleep(retry_delay)

    print("   -> GAGAL TOTAL: Notifikasi tidak dapat dikirim setelah beberapa kali percobaan.")
# -----------------------------

if __name__ == '__main__':
    print("========================================")
    print("     Account Creator Snutzzzze      ")
    print("========================================")
    try:
        jumlah_akun = int(input("Masukkan jumlah akun yang ingin dibuat: "))
        if jumlah_akun <= 0:
            print("Jumlah harus lebih dari nol."); exit()
    except ValueError:
        print("Input tidak valid. Harap masukkan angka."); exit()

    print(f"\nMemulai proses pembuatan {jumlah_akun} akun...\n")
    sukses_count = 0
    saved_activation_code = None  # Variabel untuk menyimpan kode jika pembuatan akun gagal

    for i in range(jumlah_akun):
        print(f"========================================")
        print(f"      PERCOBAAN AKUN #{i + 1} dari {jumlah_akun}      ")
        print(f"========================================\n")

        activation_code = None

        if saved_activation_code:
            print(f"[*] Menggunakan kode yang tersimpan dari percobaan sebelumnya: {saved_activation_code}")
            activation_code = saved_activation_code
            saved_activation_code = None # Hapus setelah digunakan lagi
        else:
            auth_token = get_auth_token()
            if auth_token:
                activation_code = get_activation_code(auth_token)

        if not activation_code:
            print("--> Gagal mendapatkan kode aktivasi. Lanjut ke percobaan berikutnya.\n")
            if i < jumlah_akun - 1:
                print(f"\nJeda {DELAY_SECONDS} detik sebelum lanjut...")
                time.sleep(DELAY_SECONDS)
                print("\n")
            continue
        
        new_account = create_account(activation_code)

        if new_account:
            sukses_count += 1
            telegram_message = (
                "<b>✅ Akun Baru Berhasil Dibuat</b>\n\n"
                f"<b>#️⃣ Urutan:</b> {sukses_count}/{jumlah_akun}\n\n"
                f"📧 <b>Email:</b> <code>{new_account.get('email')}</code>\n"
                f"🔑 <b>Password:</b> <code>{new_account.get('password')}</code>\n\n"
                "<i>Script by ipulSnutz</i>"
            )
            send_to_telegram(telegram_message)
        else:
            print(f"--> GAGAL membuat akun. Menyimpan kode '{activation_code}' untuk percobaan selanjutnya.")
            saved_activation_code = activation_code  # Simpan kode untuk iterasi berikutnya

        if i < jumlah_akun - 1:
            print(f"\nJeda {DELAY_SECONDS} detik sebelum lanjut...")
            time.sleep(DELAY_SECONDS)
            print("\n")

    print(f"\n========================================")
    print(f"              PROSES SELESAI              ")
    print(f"   Berhasil dibuat: {sukses_count} dari {jumlah_akun} percobaan   ")
    print(f"         Script by Saipul Bahri         ")
    print(f"========================================")
