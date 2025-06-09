#!/usr/bin/env python3
import requests
import json

# Teste da API de contatos
print("=== TESTE DA API DE CONTATOS ===")

# Simular sessão de admin (isso normalmente seria feito através do login)
session = requests.Session()

# Primeiro, fazer login
login_url = "http://127.0.0.1:5000/admin/login"
login_data = {
    "email": "linkarcasa.automacoes@gmail.com",
    "password": "linkar2024@"  # Substitua pela senha correta
}

print("1. Fazendo login...")
login_response = session.post(login_url, data=login_data, allow_redirects=False)
print(f"Status do login: {login_response.status_code}")

if login_response.status_code == 302:
    print("Login bem-sucedido (redirecionamento)")
    
    # Agora testar a API de contatos
    print("\n2. Testando API de contatos...")
    contatos_url = "http://127.0.0.1:5000/api/contatos"
    contatos_response = session.get(contatos_url)
    
    print(f"Status da API de contatos: {contatos_response.status_code}")
    
    if contatos_response.status_code == 200:
        try:
            data = contatos_response.json()
            print(f"Contatos recebidos: {len(data.get('contatos', []))}")
            print(f"Dados de paginação: {data.get('pagination', {})}")
            if data.get('contatos'):
                print(f"Primeiro contato: {json.dumps(data['contatos'][0], indent=2)}")
        except Exception as e:
            print(f"Erro ao decodificar JSON: {e}")
            print(f"Resposta raw: {contatos_response.text}")
    else:
        print(f"Erro na API: {contatos_response.text}")
        
    # Testar também a rota de teste que criamos
    print("\n3. Testando rota de teste...")
    test_url = "http://127.0.0.1:5000/api/test-connection"
    test_response = session.get(test_url)
    print(f"Status do teste: {test_response.status_code}")
    if test_response.status_code == 200:
        try:
            test_data = test_response.json()
            print(f"Resultado do teste: {json.dumps(test_data, indent=2)}")
        except Exception as e:
            print(f"Erro ao decodificar JSON do teste: {e}")
            print(f"Resposta raw do teste: {test_response.text}")
    else:
        print(f"Erro no teste: {test_response.text}")
        
else:
    print(f"Falha no login: {login_response.text}")
