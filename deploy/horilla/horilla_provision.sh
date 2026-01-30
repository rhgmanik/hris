#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  horilla_provision.sh --client <name> --domain <fqdn> --internal-port <port> \
    --db-name <name> --db-user <user> --db-password <pass> --db-host <host> --db-port <port> \
    [--install-dir /opt/horilla] [--horilla-repo https://github.com/horilla-opensource/horilla.git] [--horilla-branch master] \
    [--ssl none|letsencrypt] [--letsencrypt-email <email>] \
    [--enable-pph21] [--pph21-wheel /path/to/horilla_pph21_addon-0.1.0-py3-none-any.whl]

Notes:
  - Jalankan dengan sudo (menulis /etc/systemd/system dan /etc/nginx).
  - SSL Let's Encrypt membutuhkan DNS A/AAAA record domain sudah mengarah ke server.
USAGE
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || return 1
}

require_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "Harus dijalankan sebagai root (sudo)."
    exit 1
  fi
}

CLIENT=""
DOMAIN=""
INTERNAL_PORT=""
INSTALL_DIR="/opt/horilla"
HORILLA_REPO="https://github.com/horilla-opensource/horilla.git"
HORILLA_BRANCH="master"
SSL_MODE="none"
LE_EMAIL=""
ENABLE_PPH21="false"
PPH21_WHEEL=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --client) CLIENT="${2:-}"; shift 2 ;;
    --domain) DOMAIN="${2:-}"; shift 2 ;;
    --internal-port) INTERNAL_PORT="${2:-}"; shift 2 ;;
    --install-dir) INSTALL_DIR="${2:-}"; shift 2 ;;
    --horilla-repo) HORILLA_REPO="${2:-}"; shift 2 ;;
    --horilla-branch) HORILLA_BRANCH="${2:-}"; shift 2 ;;
    --ssl) SSL_MODE="${2:-}"; shift 2 ;;
    --letsencrypt-email) LE_EMAIL="${2:-}"; shift 2 ;;
    --enable-pph21) ENABLE_PPH21="true"; shift 1 ;;
    --pph21-wheel) PPH21_WHEEL="${2:-}"; shift 2 ;;
    --db-name) DB_NAME="${2:-}"; shift 2 ;;
    --db-user) DB_USER="${2:-}"; shift 2 ;;
    --db-password) DB_PASSWORD="${2:-}"; shift 2 ;;
    --db-host) DB_HOST="${2:-}"; shift 2 ;;
    --db-port) DB_PORT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Arg tidak dikenal: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$DOMAIN" || -z "$INTERNAL_PORT" || -z "$DB_NAME" || -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_HOST" || -z "$DB_PORT" ]]; then
  usage
  exit 1
fi

if [[ "$SSL_MODE" != "none" && "$SSL_MODE" != "letsencrypt" ]]; then
  echo "--ssl harus none atau letsencrypt"
  exit 1
fi

if [[ "$SSL_MODE" == "letsencrypt" && -z "$LE_EMAIL" ]]; then
  echo "--letsencrypt-email wajib jika --ssl letsencrypt"
  exit 1
fi

if [[ "$ENABLE_PPH21" == "true" && -z "$PPH21_WHEEL" ]]; then
  echo "--pph21-wheel wajib jika --enable-pph21"
  exit 1
fi

require_root

missing=()
for c in python3 git nginx systemctl; do
  if ! need_cmd "$c"; then
    missing+=("$c")
  fi
done

if ! need_cmd pip3; then
  if ! python3 -m pip --version >/dev/null 2>&1; then
    missing+=("pip")
  fi
fi

if [[ "$SSL_MODE" == "letsencrypt" ]]; then
  if ! need_cmd certbot; then
    missing+=("certbot")
  fi
fi

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "Dependency belum lengkap: ${missing[*]}"
  echo "Install dulu (Ubuntu):"
  echo "  sudo apt update"
  echo "  sudo apt install -y python3 python3-venv python3-pip git nginx"
  if [[ "$SSL_MODE" == "letsencrypt" ]]; then
    echo "  sudo apt install -y certbot python3-certbot-nginx"
  fi
  exit 1
fi

BASE_DIR="${INSTALL_DIR}/${CLIENT}"
APP_DIR="${BASE_DIR}/app"
VENV_DIR="${BASE_DIR}/venv"
ENV_FILE="${BASE_DIR}/.env"
SERVICE_NAME="horilla-${CLIENT}"
NGINX_SITE="/etc/nginx/sites-available/${SERVICE_NAME}.conf"
NGINX_SITE_ENABLED="/etc/nginx/sites-enabled/${SERVICE_NAME}.conf"

mkdir -p "${BASE_DIR}"

if [[ -d "${APP_DIR}/.git" ]]; then
  git -C "${APP_DIR}" fetch --all --prune
  git -C "${APP_DIR}" checkout "${HORILLA_BRANCH}"
  git -C "${APP_DIR}" pull --ff-only
else
  git clone --branch "${HORILLA_BRANCH}" "${HORILLA_REPO}" "${APP_DIR}"
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

if [[ "$ENABLE_PPH21" == "true" ]]; then
  "${VENV_DIR}/bin/pip" install "${PPH21_WHEEL}"
fi

SECRET_KEY="$("${VENV_DIR}/bin/python" -c "import secrets; print(secrets.token_urlsafe(50))")"
CSRF_ORIGINS="https://${DOMAIN},http://${DOMAIN}"

cat > "${ENV_FILE}" <<EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${DOMAIN}
CSRF_TRUSTED_ORIGINS=${CSRF_ORIGINS}

DB_ENGINE=django.db.backends.postgresql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

ENABLE_PPH21_PLUGIN=${ENABLE_PPH21}
EOF

cd "${APP_DIR}"
set +u
source "${VENV_DIR}/bin/activate"
set -u

python manage.py check
python manage.py migrate --noinput
python manage.py compilemessages || true
python manage.py collectstatic --noinput

cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Horilla (${CLIENT}) Gunicorn
After=network.target

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --timeout 120 --bind 127.0.0.1:${INTERNAL_PORT} horilla.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"
systemctl restart "${SERVICE_NAME}.service"

cat > "${NGINX_SITE}" <<EOF
server {
  listen 80;
  server_name ${DOMAIN};

  client_max_body_size 50m;

  location /static/ {
    alias ${APP_DIR}/staticfiles/;
  }

  location /media/ {
    alias ${APP_DIR}/media/;
  }

  location / {
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_pass http://127.0.0.1:${INTERNAL_PORT};
  }
}
EOF

ln -sf "${NGINX_SITE}" "${NGINX_SITE_ENABLED}"
nginx -t
systemctl reload nginx

if [[ "$SSL_MODE" == "letsencrypt" ]]; then
  certbot --nginx -d "${DOMAIN}" -m "${LE_EMAIL}" --agree-tos --non-interactive --redirect
  nginx -t
  systemctl reload nginx
fi

if [[ "$ENABLE_PPH21" == "true" ]]; then
  ENABLE_PPH21_PLUGIN=true python manage.py pph21_install_policy --all-companies --force || true
fi

echo "OK"
echo "App dir: ${APP_DIR}"
echo "Env file: ${ENV_FILE}"
echo "Service: ${SERVICE_NAME}"
echo "Nginx: ${NGINX_SITE}"
