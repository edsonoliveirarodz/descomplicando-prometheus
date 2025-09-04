# 📊 Tipos de Métricas no Prometheus — Guia rápido com exemplos

Este guia resume os **quatro tipos de métricas do Prometheus** com definições claras, exemplos práticos e consultas PromQL úteis. Ideal para colar no repositório ou wiki do time.

> 🧭 **Visão geral**
> - **Gauge (Medidor):** valor que pode **subir ou descer** ao longo do tempo (ex.: uso de memória, temperatura, tamanho de fila).
> - **Counter (Contador):** valor **monotônico crescente** (só aumenta e pode **resetar** para 0 em reinícios).
> - **Histogram (Histograma):** **conta em buckets** pré-definidos + soma e contagem totais; permite **percentis no momento da query**.
> - **Summary (Resumo):** calcula **quantis (percentis) no cliente** + soma e contagem; excelente **precisão**, mas **agregação limitada**.

---

## 🟢 Gauge — *Medidor*
**O que é:** um valor que varia para cima ou para baixo.  
**Exemplos do dia a dia:** temperatura da cidade 🌡️, tamanho de filas 🧑‍🤝‍🧑, utilização de CPU/memória 🧠.

**Exemplo de métrica (fictícia):**
```txt
memory_usage{instance="localhost:8899", job="Primeiro Exporter"}
```

**Quando usar:**
- Estados atuais que podem aumentar **ou** diminuir (memória livre, conexões abertas, threads ativas).

**Consultas úteis (PromQL):**
```promql
# Valor atual
memory_usage

# Variação do gauge no período (pode ser positiva ou negativa)
delta(memory_usage[5m])

# Valor médio no período
avg_over_time(memory_usage[5m])
```

> 💡 **Dica:** `rate()` e `increase()` são pensados para **counters**. Para *gauges*, prefira `delta()`/`avg_over_time()`/`max_over_time()` conforme o caso.

---

## 🔵 Counter — *Contador*
**O que é:** um valor que **só cresce**; pode **voltar a 0** quando o processo reinicia (reset).  
**Exemplo típico:** número total de requisições, erros totais, bytes enviados.

**Exemplo de métrica:**
```txt
requests_total{instance="localhost:8899", job="Primeiro Exporter"}
```

**Boas práticas:**
- Use o sufixo **`_total`** para counters.
- **Sempre** consulte com `rate()` ou `increase()` para lidar com resets.

**Consultas úteis (PromQL):**
```promql
# Taxa de requisições por segundo (média móvel 5m)
rate(requests_total[5m])

# Total de requisições na última hora
increase(requests_total[1h])
```

> ⚠️ **Atenção:** o valor absoluto do counter é raramente útil; foque na **taxa** ou no **incremento** em uma janela de tempo.

---

## 🟣 Histogram — *Histograma*
**O que é:** registra observações em **buckets** (limites) e também mantém **_sum** e **_count**.  
**Uso comum:** latência de requisições, tamanhos de payload, duração de jobs.

