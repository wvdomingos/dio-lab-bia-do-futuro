# Base de Conhecimento: WVD

## Dados Utilizados

Para garantir que o assistente "WVD" forneça respostas precisas e simulações matemáticas corretas, optei por criar datasets sintéticos (mockados) em formato JSON. O formato JSON foi escolhido pela facilidade de manipulação em Python (dicionários) e leitura clara pela LLM.

Os arquivos estão localizados na pasta `data`:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

> [!NOTE]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Estratégia de Integração

### Como os dados são usados no prompt?
Adotamos uma estratégia de **RAG Simples (Retrieval-Augmented Generation)** filtrado por regras de negócio, para evitar alucinação e economizar tokens:

1.  **Identificação de Intenção:** Se o usuário pergunta sobre "Investimentos", o código Python filtra apenas produtos da categoria "Investimento" no JSON.
2.  **Injeção Seletiva:** Apenas os produtos filtrados são injetados no System Prompt.
3.  **Resultado do Cálculo:** Se houver uma solicitação de simulação (ex: "Quanto rende 1000 reais?"), o Python executa a conta primeiro e insere apenas o resultado final no prompt para a LLM explicar.

---

## Exemplo de Contexto Montado

Abaixo, um exemplo de como o prompt é construído dinamicamente quando o usuário João (Perfil Conservador) pergunta: *"Qual a melhor opção para guardar meu dinheiro por 1 ano?"*.

O sistema filtra produtos de risco "Baixo" e monta o seguinte bloco para a LLM:

```text
--- INÍCIO DO CONTEXTO DE DADOS ---

[DADOS DO CLIENTE]
Nome: João Silva
Perfil de Investidor: Conservador
Saldo Atual: R$ 15.000,00

[PRODUTOS DISPONÍVEIS - FILTRO: RISCO BAIXO]
1. Produto: CDB WVD Plus
   - Tipo: Renda Fixa
   - Rentabilidade: 110% do CDI
   - Liquidez: Apenas no vencimento (365 dias)
   - Risco: Baixo (Garantia FGC)
   
2. Produto: Tesouro Selic 2029
   - Tipo: Tesouro Direto
   - Rentabilidade: Taxa Selic + 0.15%
   - Liquidez: Diária (D+1)
   - Risco: Soberano (Mínimo)

[INSTRUÇÃO]
O cliente pediu uma recomendação. Como o perfil é conservador, explique as duas opções acima comparando a "Liquidez" (já que ele pediu 1 ano, o CDB é viável, mas o Tesouro oferece liquidez diária). Não invente outros produtos.

--- FIM DO CONTEXTO ---
```
