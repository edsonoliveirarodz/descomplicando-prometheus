# 🖥️ Node Exporter no Linux (systemd) — Guia passo a passo

Guia prático para **baixar, instalar, configurar e operar** o **Node Exporter** como serviço no Linux via **systemd**.

> ✅ **Pré‑requisitos**
> - 🔑 Acesso **sudo**
> - 🧩 **systemd** disponível
> - 🌐 Porta **9100/TCP** liberada (localmente ou no firewall)
> - 🐧 Testado em **Ubuntu/Debian** (comandos compatíveis com outras distros com ajustes mínimos)

---

## 🔗 Página oficial de download
```
https://prometheus.io/download/#node_exporter
```

---

## 1) 📥 Baixar e descompactar o binário
> Abaixo usando a **versão 1.9.1** (ajuste conforme necessário).

```bash
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.9.1/node_exporter-1.9.1.linux-amd64.tar.gz
tar -xvzf node_exporter-1.9.1.linux-amd64.tar.gz
```

---

## 2) 🚚 Instalar o binário em `/usr/local/bin`
Use `install` para já definir permissões corretas:

```bash
sudo install -m 0755 node_exporter-1.9.1.linux-amd64/node_exporter /usr/local/bin/node_exporter
```

Valide a instalação:
```bash
node_exporter --version
```

---

## 3) 👤 Criar usuário/grupo do serviço
(sem shell de login e sem diretório home)

```bash
sudo groupadd -r node_exporter 2>/dev/null || true
sudo useradd  -r -g node_exporter --no-create-home --shell /sbin/nologin node_exporter
```

---

## 4) ⚙️ Criar o serviço `systemd`
Crie o arquivo **`/etc/systemd/system/node_exporter.service`** com o conteúdo abaixo:

```ini
[Unit]
Description=Node Exporter
Documentation=https://prometheus.io/download/#node_exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
  --web.listen-address=:9100 \
  --web.telemetry-path=/metrics

Restart=on-failure
RestartSec=5s

# Hardening básico (ajuste conforme suporte da sua versão do systemd)
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true
ProtectClock=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=true
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
```

Grave o arquivo (exemplo usando `tee`):
```bash
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<'SERVICE'
[Unit]
Description=Node Exporter
Documentation=https://prometheus.io/download/#node_exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
  --web.listen-address=:9100 \
  --web.telemetry-path=/metrics
Restart=on-failure
RestartSec=5s
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true
ProtectClock=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=true
MemoryDenyWriteExecute=true

[Install]
WantedBy=multi-user.target
SERVICE
```

---

## 5) 🔁 Carregar, habilitar e iniciar o serviço
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
```

Verifique status e logs:
```bash
systemctl status node_exporter --no-pager
journalctl -u node_exporter -f
```

---

## 6) 🌐 Testar as métricas expostas
```bash
curl http://localhost:9100/metrics
```
Você deverá ver métricas como `node_cpu_seconds_total`, `node_memory_MemAvailable_bytes`, `node_filesystem_avail_bytes`, entre outras.

---

## 7) 🧭 Adicionar o Node Exporter ao Prometheus
Edite `/etc/prometheus/prometheus.yml` e inclua um *job*:

```yaml
scrape_configs:
  - job_name: "node_exporter"
    static_configs:
      - targets: ["localhost:9100"]
```

Recarregue a configuração (se o Prometheus foi iniciado com `--web.enable-lifecycle`):
```bash
curl -X POST http://localhost:9090/-/reload
```

---

## 8) 🧾 Operações comuns
```bash
sudo systemctl stop node_exporter
sudo systemctl start node_exporter
sudo systemctl restart node_exporter
```

Atualizar para uma nova versão (exemplo rápido):
```bash
# pare o serviço
sudo systemctl stop node_exporter

# baixe a nova versão e reinstale o binário (repita as etapas das seções 1 e 2)

# reinicie
sudo systemctl start node_exporter
```

---

## 9) 🧯 Solução de problemas
- 🔎 **Logs:** `journalctl -u node_exporter -f`  
- 🌐 **Porta em uso:** `ss -lntp | grep :9100`  
- ⚙️ **Opções disponíveis:** `node_exporter --help`  
