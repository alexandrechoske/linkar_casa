@echo off
REM Script para iniciar a aplicação LinkarCasa no Windows
REM Data: 2025-06-09

echo === Iniciando LinkarCasa Admin System ===

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Por favor, instale o Python primeiro.
    pause
    exit /b 1
)

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado.
    echo 📝 Criando arquivo .env de exemplo...
    (
        echo # Configurações do Supabase
        echo SUPABASE_URL=sua_url_do_supabase_aqui
        echo SUPABASE_ANON_KEY=sua_chave_anonima_aqui
        echo SUPABASE_SERVICE_KEY=sua_chave_de_servico_aqui
        echo.
        echo # Configurações da aplicação
        echo SECRET_KEY=sua_chave_secreta_aqui
        echo ADMIN_EMAILS=linkarcasa.automacoes@gmail.com
        echo.
        echo # Webhook (opcional^)
        echo WEBHOOK_URL=https://seu-webhook-url-aqui.com
        echo.
        echo # Configurações de ambiente
        echo FLASK_ENV=development
        echo FLASK_DEBUG=1
    ) > .env
    echo ✅ Arquivo .env criado. Por favor, configure as variáveis antes de continuar.
    echo 📖 Edite o arquivo .env com suas configurações do Supabase.
    pause
    exit /b 1
)

REM Verificar se o virtual environment existe
if not exist "venv" if not exist ".venv" (
    echo 🔧 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
if exist "venv" (
    echo 🚀 Ativando ambiente virtual...
    call venv\Scripts\activate.bat
) else if exist ".venv" (
    echo 🚀 Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
)

REM Instalar dependências
if exist "requirements.txt" (
    echo 📦 Instalando dependências...
    pip install -r requirements.txt
) else (
    echo ⚠️  Arquivo requirements.txt não encontrado.
    echo 📦 Instalando dependências básicas...
    pip install flask python-dotenv supabase requests
)

REM Verificar se o diretório sqls existe
if not exist "sqls" (
    echo 📁 Criando diretório sqls...
    mkdir sqls
)

REM Exibir informações de início
echo.
echo === Configuração Concluída ===
echo 🌐 Aplicação será iniciada em: http://localhost:5000
echo 🔐 Admin login: http://localhost:5000/admin/login
echo 📊 Dashboard: http://localhost:5000/admin/dashboard
echo.
echo 🚀 Iniciando servidor Flask...
echo.

REM Definir variáveis de ambiente
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Iniciar a aplicação
python app.py

pause
