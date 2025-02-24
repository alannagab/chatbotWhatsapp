# -*- coding: utf-8 -*-
import os
import re
import requests
from datetime import datetime, timedelta
from flask import Flask, request, render_template
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from functions.tools import training, system

load_dotenv()
conversation_history = []
conversation_histories = {}

app = Flask(__name__)

# Credenciais Twilio
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)

openai_api_key = os.getenv('OPENAI_API_KEY')

def parse_summary(summary_text):
    """Função para processar o texto do resumo e extrair informações em um dicionário."""
    summary_data = {
        'nome_cliente': 'Faltando',
        'numero_pedido': 'Faltando',
        'canal_compra': 'Faltando',
        'problema_relatado': 'Faltando',
        'resumo_atendimento': 'Resumo indisponível'
    }
    
    # Expressões regulares para capturar cada item numerado, permitindo valores longos e alfanuméricos
    patterns = {
        'nome_cliente': r"1\.\s*Nome do Cliente:\s*([\w\s]+)\s*(?=\d|$)",          
        'numero_pedido': r"2\.\s*Número do Pedido:\s*([\w\d\s]+)\s*(?=\d|$)",       
        'canal_compra': r"3\.\s*Canal de Compra:\s*([\w\s]+)\s*(?=\d|$)",           
        'problema_relatado': r"4\.\s*Problema Relatado:\s*([\w\s]+)\s*(?=\d|$)",    
        'resumo_atendimento': r"Resumo do atendimento:\s*(.*)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, summary_text, re.IGNORECASE)
        if match:
            summary_data[key] = match.group(1).strip() 

    print("Dados do Resumo Extraídos:", summary_data)
    return summary_data

def answer_conversation(incoming_message, conversation_history):
    """Função que envia uma mensagem diretamente para a API da OpenAI e retorna a resposta."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    # Adiciona a nova mensagem ao histórico
    conversation_history.append({"role": "user", "content": incoming_message})
    
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": training},  
        ] + conversation_history  
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Verifica se houve erros na chamada da API
        completion = response.json()
        
        # Pega a resposta gerada pela IA
        response_gpt = completion['choices'][0]['message']['content']
        return response_gpt
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao chamar a API da OpenAI: {http_err}")
        return "Desculpe, houve um erro ao processar sua solicitação."
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return "Desculpe, houve um erro ao processar sua solicitação."

def generate_summary(conversation_text):
    """Função para enviar o histórico de conversas para a OpenAI e gerar um resumo."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o",
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": f"Extraia as seguintes informações de forma clara: {conversation_text}"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        completion = response.json()
        # Extrai o conteúdo do resumo usando a chave "resumo" se disponível
        summary_text = completion['choices'][0]['message']['content']
        print (summary_text)
        return summary_text
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao chamar a API da OpenAI: {http_err}")
        return "Erro ao gerar o resumo"
    except Exception as e:
        print(f"Erro ao chamar a API da OpenAI: {e}")
        return "Erro ao gerar o resumo"

@app.route('/', methods=['POST'])
def whatsapp_reply():
    incoming_message = request.form.get('Body')
    sender = request.form.get('From')

    # Validação para ignorar mensagens vazias
    if not incoming_message or not sender:
        print("Mensagem ou remetente ausente, ignorando a requisição.")
        response = MessagingResponse()
        response.message("Desculpe, houve um problema ao processar sua mensagem.")
        return str(response)

    print(f"Mensagem recebida de {sender}: {incoming_message}")

    # Inicializa o histórico de conversas do remetente, se não existir
    if sender not in conversation_histories:
        conversation_histories[sender] = []

    conversation_histories[sender].append({
        "role": "user",
        "content": incoming_message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    conversation_history = [msg for msg in conversation_histories[sender] if msg.get('content')]

    print(f"Histórico de conversas com {sender}: {conversation_history}")

    try:
        response_gpt = answer_conversation(incoming_message, conversation_history)
    except Exception as e:
        print(f"Erro ao obter resposta da OpenAI: {e}")
        response_gpt = "Desculpe, houve um erro ao processar sua solicitação."

    # Adiciona a resposta ao histórico após validação
    conversation_history.append({"role": "assistant", "content": response_gpt})
    conversation_histories[sender] = conversation_history  # Atualiza o histórico do usuário

    # Responde ao usuário
    response = MessagingResponse()
    response.message(response_gpt)
    return str(response)

@app.route('/history/<sender>', methods=['GET'])
def view_conversation_history(sender):
    """Rota para visualizar o histórico completo de conversas de um cliente específico."""
    history = conversation_histories.get(sender, [])
    
    return render_template('conversation_history.html', sender=sender, history=history)

@app.route('/history/summary', methods=['GET'])
def get_summary_within_hour():
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    summaries = {}
    for sender, history in conversation_histories.items():
        filtered_history = [
            msg for msg in history 
            if 'timestamp' in msg and start_time <= datetime.strptime(msg['timestamp'], "%Y-%m-%d %H:%M:%S") <= end_time
        ]

        if filtered_history:
            conversation_text = "\n".join(
                [f"{item['role']}: {item['content']}" for item in filtered_history if item['content']]
            )
            summary_text = generate_summary(conversation_text)
            
            summary = parse_summary(summary_text)
            
            print(f"Resumo final para {sender}: {summary}")
            
            summaries[sender] = summary

    return render_template('summary.html', summaries=summaries)

if __name__ == '__main__':
    app.run(debug=True)
