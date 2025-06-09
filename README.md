# LinkarCasa - Sistema Administrativo

Sistema administrativo para a LinkarCasa, com funcionalidades para gerenciamento de produtos, contatos e geração de orçamentos para automação residencial.

## Sobre o Projeto

A LinkarCasa é um serviço inovador que oferece infraestrutura completa para Home Assistant, com foco em conectividade Zigbee robusta e acesso externo personalizado. Este sistema administrativo complementa o portal, permitindo o gerenciamento completo de produtos, especificações técnicas e orçamentos automatizados com cálculos avançados de mão de obra e instalação.

## Características

### Tecnologias Utilizadas
- **Backend**: Flask (Python)
- **Banco de dados**: Supabase (PostgreSQL)
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Autenticação**: Sessões Flask
- **API**: RESTful para CRUD de produtos e orçamentos

### Funcionalidades Principais
- ✅ Sistema de login administrativo
- ✅ Gerenciamento completo de produtos (CRUD)
- ✅ Categorização e filtragem de produtos
- ✅ Formulário de contato integrado ao Supabase
- ✅ Gestão de leads/contatos do site
- ✅ Conversão de contatos em orçamentos detalhados
- ✅ Sistema avançado de orçamentos
- ✅ Cálculos automáticos de taxas e valores
- ✅ Interface responsiva e moderna
- ✅ Impressão de orçamentos formatados

### Módulos do Sistema
1. **Autenticação**: Login seguro para área administrativa
2. **Dashboard**: Visão geral das operações
3. **Produtos**: Cadastro e gerenciamento completo
4. **Orçamentos**: Sistema de cotação inteligente
5. **FAQ**: Perguntas frequentes
6. **Contato**: Formulário de contato e informações

## Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### Método 1: Início Rápido (Recomendado)

Para Windows, use um dos scripts de inicialização:

**PowerShell (Recomendado para Windows):**
```powershell
.\start.ps1
```

**Prompt de Comando:**
```cmd
start.bat
```

**Git Bash/WSL:**
```bash
./start.sh
```

Os scripts irão automaticamente:
- Verificar se o Python está instalado
- Criar um ambiente virtual
- Instalar todas as dependências
- Criar um arquivo `.env` de exemplo (se não existir)
- Iniciar a aplicação

### Método 2: Instalação Manual

1. **Clone ou baixe o projeto**

2. **Crie um ambiente virtual** (recomendado):
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**:
   
   **Windows (PowerShell):**
   ```powershell
   venv\Scripts\Activate.ps1
   ```
   
   **Windows (CMD):**
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure o arquivo .env**:
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
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
   ```

6. **Execute a aplicação**:
   ```bash
   python app.py
   ```

### Acessando o Sistema

1. **Acesse o sistema**: Abra seu navegador e vá para `http://localhost:5000`

2. **Área administrativa**: `http://localhost:5000/admin/login`

3. **Dashboard**: `http://localhost:5000/admin/dashboard` (após login)

### Scripts de Inicialização

O projeto inclui scripts automatizados para facilitar a inicialização:

- `start.ps1` - Script PowerShell para Windows (recomendado)
- `start.bat` - Script batch para Windows 
- `start.sh` - Script bash para Linux/Mac/WSL

Estes scripts automaticamente:
- ✅ Verificam dependências
- ✅ Criam ambiente virtual
- ✅ Instalam pacotes necessários
- ✅ Criam arquivo .env de exemplo
- ✅ Iniciam a aplicação

## Configuração do Supabase

O sistema utiliza o Supabase como banco de dados. Você precisa criar um projeto no Supabase e configurar as seguintes tabelas:

### Tabela: produtos
```sql
CREATE TABLE produtos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nome_produto TEXT NOT NULL,
  categoria TEXT,
  classe TEXT,
  tipo TEXT,
  valor_brl DECIMAL(10,2) NOT NULL,
  descricao TEXT,
  imagem_produto TEXT,
  link TEXT,
  fabricante TEXT,
  modelo TEXT,
  protocolo TEXT,
  requer_hub TEXT,
  mo_horas DECIMAL(5,2),
  tempo_instalacao DECIMAL(5,2),
  detalhes_tecnicos TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ativo BOOLEAN DEFAULT TRUE
);
```

