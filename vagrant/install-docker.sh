# Sourced by vagrant/provision.sh and vagrant/provision-agent.sh (do not run standalone).
# Docker Engine + Compose plugin + optional corporate CAs (same as former top of provision.sh).

CERT_DIR="/vagrant/vagrant/certs"

# Optional proxy from Vagrantfile env: pass through for apt/curl/docker install
if [[ -n "${HTTP_PROXY:-}" ]]; then export http_proxy="$HTTP_PROXY" HTTP_PROXY="$HTTP_PROXY"; fi
if [[ -n "${HTTPS_PROXY:-}" ]]; then export https_proxy="$HTTPS_PROXY" HTTPS_PROXY="$HTTPS_PROXY"; fi
if [[ -n "${NO_PROXY:-}" ]]; then export no_proxy="$NO_PROXY" NO_PROXY="$NO_PROXY"; fi

apt_get() {
  apt-get update -qq
  apt-get install -y -qq "$@"
}

install_corporate_cas() {
  local n=0 f
  shopt -s nullglob
  local files=("$CERT_DIR"/*.crt "$CERT_DIR"/*.cer "$CERT_DIR"/*.pem)
  shopt -u nullglob
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No files in $CERT_DIR (*.crt, *.cer, *.pem). If HTTPS fails, add your corporate root PEM there."
    return 0
  fi
  echo "Installing ${#files[@]} corporate CA file(s) into system trust store..."
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    if ! grep -q "BEGIN CERTIFICATE" "$f" 2>/dev/null; then
      echo "Skipping (no PEM marker): $f"
      continue
    fi
    n=$((n + 1))
    install -m 0644 "$f" "/usr/local/share/ca-certificates/vagrant-corp-${n}.crt"
  done
  if [[ "$n" -gt 0 ]]; then
    update-ca-certificates
  fi
}

apt-get update -qq
apt-get install -y -qq ca-certificates curl gnupg openssl
install_corporate_cas

install_docker_ce() {
  install -m 0755 -d /etc/apt/keyrings
  rm -f /etc/apt/keyrings/docker.gpg

  local keyfile
  keyfile="$(mktemp)"
  if ! curl -fsSL -o "$keyfile" https://download.docker.com/linux/ubuntu/gpg; then
    rm -f "$keyfile"
    return 1
  fi
  if ! grep -qE '^-----BEGIN PGP (PUBLIC )?KEY BLOCK-----' "$keyfile" 2>/dev/null; then
    echo "ERROR: download.docker.com did not return an OpenPGP armored key (proxy/block page?). First 500 bytes:"
    head -c 500 "$keyfile" | sed 's/[^[:print:]\t]/./g' || true
    echo
    rm -f "$keyfile"
    return 1
  fi
  if ! gpg --batch --no-tty --output /etc/apt/keyrings/docker.gpg --dearmor "$keyfile"; then
    rm -f "$keyfile"
    return 1
  fi
  rm -f "$keyfile"
  chmod a+r /etc/apt/keyrings/docker.gpg

  # shellcheck source=/dev/null
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    >/etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
}

install_docker_ubuntu_packages() {
  echo "Using Ubuntu archive: docker.io + docker-compose-v2 (no download.docker.com repo)."
  rm -f /etc/apt/sources.list.d/docker.list
  rm -f /etc/apt/keyrings/docker.gpg
  apt-get update -qq
  apt-get install -y -qq docker.io docker-compose-v2
  systemctl enable --now docker
}

if ! command -v docker >/dev/null 2>&1; then
  if ! install_docker_ce; then
    install_docker_ubuntu_packages
  fi
fi

if compgen -G "/usr/local/share/ca-certificates/vagrant-corp-*.crt" >/dev/null 2>&1; then
  mkdir -p /etc/docker/certs.d/registry-1.docker.io
  cat /usr/local/share/ca-certificates/vagrant-corp-*.crt >/etc/docker/certs.d/registry-1.docker.io/ca.crt
  systemctl restart docker 2>/dev/null || true
fi

apt_get curl
