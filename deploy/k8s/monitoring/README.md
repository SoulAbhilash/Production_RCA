# Monitoring stack (optional POC add-on)

For **Phase F / H** of the playbook, install **Prometheus** + **Alertmanager** in `poc` and route alerts to the in-cluster RCA agent:

```text
Alertmanager receiver webhook → http://rca-agent.poc.svc.cluster.local:8080/incidents
```

Recommended approach for a quick lab:

1. Add Helm repo: `prometheus-community` and install `kube-prometheus-stack` into a `monitoring` namespace **or** use a minimal `prometheus` chart with Alertmanager enabled.
2. Configure `alertmanager.config.receivers` with `webhook_configs` pointing at the `rca-agent` Service URL above.
3. Add `ServiceMonitor` for `demo-app` only if you export Prometheus metrics from the app (not included in the minimal demo image).

See also: [AWS Observability for EKS — Fluent Bit](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-logs-FluentBit.html) for CloudWatch log shipping.
