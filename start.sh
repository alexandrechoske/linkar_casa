#!/bin/bash

# Script para iniciar a aplicação LinkarCasa
# Data: 2025-06-09

echo "=== Iniciando LinkarCasa Admin System ==="

# Verificar se o Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Por favor, instale o Python primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado."
    echo "📝 Criando arquivo .env de exemplo..."
    cat > .env << EOL
# Configurações do Supabase
SUPABASE_URL=sua_url_do_supabase_aqui
SUPABASE_ANON_KEY=sua_chave_anonima_aqui
SUPABASE_SERVICE_KEY=sua_chave_de_servico_aqui

# Configurações da aplicação
SECRET_KEY=sua_chave_secreta_aqui
ADMIN_EMAILS=linkarcasa.automacoes@gmail.com

# Webhook (opcional)
WEBHOOK_URL=https://seu-webhook-url-aqui.com

# Configurações de ambiente
FLASK_ENV=development
FLASK_DEBUG=1
EOL
    echo "✅ Arquivo .env criado. Por favor, configure as variáveis antes de continuar."
    echo "📖 Edite o arquivo .env com suas configurações do Supabase."
    exit 1
fi

# Verificar se o virtual environment existe
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
if [ -d "venv" ]; then
    echo "🚀 Ativando ambiente virtual..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🚀 Ativando ambiente virtual..."
    source .venv/bin/activate
fi

# Instalar dependências
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
else
    echo "⚠️  Arquivo requirements.txt não encontrado."
    echo "📦 Instalando dependências básicas..."
    pip install flask python-dotenv supabase requests
fi

# Verificar se o diretório sqls existe
if [ ! -d "sqls" ]; then
    echo "📁 Criando diretório sqls..."
    mkdir sqls
fi

# Exibir informações de início
echo ""
echo "=== Configuração Concluída ==="
echo "🌐 Aplicação será iniciada em: http://localhost:5000"
echo "🔐 Admin login: http://localhost:5000/admin/login"
echo "📊 Dashboard: http://localhost:5000/admin/dashboard"
echo ""
echo "🚀 Iniciando servidor Flask..."
echo ""

# Iniciar a aplicação
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

python app.py
