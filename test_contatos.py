#!/usr/bin/env python3
import requests
import json

# Configuração
BASE_URL = "http://127.0.0.1:5000"

def test_contatos():
    """Testar a API de contatos"""
    
    print("=== TESTE DA API DE CONTATOS ===")
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    # Primeiro, fazer login
    print("1. Fazendo login...")
    login_data = {
        'email': 'linkarcasa.automacoes@gmail.com',
        'password': 'sua_senha_aqui'  # Você precisa colocar a senha correta
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/admin/login", data=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code == 200 and "/admin/login" not in login_response.url:
            print("✅ Login bem-sucedido!")
        else:
            print("❌ Falha no login - vamos tentar mesmo assim...")
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        print("Continuando sem login...")
    
    # Testar conexão com Supabase
    print("\n2. Testando conexão com Supabase...")
    try:
        test_response = session.get(f"{BASE_URL}/api/test-connection")
        print(f"Status da conexão: {test_response.status_code}")
        
        if test_response.status_code == 200:
            test_data = test_response.json()
            print("✅ Conexão com Supabase OK!")
            print(f"Dados de teste: {json.dumps(test_data, indent=2)}")
        else:
            print(f"❌ Erro na conexão: {test_response.status_code}")
            print(f"Resposta: {test_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
    
    # Testar API de contatos
    print("\n3. Testando API de contatos...")
    try:
        contatos_response = session.get(f"{BASE_URL}/api/contatos")
        print(f"Status dos contatos: {contatos_response.status_code}")
        
        if contatos_response.status_code == 200:
            contatos_data = contatos_response.json()
            print("✅ API de contatos funcionando!")
            print(f"Total de contatos: {len(contatos_data.get('contatos', []))}")
            print(f"Paginação: {contatos_data.get('pagination', {})}")
            
            # Mostrar alguns contatos se existirem
            contatos = contatos_data.get('contatos', [])
            if contatos:
                print("\nPrimeiros contatos:")
                for i, contato in enumerate(contatos[:3]):
                    print(f"  {i+1}. {contato.get('nome', 'Nome não disponível')} - {contato.get('email', 'Email não disponível')}")
            else:
                print("Nenhum contato encontrado")
                
        else:
            print(f"❌ Erro na API de contatos: {contatos_response.status_code}")
            print(f"Resposta: {contatos_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar contatos: {e}")
    
    # Testar estatísticas
    print("\n4. Testando estatísticas...")
    try:
        stats_response = session.get(f"{BASE_URL}/api/contatos/stats")
        print(f"Status das estatísticas: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Estatísticas funcionando!")
            print(f"Estatísticas: {json.dumps(stats_data, indent=2)}")
        else:
            print(f"❌ Erro nas estatísticas: {stats_response.status_code}")
            print(f"Resposta: {stats_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar estatísticas: {e}")

if __name__ == "__main__":
    test_contatos()
