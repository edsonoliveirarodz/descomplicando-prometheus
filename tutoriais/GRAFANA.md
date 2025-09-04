# 📈 Grafana no Linux (systemd) — Guia passo a passo

Um guia direto para **instalar, configurar e operar o Grafana** em distribuições baseadas em **Debian/Ubuntu** usando **systemd**.

> ✅ **Pré‑requisitos**
> - 🔑 Acesso **sudo**
> - 🧩 **systemd** disponível
> - 🌐 Porta **3000/TCP** liberada (localmente ou no firewall)
> - 🐧 Distribuições: **Ubuntu/Debian** (este guia usa `apt`)

---

## 1) 📦 Instalar pacotes de pré‑requisitos
```bash
sudo apt update
sudo apt install -y apt-transport-https software-properties-common wget gpg
```

---

## 2) 🗝️ Configurar repositório oficial e instalar o Grafana
```bash
# Crie o diretório de chaves (se ainda não existir)
sudo mkdir -p /etc/apt/keyrings/

# Baixe e registre a chave GPG do repositório
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

# Adicione o repositório estável do Grafana
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Atualize e instale
sudo apt update
sudo apt install -y grafana
```

> ℹ️ O pacote `grafana` instala o **grafana-server**, arquivos de configuração e cria o serviço systemd.

---

## 3) ▶️ Iniciar, habilitar e verificar o serviço
```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
sudo systemctl status grafana-server --no-pager
```
Logs em tempo real:
```bash
journalctl -u grafana-server -f
```

---

## 4) 🖥️ Acessar a interface Web
Abra o navegador e acesse:
```
http://localhost:3000
```
**Credenciais padrão:** `admin` / `admin` (será solicitado trocar na primeira entrada).

> 🔐 **Altere a senha imediatamente!** Veja abaixo como redefinir via CLI, se necessário.

---

## 5) 📂 Caminhos importantes
- ⚙️ Config: `/etc/grafana/grafana.ini`  
- 📁 Dados: `/var/lib/grafana`  
- 🧾 Logs: `/var/log/grafana/` (ex.: `grafana.log`)  
- 📦 Conteúdo estático: `/usr/share/grafana`  
- 🔧 Provisionamento: `/etc/grafana/provisioning/`

---

## 6) 🧯 Solução de problemas
- 🔎 **Status & logs:** `systemctl status grafana-server` • `journalctl -u grafana-server -f`
- 🌐 **Porta em uso:** `ss -lntp | grep :3000`
- 🔐 **Reset de senha admin:** `sudo grafana-cli admin reset-admin-password 'NovaSenha'`