### Tabela: cotacoes
```sql
CREATE TABLE cotacoes (
  id TEXT PRIMARY KEY,
  cliente_nome TEXT NOT NULL,
  cliente_contato TEXT,
  cliente_endereco TEXT,
  produtos JSONB,
  subtotal_produtos DECIMAL(10,2) NOT NULL,
  mo_valor DECIMAL(10,2) NOT NULL,
  taxa_instalacao DECIMAL(10,2) NOT NULL,
  valor_total DECIMAL(10,2) NOT NULL,
  parcelas INTEGER DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: contatos
```sql
CREATE TABLE contatos (
  id SERIAL PRIMARY KEY,
  nome TEXT NOT NULL,
  email TEXT NOT NULL,
  telefone TEXT,
  mensagem TEXT,
  criado_em TIMESTAMP DEFAULT NOW()
);
```

## Estrutura do Projeto

```
linkar_casa/
├── app.py                         # Aplicação principal Flask
├── contexto.md                    # Contextualização do projeto
├── produtos_rows.sql              # Scripts SQL para os produtos
├── requirements.txt               # Dependências do projeto
├── start.sh                       # Script de inicialização
├── README.md                      # Este arquivo
├── static/                        # Arquivos estáticos
│   ├── css/
│   │   └── style.css              # Estilos customizados
│   ├── js/
│   │   └── script.js              # JavaScript customizado
│   └── medias/                    # Arquivos de mídia e logos
│       ├── Fundo Branco.png
│       ├── Logo - Fundo Transparente.png
│       └── Logo Only - Fundo Transparente.png
└── templates/                     # Templates HTML
    ├── index.html                 # Página principal
    ├── politica-privacidade.html
    ├── termos-uso.html
    └── admin/                     # Área administrativa
        ├── dashboard.html         # Painel principal
        ├── login.html             # Tela de login
        ├── products.html          # Gerenciamento de produtos
        └── quotation.html         # Sistema de orçamentos
