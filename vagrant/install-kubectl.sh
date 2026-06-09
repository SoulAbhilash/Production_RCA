# Sourced by vagrant/provision.sh and vagrant/provision-agent.sh after install-docker.sh
# (curl + CA certificates are already configured). Installs upstream kubectl to /usr/local/bin
# and verifies the client responds. Does not require a Kubernetes cluster.

install_kubectl_binary() {
  local arch u version url tmp shafile expected
  u="$(dpkg --print-architecture)"
  case "$u" in
    amd64 | arm64) arch="$u" ;;
    *)
      echo "Unsupported dpkg architecture for kubectl: $u" >&2
      return 1
      ;;
  esac

  version="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"
  url="https://dl.k8s.io/release/${version}/bin/linux/${arch}/kubectl"
  tmp="$(mktemp)"
  echo "Installing kubectl ${version} (${arch})..."
  curl -fsSL "$url" -o "$tmp"
  shafile="${tmp}.sha256"
  curl -fsSL "${url}.sha256" -o "$shafile"
  expected="$(cut -d' ' -f1 <"$shafile")"
  echo "${expected}  ${tmp}" | sha256sum -c -
  install -m 0755 "$tmp" /usr/local/bin/kubectl
  rm -f "$tmp" "$shafile"
}

if command -v kubectl >/dev/null 2>&1; then
  echo "kubectl already on PATH ($(command -v kubectl))."
else
  install_kubectl_binary
fi

echo "Verifying kubectl client..."
kubectl version --client
echo "OK: kubectl is installed and the client runs."
