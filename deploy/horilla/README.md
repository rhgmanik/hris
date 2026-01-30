# Deploy (Bare Metal)

Dokumen ini untuk instalasi Horilla di bare metal dengan Gunicorn + Nginx, dan (opsional) addon PPh21.

## 1) Konsep

- Horilla di-clone dari repo upstream.
- Addon PPh21 diinstall via wheel/pip ke virtualenv yang sama.
- Aktivasi addon per-klien lewat env `ENABLE_PPH21_PLUGIN=True`.

## 2) Provision Script

Script: `deploy/horilla_provision.sh`

Contoh:

```bash
sudo bash deploy/horilla_provision.sh \
  --client client1 \
  --domain client1.example.com \
  --internal-port 8001 \
  --ssl letsencrypt \
  --letsencrypt-email admin@example.com \
  --db-name horilla_client1 \
  --db-user horilla \
  --db-password 'CHANGE_ME' \
  --db-host 127.0.0.1 \
  --db-port 5432 \
  --enable-pph21 \
  --pph21-wheel /opt/addons/horilla_pph21_addon-0.1.0-py3-none-any.whl
```

Yang script lakukan:

- cek dependency (python3, pip, git, nginx, systemctl; certbot bila SSL enabled)
- clone/pull Horilla ke `/opt/horilla/<client>/app`
- buat venv `/opt/horilla/<client>/venv`
- install requirements Horilla
- (opsional) install wheel PPh21
- generate `.env` instance (DB, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DB_INIT_PASSWORD, ENABLE_PPH21_PLUGIN)
- generate helper script `manage.sh` untuk menjalankan `manage.py` dengan env+venv yang benar
- generate `horilla/local_settings.py` untuk:
  - load `horilla_apps` sejak awal (INSTALLED_APPS lengkap)
  - apply hardening production saat DEBUG=False (secure cookies, HSTS, proxy ssl header)
- auto-generate migrations untuk app lokal yang folder `migrations/` masih kosong (hanya `__init__.py`)
  - output ditulis ke `local_migrations/<app>/` (bukan ke folder app) supaya tidak mengotori source upstream
- migrate + collectstatic + compilemessages
- buat systemd service Gunicorn
- buat Nginx site config
- (opsional) request SSL Let's Encrypt via certbot

## 2.1) Catatan Cloudflare Tunnel

Jika domain kamu dipublish lewat **Cloudflare Tunnel** (mis. `hr.tahok.my.id`) dan origin tidak membuka port 80/443 publik, gunakan:

- `--ssl cloudflare` (tanpa certbot/Let's Encrypt)

Alasannya:

- TLS sudah terminasi di Cloudflare edge, origin menerima HTTP dari `cloudflared`.
- Django tetap perlu tahu request itu “secure” supaya cookie secure dan redirect bekerja benar.

Contoh:

```bash
sudo bash deploy/horilla_provision.sh \
  --client hr \
  --domain hr.tahok.my.id \
  --internal-port 8001 \
  --ssl cloudflare \
  --db-name horilla_hr \
  --db-user horilla \
  --db-password 'CHANGE_ME' \
  --db-host 127.0.0.1 \
  --db-port 5432
```

Konfigurasi Tunnel (di host cloudflared):

- Public hostname: `hr.tahok.my.id`
- Service: `http://localhost` (atau `http://127.0.0.1:80`)

## 3) Update SOP

- Update Horilla:
  - `git pull` di folder `app`
  - `pip install -r requirements.txt` bila berubah
  - jalankan migrasi:
    - `DJANGO_SETTINGS_MODULE=horilla.local_settings python manage.py migrate`
  - restart service
- Update addon:
  - `pip install --upgrade <wheel/registry>`
  - apply PPh21:
    - `DJANGO_SETTINGS_MODULE=horilla.local_settings python manage.py pph21_install_policy --all-companies --force`
  - restart service
