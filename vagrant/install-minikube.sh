# Sourced by vagrant/provision.sh after install-docker.sh + install-kubectl.sh.
# Installs minikube to /usr/local/bin and starts a one-node cluster (--driver=docker).
# Kubeconfig + profile are copied to vagrant's home so `vagrant ssh` + kubectl work.
#
# Set MINIKUBE_START=0 (e.g. in Vagrantfile env) to only install the binary and skip start.

MINIKUBE_START="${MINIKUBE_START:-1}"

install_minikube_binary() {
  local arch u url tmp
  u="$(dpkg --print-architecture)"
  case "$u" in
    amd64) arch="amd64" ;;
    arm64) arch="arm64" ;;
    *)
      echo "Unsupported dpkg architecture for minikube: $u" >&2
      return 1
      ;;
  esac

  url="https://storage.googleapis.com/minikube/releases/latest/minikube-linux-${arch}"
  tmp="$(mktemp)"
  echo "Installing latest minikube (${arch}) from ${url}..."
  curl -fsSL "$url" -o "$tmp"
  install -m 0755 "$tmp" /usr/local/bin/minikube
  rm -f "$tmp"
}

sync_minikube_to_vagrant() {
  mkdir -p /home/vagrant/.kube
  if [[ -f /root/.kube/config ]]; then
    cp -a /root/.kube/config /home/vagrant/.kube/config
    sed -i 's#/root/.minikube#/home/vagrant/.minikube#g' /home/vagrant/.kube/config
  fi
  if [[ -d /root/.minikube ]]; then
    rm -rf /home/vagrant/.minikube
    cp -a /root/.minikube /home/vagrant/.minikube
  fi
  chown -R vagrant:vagrant /home/vagrant/.kube /home/vagrant/.minikube 2>/dev/null || true
}

if command -v minikube >/dev/null 2>&1; then
  echo "minikube already on PATH ($(command -v minikube))."
else
  install_minikube_binary
fi

minikube version

if [[ "${MINIKUBE_START}" == "0" ]]; then
  echo "MINIKUBE_START=0: skipping minikube start. Later: sudo minikube start --driver=docker"
  return 0
fi

# docker driver avoids nested KVM inside VirtualBox; needs Docker from install-docker.sh.
# Vagrant runs this script as root; minikube v1.38+ requires --force for docker-as-root (DRV_AS_ROOT).
if ! minikube status >/dev/null 2>&1; then
  echo "Starting minikube (docker driver)..."
  apt-get install -y -qq conntrack >/dev/null 2>&1 || true
  # minikube v1.38+ requires at least 2 CPUs for the docker driver; demo VM uses vb.cpus=2
  minikube start --driver=docker --force --cpus=2 --memory=2048 --wait=all --wait-timeout=10m
fi

sync_minikube_to_vagrant

echo "Verifying cluster (as vagrant)..."
runuser -u vagrant -- /usr/local/bin/kubectl cluster-info
echo "OK: minikube is installed and kubectl can reach the API."
