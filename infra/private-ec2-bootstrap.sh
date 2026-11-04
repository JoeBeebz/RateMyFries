#!/bin/bash
set -euo pipefail
umask 077

# The static outbound address is attached immediately after instance creation.
for attempt in {1..12}; do
    if dnf install -y python3.12 python3.12-pip openssl; then break; fi
    sleep 5
done
command -v python3.12
systemctl enable --now amazon-ssm-agent
groupadd -f fry-admins
for name in '__ADMIN_ONE__' '__ADMIN_TWO__'; do
    id "$name" >/dev/null 2>&1 || useradd -m -s /bin/bash "$name"
    usermod -aG fry-admins "$name"
done
printf '%%fry-admins ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/fry-admins
chmod 440 /etc/sudoers.d/fry-admins
visudo -cf /etc/sudoers.d/fry-admins
id fryapp >/dev/null 2>&1 || useradd --system --home-dir /srv/ratemyfries --shell /sbin/nologin fryapp
install -d -m 0750 -o fryapp -g fry-admins /srv/ratemyfries
install -d -m 0700 /etc/ratemyfries /root/fry-transfer

# The private key stays on this machine. Only its public certificate is exported.
openssl req -x509 -newkey rsa:3072 -noenc -sha256 -days 7 \
    -subj '/CN=Fry private migration' \
    -keyout /root/fry-transfer/key.pem -out /root/fry-transfer/certificate.pem
chmod 600 /root/fry-transfer/key.pem

cat > /etc/systemd/system/ratemyfries.service <<'UNIT'
[Unit]
Description=Private Fry class development website
After=network-online.target
Wants=network-online.target
ConditionPathExists=/srv/ratemyfries/current/.venv/bin/waitress-serve
[Service]
Type=simple
User=fryapp
Group=fry-admins
WorkingDirectory=/srv/ratemyfries/current
EnvironmentFile=/etc/ratemyfries/google.env
ExecStart=/srv/ratemyfries/current/.venv/bin/waitress-serve --host=127.0.0.1 --port=8000 --call app:create_app
Restart=on-failure
RestartSec=5
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/srv/ratemyfries
ProtectHome=true
[Install]
WantedBy=multi-user.target
UNIT
printf 'GOOGLE_PLACES_API_KEY=\n' > /etc/ratemyfries/google.env
chmod 600 /etc/ratemyfries/google.env
systemctl daemon-reload
systemctl enable ratemyfries.service
printf 'Fry private bootstrap complete\n' > /root/fry-transfer/ready
