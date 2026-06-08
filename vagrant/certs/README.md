# Corporate TLS certificates (optional)

If provisioning still cannot use Docker’s APT repo (some proxies return HTML instead of the GPG key), the script **falls back** to Ubuntu’s **`docker.io`** + **`docker-compose-v2`** so `docker compose` keeps working.


## What to do

1. Export your organisation’s **root** (or issuing) CA as **PEM** (Base-64 `.cer` / “Certificate Base64” is fine).
2. Copy one or more files into this folder with extension **`.crt`** or **`.pem`** (PEM text: `-----BEGIN CERTIFICATE-----`).
3. Run `vagrant provision` again (or `vagrant up`). Use `vagrant provision demo` / `vagrant provision agent` if you only need one VM refreshed.

Files here are **gitignored** so they are not committed.

### Windows (quick path)

- `Win+R` → `certmgr.msc` → **Trusted Root Certification Authorities** → **Certificates**.
- Find your company root (often named after the proxy / security product).
- Right‑click → **All Tasks** → **Export** → **Base-64 encoded X.509 (.CER)** → save as e.g. `corp-root.crt` in this folder.

If the cert lives under **Intermediate** instead of **Trusted Root**, export that PEM instead (or the root that signed it).

### Verify PEM

Open the file in a text editor; it should start with:

```text
-----BEGIN CERTIFICATE-----
```

## Corporate HTTP proxy

If you use a proxy on the host, set it in the same shell before Vagrant (PowerShell example):

```powershell
$env:HTTP_PROXY = "http://10.158.100.3:8080"
$env:HTTPS_PROXY = "https://10.158.100.3:8080"
$env:NO_PROXY = "localhost,127.0.0.1"
vagrant provision
```

The `Vagrantfile` forwards these into the provision script when set.

If `docker compose` later fails pulling images with a TLS error, the same CAs are also installed under **`/etc/docker/certs.d/registry-1.docker.io/`** during provision (Docker Hub).

**pip / PyPI during `docker build`:** the app image does not inherit the VM’s trust store. Provision copies your PEM files from **`vagrant/certs/`** into **`app/docker-certs/`** in the build workspace so the **`app/Dockerfile`** can register them before `pip install` (see [`../app/README.md`](../app/README.md)).
