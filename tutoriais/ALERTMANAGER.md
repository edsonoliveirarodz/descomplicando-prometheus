# 📣 Alertmanager no Linux (systemd) — Guia passo a passo

Guia prático para **baixar, instalar, configurar e executar o Alertmanager** como serviço **systemd** em Linux.
> ✅ **Pré‑requisitos**
> - 🔑 Acesso **sudo**
> - 🧩 **systemd** disponível
> - 🌐 Porta **9093/TCP** liberada (localmente ou no firewall)
> - 🐧 Testado em **Ubuntu/Debian** (comandos compatíveis com outras distros com ajustes mínimos)

---

## 🔗 Página oficial de download
```
https://prometheus.io/download/#alertmanager
```

---

## 1) 📥 Baixar e extrair o binário
> Exemplo usando a **versão 0.28.1** (ajuste conforme necessário).

```bash
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v0.28.1/alertmanager-0.28.1.linux-amd64.tar.gz
tar -xvzf alertmanager-0.28.1.linux-amd64.tar.gz
cd alertmanager-0.28.1.linux-amd64
```

---

## 2) 🚚 Instalar binários
```bash
sudo install -m 0755 alertmanager /usr/local/bin/alertmanager
sudo install -m 0755 amtool       /usr/local/bin/amtool
```

Valide a instalação:
```bash
alertmanager --version
amtool --version
```

---

## 3) 👤 Criar usuário/grupo e diretórios
```bash
# Usuário e grupo de sistema sem shell de login
sudo groupadd -r alertmanager 2>/dev/null || true
sudo useradd  -r -g alertmanager --no-create-home --shell /sbin/nologin alertmanager 2>/dev/null || true

# Diretórios de config, dados e (opcional) logs
sudo mkdir -p /etc/alertmanager /var/lib/alertmanager /var/log/alertmanager
sudo chown -R alertmanager:alertmanager /etc/alertmanager /var/lib/alertmanager /var/log/alertmanager
```

---

## 4) ⚙️ Criar o serviço `systemd`
Crie **`/etc/systemd/system/alertmanager.service`** com o conteúdo abaixo:

```ini
[Unit]
Description=Prometheus Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
WorkingDirectory=/var/lib/alertmanager

ExecStart=/usr/local/bin/alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --storage.path=/var/lib/alertmanager \
  --web.route-prefix=/ \
  --web.listen-address=:9093

Restart=on-failure
RestartSec=5s

# Hardening (ajuste conforme suporte da sua versão do systemd)
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
ReadWritePaths=/var/lib/alertmanager /var/log/alertmanager

[Install]
WantedBy=multi-user.target
```

Grave via `tee` (copiar/colar):
```bash
sudo tee /etc/systemd/system/alertmanager.service > /dev/null <<'SERVICE'
[Unit]
Description=Prometheus Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
User=alertmanager
Group=alertmanager
Type=simple
WorkingDirectory=/var/lib/alertmanager

ExecStart=/usr/local/bin/alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --storage.path=/var/lib/alertmanager \
  --web.route-prefix=/ \
  --web.listen-address=:9093

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
ReadWritePaths=/var/lib/alertmanager /var/log/alertmanager

[Install]
WantedBy=multi-user.target
SERVICE
```

Carregue, habilite e inicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now alertmanager
```

Verifique status e logs:
```bash
systemctl status alertmanager --no-pager
journalctl -u alertmanager -f
```

---

## 5) 🖥️ Acessar a interface Web
```
http://localhost:9093
```
*(em servidor remoto, substitua `localhost` pelo host/IP e garanta a porta liberada).*

Endpoints úteis:
```bash
curl -s http://localhost:9093/-/healthy
curl -s http://localhost:9093/api/v2/status | jq .  # se tiver jq instalado
```

---

## 6) 🔗 Integrar o Alertmanager no Prometheus
No **Prometheus**, adicione a seção `alerting` e inclua seus arquivos de regras:

```yaml
# /etc/prometheus/prometheus.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["localhost:9093"]

rule_files:
  - /etc/prometheus/rules/*.yml
```

Exemplo simples de regra (salve em `/etc/prometheus/rules/instance_down.yml`):
```yaml
groups:
  - name: example.rules
    rules:
      - alert: InstanceDown
        expr: up == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Instância {{ $labels.instance }} fora do ar"
          description: "O alvo {{ $labels.job }} / {{ $labels.instance }} não responde há mais de 2 minutos."
```

Recarregue o Prometheus (se iniciado com `--web.enable-lifecycle`):
```bash
curl -X POST http://localhost:9090/-/reload
```

---

## 7) 🧰 Operações com `amtool`
Listar alertas ativos:
```bash
amtool alert query
```

Criar um **silence** por 1h para um alerta específico:
```bash
amtool silence add alertname=InstanceDown --duration 1h \
  --author "Seu Nome" --comment "Janela de manutenção"
```

Mostrar silences:
```bash
amtool silence query
```

Validar config (sempre que editar `alertmanager.yml`):
```bash
amtool check-config /etc/alertmanager/alertmanager.yml
```

---

## 8) 🧯 Solução de problemas
- 🔎 **Status & logs:** `systemctl status alertmanager` • `journalctl -u alertmanager -f`
- 🧪 **Healthcheck:** `curl -s localhost:9093/-/healthy`
- 🌐 **Porta:** `ss -lntp | grep :9093`
- ✅ **Config ok?:** `amtool check-config /etc/alertmanager/alertmanager.yml`
- 🔗 **Prometheus aponta para o AM?:** verifique a seção `alerting:` no `prometheus.yml`
- ⏱️ **Reloader:** atualize com `systemctl restart alertmanager` após mudar a config

---

## 9) 📂 Caminhos importantes
- ⚙️ Binários: `/usr/local/bin/alertmanager`, `/usr/local/bin/amtool`
- 🧾 Config: `/etc/alertmanager/alertmanager.yml`
- 💾 Dados: `/var/lib/alertmanager`
- 🧾 Logs: `journalctl -u alertmanager` (ou `/var/log/alertmanager` se configurado)
- 🌐 UI: `http://<host>:9093`
