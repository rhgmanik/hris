# Horilla PPh21 Addon

Addon plugin PPh21 (Indonesia) untuk Horilla.

## Instalasi (wheel) untuk banyak klien

Di mesin build:

```bash
python -m pip install --upgrade pip
python -m pip install "build>=1.2.1"
python -m build /home/ruben/horillas/horilla_pph21_addon
```

Hasil wheel ada di `dist/`. Salin wheel itu ke server klien lalu install:

```bash
source horillavenv/bin/activate
pip install /path/to/horilla_pph21_addon-0.1.0-py3-none-any.whl
```

## Instalasi (editable) untuk development

```bash
source horillavenv/bin/activate
pip install -e /home/ruben/horillas/horilla_pph21_addon
```

## Aktivasi

Tambahkan `pph21_plugin.apps.Pph21PluginConfig` ke `INSTALLED_APPS`.

## Release SOP singkat

Build wheel:

```bash
cd /home/ruben/horillas/horilla_pph21_addon
bash scripts/build_wheel.sh
```

Upload ke private registry (opsional):

```bash
python -m pip install "twine>=5.1.1"
python -m twine upload dist/*
```

## Install/Update policy code

```bash
python manage.py pph21_install_policy --company-id 1 --force
```
