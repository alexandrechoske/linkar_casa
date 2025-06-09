# Script PowerShell para iniciar a aplicação LinkarCasa
# Data: 2025-06-09

Write-Host "=== Iniciando LinkarCasa Admin System ===" -ForegroundColor Cyan

# Verificar se o Python está instalado
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado. Por favor, instale o Python primeiro." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado." -ForegroundColor Yellow
    Write-Host "📝 Criando arquivo .env de exemplo..." -ForegroundColor Yellow
    
    $envContent = @"
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
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Arquivo .env criado. Por favor, configure as variáveis antes de continuar." -ForegroundColor Green
    Write-Host "📖 Edite o arquivo .env com suas configurações do Supabase." -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o virtual environment existe
if (-not (Test-Path "venv") -and -not (Test-Path ".venv")) {
    Write-Host "🔧 Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativar ambiente virtual
if (Test-Path "venv") {
    Write-Host "🚀 Ativando ambiente virtual..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv") {
    Write-Host "🚀 Ativando ambiente virtual..." -ForegroundColor Green
    & ".venv\Scripts\Activate.ps1"
}

# Instalar dependências
if (Test-Path "requirements.txt") {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "⚠️  Arquivo requirements.txt não encontrado." -ForegroundColor Yellow
    Write-Host "📦 Instalando dependências básicas..." -ForegroundColor Yellow
    pip install flask python-dotenv supabase requests
}

# Verificar se o diretório sqls existe
if (-not (Test-Path "sqls")) {
    Write-Host "📁 Criando diretório sqls..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Name "sqls"
}

# Exibir informações de início
Write-Host ""
Write-Host "=== Configuração Concluída ===" -ForegroundColor Green
Write-Host "🌐 Aplicação será iniciada em: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🔐 Admin login: http://localhost:5000/admin/login" -ForegroundColor Cyan
Write-Host "📊 Dashboard: http://localhost:5000/admin/dashboard" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Iniciando servidor Flask..." -ForegroundColor Green
Write-Host ""

# Definir variáveis de ambiente
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "1"

# Iniciar a aplicação
try {
    python app.py
} catch {
    Write-Host "❌ Erro ao iniciar a aplicação: $_" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
}

Read-Host "Pressione Enter para sair"
