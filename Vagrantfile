# -*- mode: ruby -*-
# vi: set ft=ruby :

# Two Linux VMs (Ubuntu): demo = full POC in one place (Docker Compose app+DB + minikube + kubectl);
# agent = RCA agent container only (Docker + kubectl, no minikube).
# Demo keeps Compose and Kubernetes on the same guest so you do not need a second VM or host minikube for this flow.
# Skip minikube start / save RAM: MINIKUBE_START=0 vagrant up demo  (PowerShell: $env:MINIKUBE_START="0")
# Requires: VirtualBox + Vagrant. From repo root:
#   vagrant up              # both VMs
#   vagrant up demo         # app + Postgres + minikube (default MINIKUBE_START=1)
#   If host port 8000 is busy: DEMO_APP_HOST_PORT=18000 vagrant up demo  (PowerShell: $env:DEMO_APP_HOST_PORT="18000")
#   vagrant up agent        # RCA agent on http://127.0.0.1:18080 (host) -> guest 8080
#   vagrant ssh demo|agent
#
# Migrating from the old single-VM layout: destroy the old box first (`vagrant destroy -f`), then `vagrant up`
# so VirtualBox gets `production_agent_monitor-demo` and `production_agent_monitor-agent` instead of the
# previous single `production_agent_monitor` name.

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"

  proxy_env = {
    "HTTP_PROXY"  => ENV["HTTP_PROXY"] || ENV["http_proxy"].to_s,
    "HTTPS_PROXY" => ENV["HTTPS_PROXY"] || ENV["https_proxy"].to_s,
    "NO_PROXY"    => ENV["NO_PROXY"] || ENV["no_proxy"].to_s,
  }

  config.vm.define "demo", primary: true do |demo|
    demo.vm.hostname = "rca-demo-docker"
    # API: guest 8000 -> host (default 8000). If host 8000 is busy, set DEMO_APP_HOST_PORT e.g. 18000
    # before `vagrant up`, and/or rely on auto_correct so Vagrant picks another host port (see `vagrant port demo`).
    demo_api_host_port = ENV.fetch("DEMO_APP_HOST_PORT", "8000").to_i
    demo.vm.network "forwarded_port", guest: 8000, host: demo_api_host_port, host_ip: "127.0.0.1", auto_correct: true
    demo.vm.network "forwarded_port", guest: 5432, host: 5433, host_ip: "127.0.0.1", auto_correct: true

    demo.vm.provider "virtualbox" do |vb|
      vb.name = "production_agent_monitor-demo"
      vb.cpus = 2
      # minikube (docker driver) + docker compose app/DB; use MINIKUBE_START=0 to skip cluster and lower RAM
      vb.memory = 4096
    end

    minikube_env = { "MINIKUBE_START" => ENV.fetch("MINIKUBE_START", "1") }
    demo.vm.provision "shell", path: "vagrant/provision.sh", privileged: true, env: proxy_env.merge(minikube_env)
  end

  config.vm.define "agent" do |agent|
    agent.vm.hostname = "rca-agent-docker"
    # Host 18080 avoids clashing with other services; guest listens on 8080.
    agent.vm.network "forwarded_port", guest: 8080, host: 18080, host_ip: "127.0.0.1", auto_correct: true

    agent.vm.provider "virtualbox" do |vb|
      vb.name = "production_agent_monitor-agent"
      vb.cpus = 1
      vb.memory = 1536
    end

    agent.vm.provision "shell", path: "vagrant/provision-agent.sh", privileged: true, env: proxy_env
  end
end
