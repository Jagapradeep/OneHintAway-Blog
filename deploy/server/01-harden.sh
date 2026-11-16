#!/bin/bash
# Basic hardening for a fresh Ubuntu 24.04 server. Safe to run again.
#   ssh root@<server> 'bash -s' < deploy/server/01-harden.sh
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# 1. SSH: keys only. No password can ever log in, so guessing passwords is pointless.
cat > /etc/ssh/sshd_config.d/00-hardening.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
EOF
sshd -t && systemctl reload ssh

# 2. Security updates install themselves.
apt-get update -qq
apt-get install -y -qq unattended-upgrades fail2ban ufw >/dev/null
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# 3. Firewall: everything closed except SSH, web, and the Kubernetes API (for deploys;
#    it accepts only clients with a valid token or certificate).
ufw --force reset >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow 22/tcp >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw allow 6443/tcp >/dev/null
# k3s: pods and services must reach each other and the node.
ufw allow from 10.42.0.0/16 >/dev/null
ufw allow from 10.43.0.0/16 >/dev/null
ufw --force enable >/dev/null

# 4. fail2ban bans addresses that keep failing SSH logins.
systemctl enable --now fail2ban >/dev/null 2>&1

# 5. A little swap, so a memory spike slows the server down instead of killing a process.
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  sysctl -q -w vm.swappiness=10 && echo 'vm.swappiness=10' > /etc/sysctl.d/99-swappiness.conf
fi

echo "--- result"
sshd -T | grep -E '^(passwordauthentication|permitrootlogin) '
ufw status | sed -n '1,12p'
systemctl is-active fail2ban unattended-upgrades
free -m | awk '/Swap:/ {print "swap " $2 " MB"}'
