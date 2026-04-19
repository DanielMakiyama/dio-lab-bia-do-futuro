# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

> [!TIP]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Os dados foram utilizados como fornecidos, com duas observações importantes:

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos são carregados uma única vez no início da sessão via Python, convertidos para texto estruturado e injetados no system prompt da Julia. Não há consulta dinâmica a banco de dados tudo entra como contexto estático na chamada à API.

```
import pandas as pd, json

def carregar_base_conhecimento():
    transacoes = pd.read_csv("data/transacoes.csv")
    historico  = pd.read_csv("data/historico_atendimento.csv")
    produtos   = json.load(open("data/produtos_financeiros.json"))
    perfil     = json.load(open("data/perfil_investidor.json"))
    return transacoes, historico, produtos, perfil
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são formatados como texto e inseridos no system prompt da Julia, na seção de contexto do cliente. O LLM recebe tudo junto com as instruções de persona e regras de segurança sem RAG, sem chamadas externas, sem banco de dados. Simples, auditável e suficiente para o escopo do desafio.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