```

## Funcionalidades Detalhadas

### Sistema de Login Administrativo
- Acesso seguro com credenciais administrativas
- Rotas protegidas por middleware de autenticação
- Sessões com Flask para controle de acesso

### Gerenciamento de Produtos
- CRUD completo de produtos
- Categorização e filtragem de produtos
- Especificações técnicas detalhadas
- Visualização em galeria por categorias
- Estatísticas rápidas dos produtos cadastrados
- Importação via CSV

### Sistema de Orçamentos
- Seleção intuitiva de produtos
- Busca e filtragem em tempo real
- Gerenciamento de quantidades
- Cálculos automáticos de valores:
  - Mão de obra (50% do valor ou baseado em horas)
  - Taxa de instalação (30% do valor ou baseado em horas)
- Parcelamento em até 12x
- Impressão de orçamentos formatados
- Salvamento de histórico de orçamentos
- Informações de clientes para orçamentos personalizados

### Módulo de Contatos
- Formulário de contato integrado
- Armazenamento de contatos no Supabase
- Conversão de contatos em orçamentos
- Notificações por e-mail (futuro)

## Contatos e Orçamentos

O sistema implementa uma estrutura de duas tabelas para gerenciar contatos e orçamentos:

### 1. Contatos (`contatos_site`)
Armazena os envios iniciais do formulário de contato:
- **ID**: Identificador único (UUID)
- **Nome**: Nome do cliente
- **Email**: Email de contato
- **Telefone**: Telefone de contato
- **Mensagem**: Mensagem enviada pelo formulário
- **Status**: Estado atual do contato (novo, em_analise, contatado, orçamento_criado, concluido, cancelado)
- **Origem**: Fonte do contato (site, indicação, etc.)
- **Timestamps**: Datas de criação e atualização

### 2. Orçamentos (`orcamentos`)
Armazena informações detalhadas para cotações baseadas em contatos:
- **ID**: Identificador único (UUID)
- **Contato_ID**: Referência ao contato original
- **Código**: Identificador amigável (ex: ORC-20250608120030)
- **Dados do Cliente**: Nome, email, telefone, endereço
- **Produtos**: Lista JSON de produtos incluídos no orçamento
- **Valores**: Subtotal de produtos, mão de obra, instalação, total
- **Status**: Estado do orçamento (em_analise, enviado, aprovado, rejeitado)
- **Observações**: Notas adicionais
- **Timestamps**: Datas de criação e atualização

### Fluxo de Trabalho

1. Cliente envia um formulário de contato pelo site
2. O contato é registrado na tabela `contatos_site` com status "novo"
3. Administrador visualiza o novo contato no dashboard
4. O status é atualizado conforme o andamento (em_analise, contatado)
5. Administrador cria um orçamento vinculado ao contato
6. O status do contato é atualizado para "orçamento_criado"
7. Orçamento é enviado ao cliente via email (opcional)
8. O status é atualizado para "concluido" ou "cancelado" conforme resultado

### Permissões de Banco de Dados

As tabelas utilizam Row Level Security (RLS) do Supabase:
- `contatos_site`: Permite inserção por usuários anônimos (formulário do site)
- `orcamentos`: Acesso restrito a usuários autenticados (administradores)

### Configuração Inicial

Use uma das rotinas de configuração para criar as tabelas:

**Windows (PowerShell):**
```powershell
.\setup_database.ps1
```

**Linux/Mac (Bash):**
```bash
./setup_database.sh
```

Ou acesse a rota `/setup_database` após login administrativo.

## Deploy

### Para produção:
1. Configure um servidor web (Nginx, Apache)
2. Use um WSGI server como Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Configure SSL/HTTPS
4. Defina as variáveis de ambiente apropriadas
5. Garanta que o banco de dados Supabase esteja configurado corretamente

### Plataformas Cloud:
O projeto está preparado para deploy em:
- Heroku
- Vercel
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Suporte e Manutenção

### Problemas Comuns
1. **Erro de dependências**: Execute `pip install -r requirements.txt`
2. **Porta em uso**: Altere a porta no `app.py` (padrão: 5000)
3. **Problemas com Supabase**: Verifique as credenciais no arquivo `.env`
4. **Erros de autenticação**: Certifique-se de que as sessões estão funcionando corretamente

### Logs
Para debug, ative o modo de desenvolvimento no Flask:
```python
app.run(debug=True)
```

## Tabela de Requisitos

| Feature                   | Status    | Descrição                                     |
|---------------------------|-----------|-----------------------------------------------|
| Login de Administrador    | ✅ Completo| Sistema de autenticação para área admin       |
| Gestão de Produtos        | ✅ Completo| CRUD completo de produtos com filtros         |
| Detalhes Técnicos         | ✅ Completo| Campo para especificações detalhadas          |
| Sistema de Cotação        | ✅ Completo| Cálculos automáticos de valores               |
| Taxas de MO e Instalação  | ✅ Completo| Cálculo baseado em percentual ou horas        |
| Impressão de Orçamentos   | ✅ Completo| Formato de impressão profissional             |
| Gestão de Contatos        | ✅ Completo| Formulário de contato e gestão de leads       |

## Licença

Este projeto foi desenvolvido para a LinkarCasa. Todos os direitos reservados.

---

**LinkarCasa - Automação residencial inteligente feita para você**

## Autenticação com Supabase

O sistema utiliza o Supabase Auth para autenticação segura de administradores:

### Configuração inicial

1. Configure as variáveis de ambiente no arquivo `.env`:
   ```
   SUPABASE_URL=https://sua-referencia-supabase.supabase.co
   SUPABASE_SERVICE_KEY=sua_service_key_do_supabase
   SUPABASE_ANON_KEY=sua_anon_key_do_supabase
   ADMIN_EMAILS=admin@seu-dominio.com,outro@seu-dominio.com
   ```

2. Execute o script para criar o usuário administrador:
   ```bash
   python create_admin_user.py
   ```

3. Siga as instruções para criar um usuário administrador no Supabase Auth.

### Segurança

- Senhas são armazenadas de forma segura no Supabase Auth
- A autenticação é gerenciada por tokens JWT
- Acesso administrativo é restrito aos emails na lista ADMIN_EMAILS
- Todas as rotas administrativas exigem autenticação

### Gestão de usuários

Para adicionar novos administradores:
1. Execute `python create_admin_user.py` novamente, ou
2. Use o dashboard do Supabase para criar usuários e adicione seus emails à variável `ADMIN_EMAILS`
