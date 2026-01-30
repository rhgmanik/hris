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
- generate `.env` instance (DB, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, ENABLE_PPH21_PLUGIN)
- migrate + collectstatic + compilemessages
- buat systemd service Gunicorn
- buat Nginx site config
- (opsional) request SSL Let's Encrypt via certbot

## 3) Update SOP

- Update Horilla:
  - `git pull` di folder `app`
  - `pip install -r requirements.txt` bila berubah
  - `python manage.py migrate`
  - restart service
- Update addon:
  - `pip install --upgrade <wheel/registry>`
  - `python manage.py pph21_install_policy --all-companies --force`
  - restart service

