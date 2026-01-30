# Catatan: Instalasi Horilla Baru + Addon PPh21 (horilla-test)

Dokumen ini merangkum langkah yang dipakai untuk membuat instalasi Horilla bersih di folder `horilla-test` dan memasang addon PPh21 dari repo `hris`.

## Lokasi

- Horilla (upstream): `/home/ruben/horillas/horilla-test/app`
- Addon (repo ops): `/home/ruben/horillas/hris/addons/horilla_pph21_addon`

## 1) Clone Horilla upstream

```bash
cd /home/ruben/horillas
rm -rf horilla-test
mkdir -p horilla-test
cd horilla-test

git clone --depth 1 https://github.com/horilla-opensource/horilla.git app
```

## 2) Buat virtualenv + install dependency Horilla

```bash
cd /home/ruben/horillas/horilla-test/app
python3 -m venv horillavenv
source horillavenv/bin/activate
pip install -r requirements.txt
```

## 3) Buat file `.env` untuk test

File: `/home/ruben/horillas/horilla-test/app/.env`

Minimal (SQLite + enable plugin):

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://localhost:8000,http://127.0.0.1:8000
ENABLE_PPH21_PLUGIN=True
```

## 4) Install addon PPh21 ke virtualenv horilla-test

```bash
cd /home/ruben/horillas/horilla-test/app
source horillavenv/bin/activate
pip install -e /home/ruben/horillas/hris/addons/horilla_pph21_addon
```

## 5) Patch settings agar plugin bisa diaktifkan via env

File: `/home/ruben/horillas/horilla-test/app/horilla/settings.py`

Tambahkan env flag:

- `ENABLE_PPH21_PLUGIN=(bool, False)` pada `environ.Env(...)`

Lalu tambahkan di akhir `INSTALLED_APPS`:

- `if env("ENABLE_PPH21_PLUGIN"): INSTALLED_APPS.append("pph21_plugin.apps.Pph21PluginConfig")`

## 6) Migrate database

Catatan: di repo upstream Horilla, beberapa app tidak menyertakan migrations lengkap. Untuk environment test ini, payroll perlu dibuatkan migration terlebih dahulu.

```bash
cd /home/ruben/horillas/horilla-test/app
source horillavenv/bin/activate

python manage.py makemigrations payroll
python manage.py migrate --noinput
```

## 7) Install/Update “policy” PPh21 (FilingStatus)

Command addon:

```bash
cd /home/ruben/horillas/horilla-test/app
source horillavenv/bin/activate

ENABLE_PPH21_PLUGIN=True python manage.py pph21_install_policy --dry-run
ENABLE_PPH21_PLUGIN=True python manage.py pph21_install_policy --force
```

Efeknya:

- Membuat/Update `payroll.models.models.FilingStatus` dengan `filing_status="PPh21"`
- Set `use_py=True` dan mengisi `python_code` dari plugin (`pph21_plugin.indonesia.policy_code_snippet()`).

Verifikasi cepat:

```bash
python manage.py shell -c "from payroll.models.models import FilingStatus; f=FilingStatus.objects.filter(filing_status='PPh21').first(); print(bool(f), f.use_py, bool((f.python_code or '').strip()))"
```

Output yang diharapkan:

- `True True True`

## 8) Jalankan server (opsional)

```bash
cd /home/ruben/horillas/horilla-test/app
source horillavenv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

