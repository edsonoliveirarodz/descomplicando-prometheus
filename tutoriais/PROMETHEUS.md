# 🚀 Prometheus no Linux (systemd) — Guia passo a passo

Um guia prático para **baixar, instalar, configurar e executar o Prometheus como serviço** no Linux usando **systemd**.

> ✅ **Pré‑requisitos**
> - 🔑 Acesso **sudo**
> - 🧩 **systemd** disponível
> - 🌐 Porta **9090/TCP** liberada (localmente ou no firewall)

---

## 1) 📥 Baixar o binário

```bash
# Ajuste conforme necessário
export PROM_VERSION="3.5.0"
curl -fsSLO https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz
```

📦 **Extraia** e entre no diretório:
```bash
tar -xvf prometheus-3.5.0.linux-amd64.tar.gz
cd prometheus-3.5.0.linux-amd64.tar.gz
```

---

## 2) 🧑‍🔧 Criar usuário/grupo e diretórios padrão

```bash
# Usuário e grupo de sistema sem shell de login
sudo groupadd -r prometheus 2>/dev/null || true
sudo useradd  -r -g prometheus --no-create-home --shell /sbin/nologin prometheus

# Diretórios para config, dados e logs
sudo mkdir -p /etc/prometheus /var/lib/prometheus /var/log/prometheus
```

🗂️ **Layout recomendado**
- `/usr/local/bin/` → binários `prometheus` e `promtool`
- `/etc/prometheus/` → `prometheus.yml`, `consoles/`, `console_libraries/`
- `/var/lib/prometheus/` → dados (TSDB)
- `/var/log/prometheus/` → logs do serviço

---

## 3) 🔧 Instalar binários e (opcional) consoles

```bash
# Copie binários com permissões adequadas
sudo install -m 0755 prometheus /usr/local/bin/prometheus
sudo install -m 0755 promtool /usr/local/bin/promtool

# (Opcional, porém útil para páginas de console)
sudo cp -r consoles console_libraries /etc/prometheus/
```

🔐 **Ajuste propriedade (owner):**
```bash
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus /var/log/prometheus
sudo chown prometheus:prometheus /usr/local/bin/prometheus /usr/local/bin/promtool
```

🧪 **Valide as versões:**
```bash
prometheus --version
promtool --version
```

---

## 4) 📝 Criar a configuração do Prometheus

Crie um arquivo mínimo em `/etc/prometheus/prometheus.yml`:

```yaml
# /etc/prometheus/prometheus.yml
global:
  # Configurações globais do Prometheus, ou seja, configurações que serão utilizadas em todos os jobs caso não sejam configuradas separadamente dentro de cada job.
  scrape_interval: 15s # Intervalo de coleta dos dados, ou seja, a cada 15 segundos o Prometheus vai até o alvo monitorado coletar as métricas, o padrão é 1 minuto.
  evaluation_interval: 15s # Intervalo para o Prometheus avaliar as regras de alerta, o padrão é 1 minuto. Não estamos utilizando regras para os alertas, vamos manter aqui somente para referência.
  scrape_timeout: 10s # Intervalos para o Prometheus aguardar o alvo monitorado responder antes de considerar que o alvo está indisponível, o padrão é 10 segundos.

rule_files: # Inicio da definição das regras de alerta, nesse primeiro exemplo vamos deixar sem regras, pois não iremos utilizar alertas por agora.

scrape_configs:
# Inicio da definição das configurações de coleta, ou seja, como o Prometheus vai coletar as métricas e onde ele vai encontrar essas métricas.
- job_name: "prometheus" # Nome do job, ou seja, o nome do serviço que o Prometheus vai monitorar.
  static_configs:
  # Inicio da definição das configurações estáticas, ou seja, configurações que não serão alteradas durante o processo de coleta.
  - targets: [ "localhost:9090" ] # Endereço do alvo monitorado, ou seja, o endereço do serviço que o Prometheus vai monitorar. Nesse caso é o próprio Prometheus.
```

🧪 **Valide a configuração:**
```bash
promtool check config /etc/prometheus/prometheus.yml
```

---

## 5) ⚙️ Criar o serviço systemd

Crie `/etc/systemd/system/prometheus.service` com o conteúdo abaixo:

```
[Unit]
Description=Prometheus
Documentation=https://prometheus.io/docs/introduction/overview/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecReload=/bin/kill -HUP \$MAINPID
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --web.listen-address=0.0.0.0:9090 \
  --web.external-url=

SyslogIdentifier=prometheus
Restart=always

[Install]
WantedBy=multi-user.target
```

🔁 **Recarregue, habilite e inicie o serviço:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now prometheus
```

🔎 **Verifique status e logs:**
```bash
systemctl status prometheus --no-pager
journalctl -u prometheus -f
```

---

## 6) 🖥️ Acessar a interface Web

Abra o navegador e acesse:

```
http://localhost:9090
```

Se estiver em um servidor remoto, substitua `localhost` pelo IP/host e garanta a porta liberada.

---

## 7) 🛠️ Operações comuns

**🔄 Recarregar configuração sem reiniciar** (requer `--web.enable-lifecycle`):
```bash
curl -X POST http://localhost:9090/-/reload
```

**⏯️ Parar / Iniciar / Reiniciar:**
```bash
sudo systemctl stop prometheus
sudo systemctl start prometheus
sudo systemctl restart prometheus
```

**⬆️ Atualizar para nova versão:**
1. Ajuste `PROM_VERSION` e repita as etapas **1–3**.
2. Valide com `prometheus --version` e `promtool --version`.
3. `sudo systemctl restart prometheus`.

**🧼 Desinstalar** (preserva dados):
```bash
sudo systemctl disable --now prometheus
sudo rm -f /etc/systemd/system/prometheus.service
sudo rm -f /usr/local/bin/prometheus /usr/local/bin/promtool
sudo systemctl daemon-reload
```
> ⚠️ Se quiser remover **dados/config**, apague `/var/lib/prometheus`, `/var/log/prometheus` e `/etc/prometheus` (cuidado!).

---

## 8) 🧯 Solução de problemas (troubleshooting)
- 📝 Logs: `journalctl -u prometheus -e` ou `-f` para seguir em tempo real
- 🔭 Porta: `ss -lntp | grep :9090`
- ✅ Config: `promtool check config /etc/prometheus/prometheus.yml`
- 🔍 Execução: `systemctl show -p ExecStart prometheus`
- 🔐 Permissões: confirme que dados/logs pertencem a `prometheus:prometheus`

---

## 9) 🧭 Referências rápidas
| Item | Caminho / Comando |
|---|---|
| 📁 Binários | `/usr/local/bin/prometheus`, `/usr/local/bin/promtool` |
| ⚙️ Config | `/etc/prometheus/prometheus.yml` |
| 💾 Dados | `/var/lib/prometheus` |
| 🧾 Logs | `journalctl -u prometheus` e `/var/log/prometheus` |
| 🌐 UI | `http://<host>:9090` |
