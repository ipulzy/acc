import requests
from bs4 import BeautifulSoup
import getpass
import re
import time

# Header yang lebih lengkap untuk meniru browser
BASE_HEADERS = {
    'authority': 'tmtunnels.id',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://tmtunnels.id',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

def login(session, username, password):
    """Fungsi untuk melakukan login ke situs."""
    login_url = "https://tmtunnels.id/login.php"
    payload = {'username': username, 'password': password}
    headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/login.php", "Content-Type": "application/x-www-form-urlencoded"}
    try:
        print(f"🔒 Mencoba login dengan username: {username}...")
        response = session.post(login_url, headers=headers, data=payload)
        response.raise_for_status()
        if 'Login Success' in response.text:
            print("✅ Login Berhasil!")
            return True
        else:
            print("❌ Login Gagal! Periksa kembali username dan password Anda.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error saat koneksi untuk login: {e}")
        return False

def cek_dan_tampilkan_data_vpn(session):
    """Memeriksa dan menampilkan detail VPN."""
    data_url = "https://tmtunnels.id/data"
    headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/dashboard"}
    print("\n🔄 Mengambil data VPN aktif...")
    try:
        response = session.get(data_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        vpn_cards = soup.find_all('div', class_='card-body')
        if not vpn_cards:
            print("Tidak ada informasi VPN aktif yang ditemukan."); return []
        active_accounts = []
        print("\n" + "=".center(43, "="))
        print(" DETAIL VPN AKTIF ".center(43, " "))
        print("=".center(43, "="))
        for i, card in enumerate(vpn_cards, 1):
            try:
                title_elem = card.find('h5', class_='card-title')
                username_vpn = title_elem.find(string=True, recursive=False).strip()
                detail_button = card.find('span', class_='detailInfo')
                idremark = detail_button['data-idremark'] if detail_button else None
                if not idremark: continue
                all_p_tags = card.find_all('p', class_='card-text')
                exp_text = next((p.text.replace("Exp:", "").strip() for p in all_p_tags if "Exp:" in p.text), "N/A")
                usage_text = next((p.text.replace("Usage:", "").strip() for p in all_p_tags if "Usage:" in p.text), "N/A")
                print(f"\n{i}. Nama Pengguna : {username_vpn}")
                print(f"   ├─ Masa Aktif  : {exp_text}")
                print(f"   └─ Pemakaian   : {usage_text}")
                active_accounts.append({'index': i, 'username': username_vpn, 'idremark': idremark})
            except AttributeError: pass
        print("\n" + "="*43)
        return active_accounts
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil data dari server: {e}"); return []

def renew_account(session, idremark, username):
    """Fungsi untuk memperpanjang akun."""
    print(f"\n🚀 Memulai proses renew untuk akun: {username}...")
    try:
        renew_quote_url = "https://tmtunnels.id/renewquote.php"
        headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/data", "X-Requested-With": "XMLHttpRequest", "accept": "*/*"}
        quote_resp = session.post(renew_quote_url, headers=headers, data={'idremark': idremark})
        soup = BeautifulSoup(quote_resp.text, 'html.parser')
        idsoal_tag = soup.find('input', {'name': 'idsoal'})
        answer_tag = soup.find('input', {'name': 'answerTrue'})
        if not idsoal_tag or 'value' not in idsoal_tag.attrs or not answer_tag or 'value' not in answer_tag.attrs:
            print("❌ Gagal mendapatkan pertanyaan untuk renew."); return
        idsoal, answer = idsoal_tag['value'], answer_tag['value']
        print(f"✔️ Mendapatkan pertanyaan renew. Menjawab secara otomatis...")
        renew_url = "https://tmtunnels.id/renew.php"
        renew_payload = {'answer': answer, 'answerTrue': answer, 'idsoal': idsoal, 'idremark': idremark}
        session.post(renew_url, headers={**BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}, data=renew_payload)
        verify_url = f"https://tmtunnels.id/data?renew={username}"
        verify_resp = session.get(verify_url, headers={**BASE_HEADERS, "Referer": "https://tmtunnels.id/data"})
        if "Successfully</h5>" in verify_resp.text: print(f"✅ Akun '{username}' berhasil diperpanjang!")
        else: print(f"❌ Gagal memperpanjang akun '{username}'.")
    except Exception as e: print(f"Terjadi kesalahan selama proses renew: {e}")

def get_config(session, idremark):
    """Fungsi untuk mengambil detail konfigurasi VPN."""
    print(f"\n📄 Mengambil konfigurasi untuk ID Remark: {idremark}...")
    detail_url = "https://tmtunnels.id/detail.php"
    headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/data", "X-Requested-With": "XMLHttpRequest", "accept": "*/*"}
    try:
        response = session.post(detail_url, headers=headers, data={'idremark': idremark})
        get_config_from_html(response.text)
    except Exception as e: print(f"Gagal mengambil konfigurasi: {e}")

def delete_account(session, idremark, username):
    """Fungsi untuk menghapus akun VPN."""
    print(f"\n🔥 Memulai proses delete untuk akun: {username}...")
    try:
        delete_quote_url = "https://tmtunnels.id/deletequote.php"
        quote_headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/data", "X-Requested-With": "XMLHttpRequest", "accept": "*/*"}
        session.post(delete_quote_url, headers=quote_headers, data={'idremark': idremark}).raise_for_status()
        print("✔️ Validasi sesi OK.")
        delete_url = f"https://tmtunnels.id/delete.php?idremark={idremark}"
        delete_headers = {**BASE_HEADERS, "Referer": "https://tmtunnels.id/data"}
        delete_response = session.get(delete_url, headers=delete_headers)
        delete_response.raise_for_status()
        print("✔️ Perintah delete terkirim, memverifikasi hasil...")
        soup = BeautifulSoup(delete_response.text, 'html.parser')
        success_message = soup.find('h5', string=re.compile(f"Delete {re.escape(username)} Successfully", re.IGNORECASE))
        if success_message:
            print(f"✅ Akun '{username}' berhasil dihapus!")
        else:
            print(f"❌ Gagal menghapus akun '{username}'.")
            alert = soup.find('div', class_=re.compile(r'alert-'))
            if alert: print(f"   Pesan dari server: {alert.text.strip()}")
            else: print("   Server tidak memberikan pesan sukses atau error yang spesifik.")
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan koneksi selama proses delete: {e}")
    except Exception as e:
        print(f"Terjadi kesalahan yang tidak terduga selama proses delete: {e}")

def create_account(session, logged_in_username):
    """Fungsi untuk membuat akun VPN baru dengan menu pilihan nomor."""
    create_url = "https://tmtunnels.id/create"
    quiz_url = "https://tmtunnels.id/quiz.php"
    send_url = "https://tmtunnels.id/send.php"
    try:
        print("\n🛠️  Mengambil opsi pembuatan akun...")
        create_page = session.get(create_url, headers={**BASE_HEADERS, "Referer": "https://tmtunnels.id/dashboard"})
        soup = BeautifulSoup(create_page.text, 'html.parser')
        
        server_list = [{'code': opt['value'], 'name': opt.text.strip()} for opt in soup.select('select[name="serv"] option') if opt.has_attr('value') and opt['value']]
        if not server_list:
            print("❌ Gagal mendapatkan daftar server yang valid."); return

        print("\n┌─ Pilihan Server " + "─"*25 + "┐")
        for i, server in enumerate(server_list, 1):
            print(f"│ {i}. {server['name']:<35} │")
        print("└" + "─"*41 + "┘")
        try:
            server_num = int(input(f"│ Masukkan nomor server (1-{len(server_list)}): "))
            if not 1 <= server_num <= len(server_list):
                print("❌ Nomor server tidak valid."); return
            serv_choice = server_list[server_num - 1]['code']
        except ValueError:
            print("❌ Input tidak valid. Harap masukkan angka."); return

        print("\n┌─ Pilihan Protokol " + "─"*23 + "┐")
        protocol_list = [
            {'code': 'vmess', 'name': 'VMess'},
            {'code': 'vless', 'name': 'VLess'},
            {'code': 'trojan', 'name': 'Trojan'},
        ]
        for i, proto in enumerate(protocol_list, 1):
            print(f"│ {i}. {proto['name']:<35} │")
        print("└" + "─"*41 + "┘")
        try:
            proto_num = int(input(f"│ Masukkan nomor protokol (1-{len(protocol_list)}): "))
            if not 1 <= proto_num <= len(protocol_list):
                print("❌ Nomor protokol tidak valid."); return
            proto_choice = protocol_list[proto_num - 1]['code']
        except ValueError:
            print("❌ Input tidak valid. Harap masukkan angka."); return
            
        remark = input("│ Masukkan nama (remark) untuk akun baru: ")

        print("\n✔️ Mengambil pertanyaan (captcha)...")
        quiz_headers = {**BASE_HEADERS, "Referer": create_url, "X-Requested-With": "XMLHttpRequest", "accept": "*/*", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        quiz_payload = {'username': logged_in_username, 'proto': proto_choice, 'serv': serv_choice, 'remark': remark}
        quiz_resp = session.post(quiz_url, headers=quiz_headers, data=quiz_payload)
        quiz_soup = BeautifulSoup(quiz_resp.text, 'html.parser')
        
        try:
            idsoal = quiz_soup.find('input', {'name': 'idsoal'})['value']
            answer = quiz_soup.find('input', {'name': 'answerTrue'})['value']
        except (TypeError, KeyError):
            print("\n❌ FATAL: Gagal mem-parsing captcha."); return

        final_payload = {'answer': answer, 'username': logged_in_username, 'remark': remark, 'protocol': proto_choice, 'answerTrue': answer, 'idsoal': idsoal, 'serv': serv_choice}
        print("⚙️  Membuat akun, harap tunggu...")
        response = session.post(send_url, headers={**BASE_HEADERS, "Referer": create_url, "Content-Type": "application/x-www-form-urlencoded"}, data=final_payload)
        
        if "Succesfully Create" in response.text:
            print("✅ Akun berhasil dibuat! Menampilkan detail...")
            get_config_from_html(response.text)
        else:
            error_soup = BeautifulSoup(response.text, 'html.parser')
            alert = error_soup.find('div', class_=re.compile(r'alert-'))
            if alert: print(f"❌ Gagal membuat akun: {alert.text.strip()}")
            else: print("❌ Gagal membuat akun. Tidak ada respons yang diharapkan.")
    except Exception as e: print(f"Terjadi kesalahan yang tidak terduga: {e}")

def get_config_from_html(html_text):
    """Fungsi bantuan untuk parsing detail config."""
    soup = BeautifulSoup(html_text, 'html.parser')
    details = {a.get_text(strip=True).split(':', 1)[0].strip(): a.get_text(strip=True).split(':', 1)[1].strip() for a in soup.find_all('a', style="font-size: 14px;") if ':' in a.text}
    textareas = soup.find_all('textarea', class_='form-control')
    print("\n" + "─" * 15 + " DETAIL KONFIGURASI " + "─" * 15)
    for key, value in details.items(): print(f"   - {key:<11}: {value}")
    print("\n" + "─" * 15 + " CONFIG LINKS " + "─" * 15)
    for area in textareas:
        label_tag = area.find_previous('label')
        label = label_tag.text if label_tag else "Config"
        print(f"\n[{label}]\n{area.text.strip()}")
    print("\n" + "─" * 52)

def main_menu():
    """Fungsi utama untuk menampilkan menu."""
    session = requests.Session()
    logged_in, logged_in_user, login_time = False, None, 0
    while True:
        if logged_in and (time.time() - login_time > 3600):
            print("\n" + "="*45 + "\n⌛ Sesi Anda telah berakhir. Silakan login kembali.\n" + "="*45)
            logged_in, logged_in_user = False, None
        
        print("\n" + "+"*43)
        if logged_in:
            status_text = f"👤 Status: Login sebagai '{logged_in_user}'"
            print(f"| {status_text.center(39)} |")
            print("+" + "="*41 + "+")
        
        title = "MENU UTAMA"
        print(f"| {title.center(39)} |")
        print("+" + "-"*41 + "+")
        menu_items = [
            "1. Login ke Akun", "2. Cek Akun VPN Aktif", "3. Renew Akun VPN",
            "4. Ambil Konfigurasi VPN", "5. Delete Akun VPN", "6. Buat Akun VPN", "7. Keluar"
        ]
        for item in menu_items:
            print(f"| {item:<39} |")
        print("+" + "-"*41 + "+")

        pilihan = input("└── Pilihan Anda (1-7): ")
        
        if pilihan == '1':
            user = input("├── Masukkan username: ")
            passwd = getpass.getpass("└── Masukkan password: ")
            is_success = login(session, user, passwd)
            if is_success: logged_in, logged_in_user, login_time = True, user, time.time()
            else: logged_in, logged_in_user = False, None
        elif pilihan == '2':
            if logged_in: cek_dan_tampilkan_data_vpn(session)
            else: print("\n⚠️ Anda harus login terlebih dahulu!")
        elif pilihan in ['3', '4', '5']:
            if not logged_in: print("\n⚠️ Anda harus login terlebih dahulu!"); continue
            active_accounts = cek_dan_tampilkan_data_vpn(session)
            if not active_accounts: continue
            try:
                action_map = {"3": "di-renew", "4": "diambil konfigurasinya", "5": "dihapus"}
                action_word = action_map.get(pilihan)
                num = int(input(f"└── Masukkan nomor akun untuk {action_word}: "))
                acc = next((a for a in active_accounts if a['index'] == num), None)
                if not acc: print("❌ Nomor akun tidak valid."); continue
                if pilihan == '3': renew_account(session, acc['idremark'], acc['username'])
                elif pilihan == '4': get_config(session, acc['idremark'])
                elif pilihan == '5':
                    if input(f"Anda YAKIN ingin menghapus '{acc['username']}'? (y/n): ").lower() == 'y':
                        delete_account(session, acc['idremark'], acc['username'])
                    else: print("Aksi delete dibatalkan.")
            except ValueError: print("❌ Input tidak valid.")
        elif pilihan == '6':
            if logged_in: create_account(session, logged_in_user)
            else: print("\n⚠️ Anda harus login terlebih dahulu!")
        elif pilihan == '7': print("\nTerima kasih! Sampai jumpa. 👋"); break
        else: print("\nPilihan tidak valid.")

if __name__ == "__main__": main_menu()
