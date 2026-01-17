import json
import re
import google.generativeai as genai
import pandas as pd
from config import API_KEY, ARQUIVO_CLIENTE, ARQUIVO_PRODUTOS, MODEL_NAME

# Configuração da API
genai.configure(api_key=API_KEY)

class EloAgent:
    def __init__(self):
        self.dados_cliente = self._carregar_json(ARQUIVO_CLIENTE)
        self.produtos = self._carregar_json(ARQUIVO_PRODUTOS)
        self.model = genai.GenerativeModel(MODEL_NAME)
        
        # System Prompt definido na etapa 3
        self.system_instruction = """
        Você é o Elo, assistente financeiro.
        1. Use os dados abaixo para responder.
        2. Se houver um bloco [CÁLCULO REALIZADO], use-o para explicar o rendimento.
        3. Nunca invente taxas.
        4. Seja educativo e cordial.
        """

    def _carregar_json(self, caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _calcular_simulacao(self, valor, dias=365):
        """
        Engine de Cálculo: Simula investimento no CDB Elo Plus (Padrão)
        """
        # Pega o primeiro produto para simulação (CDB)
        produto = self.produtos[0] 
        taxa_dia = (1 + produto['taxa_anual']) ** (1/365) - 1
        montante = valor * ((1 + taxa_dia) ** dias)
        lucro = montante - valor
        
        return {
            "produto": produto['nome'],
            "aporte": valor,
            "dias": dias,
            "valor_final": round(montante, 2),
            "lucro": round(lucro, 2),
            "taxa_usada": produto['taxa_texto']
        }

    def _detectar_intencao_calculo(self, mensagem):
        """
        Verifica se o usuário citou valores numéricos para investir.
        Ex: "Quanto rende 1000 reais?"
        """
        # Regex para encontrar números (ex: 1000, 500.00, 5k)
        numeros = re.findall(r'\d+', mensagem.replace(".", "").replace(",", ""))
        
        palavras_chave = ["rende", "investir", "simular", "aplicar"]
        tem_intencao = any(p in mensagem.lower() for p in palavras_chave)
        
        if tem_intencao and numeros:
            valor = float(numeros[0])
            # Filtro básico para evitar anos (2025) como valor
            if valor > 2030 or valor < 1900: 
                return valor
        return None

    def gerar_resposta(self, mensagem_usuario, historico_chat=[]):
        contexto_extra = ""
        
        # 1. Verifica se precisa acionar a Engine de Cálculo (Python)
        valor_detectado = self._detectar_intencao_calculo(mensagem_usuario)
        
        if valor_detectado:
            resultado = self._calcular_simulacao(valor_detectado)
            contexto_extra = f"""
            [CÁLCULO REALIZADO PELO SISTEMA]
            Produto: {resultado['produto']}
            Valor Investido: R$ {resultado['aporte']}
            Prazo: {resultado['dias']} dias
            Valor Bruto Final: R$ {resultado['valor_final']}
            Lucro Estimado: R$ {resultado['lucro']}
            Taxa Base: {resultado['taxa_usada']}
            [FIM CÁLCULO]
            Instrução: Explique esse resultado ao usuário de forma amigável.
            """

        # 2. Monta o Prompt Final (RAG)
        prompt_final = f"""
        {self.system_instruction}
        
        DADOS DO CLIENTE:
        {json.dumps(self.dados_cliente, ensure_ascii=False)}
        
        PRODUTOS DISPONÍVEIS:
        {json.dumps(self.produtos, ensure_ascii=False)}
        
        {contexto_extra}
        
        HISTÓRICO DA CONVERSA:
        {historico_chat[-3:] if historico_chat else "Início da conversa."}
        
        USUÁRIO: {mensagem_usuario}
        ELO:
        """
        
        # 3. Chama a LLM
        response = self.model.generate_content(prompt_final)
        return response.text