**Séries expostas pelo histograma (ex.: latência):**
```txt
requests_duration_seconds_bucket{le="0.5", ...}
requests_duration_seconds_bucket{le="1", ...}
requests_duration_seconds_bucket{le="2.5", ...}
requests_duration_seconds_bucket{le="5", ...}
requests_duration_seconds_bucket{le="10", ...}
requests_duration_seconds_sum{...}
requests_duration_seconds_count{...}
```
- O rótulo **`le`** (\"less or equal\") indica o **limite superior** do bucket (ex.: `le="0.5"` → ≤ 0,5 s).  
- Clientes costumam expor *buckets padrão* cobrindo de milissegundos até ~10 s.

**Consultas úteis (PromQL):**
```promql
# P95 de latência em 5m (agregando todas as instâncias)
histogram_quantile(0.95,
  sum by (le) (rate(requests_duration_seconds_bucket[5m]))
)

# Latência média (sum/count)
sum(rate(requests_duration_seconds_sum[5m]))
/
sum(rate(requests_duration_seconds_count[5m]))
```
> ✅ **Vantagem:** você escolhe o percentil (**p50/p90/p95/p99**) **na query** e pode **agregar** por serviço/instância/região.

---

## 🟧 Summary — *Resumo*
**O que é:** calcula **quantis (percentis)** no próprio cliente/exporter; expõe também **_sum** e **_count**.  
**Séries comuns:**
```txt
# Exemplos (nomes variam conforme biblioteca)
requests_duration_seconds{quantile="0.5", ...}
requests_duration_seconds{quantile="0.9", ...}
requests_duration_seconds{quantile="0.99", ...}
requests_duration_seconds_sum{...}
requests_duration_seconds_count{...}
```

**Consultas úteis (PromQL):**
```promql
# Latência média via sum/count
rate(requests_duration_seconds_sum[5m]) 
/ rate(requests_duration_seconds_count[5m])
```

> ⚠️ **Limitação importante:** quantis de *summary* **não** podem ser **agregados com precisão** entre múltiplas instâncias (os quantis já vêm prontos do cliente). Se você precisa de percentis globais e agregáveis, prefira **histogram**.

---

## 🧪 Exemplos completos (mini‑receitas)

### 1) Erros por segundo (Counter)
```promql
sum by (job) (rate(app_errors_total[5m]))
```

### 2) Tamanho médio de fila (Gauge)
```promql
avg_over_time(queue_length[5m])
```

### 3) P99 de latência HTTP por rota (Histogram)
```promql
histogram_quantile(0.99,
  sum by (le, route) (rate(http_server_duration_seconds_bucket[5m]))
)
```

### 4) Latência média a partir de Summary
```promql
sum by (job) (rate(requests_duration_seconds_sum[5m]))
/
sum by (job) (rate(requests_duration_seconds_count[5m]))
```

---

## 🧷 Convenções de nomenclatura & rótulos
- ✅ **Counters:** use sufixo **`_total`** (ex.: `requests_total`).  
- 📐 **Unidades no nome:** `*_seconds`, `*_bytes`, `*_ratio`, etc.  
- 🐍 **snake_case** para nomes de métricas e rótulos.  
- 🏷️ Rótulos úteis: `job`, `instance`, `method`, `route`, `status_code` (evite alta cardinalidade!).

---

## 🆚 Tabela comparativa — *Histogram* vs *Summary*

| Critério | Histogram | Summary |
|---|---|---|
| Cálculo de percentis | **Na query** (`histogram_quantile`) | **No cliente/exporter** |
| Agregação entre instâncias | **Boa** (agregue buckets) | **Limitada** (quantis não agregáveis) |
| Precisão dos percentis | Depende da malha de **buckets** | **Alta** conforme a lib/algoritmo |
| Configuração | Definir **buckets** | Definir **quantis** |
| Quando escolher | Percentis agregados por serviço/região; flexibilidade na análise | Percentis locais por instância; custo/precisão controlados no cliente |

---

## 🎯 Resumo final
- **Gauge**: estado atual que pode subir/descer.  
- **Counter**: só aumenta; use `rate()`/`increase()` nas queries.  
- **Histogram**: buckets + sum/count; percentis na query e **boa agregação**.  
- **Summary**: quantis no cliente; **alta precisão** porém **agregação limitada**.

> 🤝 Dica prática: se você precisa de **p95/p99 globais** em vários pods/hosts, opte por **histogram**. Se a análise é **local** por instância e você quer percentis prontos, use **summary**.

---

### 📌 Exemplos do conteúdo original (mantidos e revisados)
- **Gauge:** `memory_usage{instance="localhost:8899", job="Primeiro Exporter"}`  
- **Counter:** `requests_total{instance="localhost:8899", job="Primeiro Exporter"}`  
- **Histogram (bucket):** `requests_duration_seconds_bucket{le="0.5"}` → **até 0,5 s**  
- **Summary (sum/count):** `requests_duration_seconds_sum{instance="localhost:8899", job="Primeiro Exporter"}`
