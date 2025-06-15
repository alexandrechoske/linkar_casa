from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
import os
import math
import logging
from datetime import datetime, timedelta
from functools import wraps
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'seu-secret-key-aqui')

# Configurar logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuração do Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
# Inicialização do cliente Supabase com a chave de serviço para operações no backend
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None
# Cliente anônimo para autenticação
supabase_auth: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL and SUPABASE_ANON_KEY else None

# Lista de emails de admin permitidos
ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', 'linkarcasa.automacoes@gmail.com').split(',')

# Configuração do webhook
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://seu-webhook-url-aqui.com')

# Decorator para verificar login de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in') or not session.get('admin_user'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/politica-privacidade')
def politica_privacidade():
    return render_template('politica-privacidade.html')

@app.route('/termos-uso')
def termos_uso():
    return render_template('termos-uso.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            if not supabase_auth:
                logger.error("Tentativa de login falhou: Cliente Supabase não configurado")
                flash('Erro de conexão com o servidor. Verifique se as variáveis de ambiente SUPABASE_URL e SUPABASE_ANON_KEY estão configuradas corretamente.', 'error')
                return render_template('admin/login.html')
                
            # Tenta autenticar com o Supabase
            auth_response = supabase_auth.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Verifica se o usuário está na lista de admins permitidos
            user = auth_response.user
            if user and user.email in ADMIN_EMAILS:
                session['admin_logged_in'] = True
                session['admin_user'] = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.user_metadata.get('name', email) if hasattr(user, 'user_metadata') else email
                }
                logger.info(f"Login bem-sucedido para administrador: {email}")
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                logger.warning(f"Tentativa de acesso administrativo negada para: {email}")
                flash('Você não tem permissão de administrador.', 'error')
        except ValueError as e:
            # Erro de formato/validação
            logger.error(f"Erro de validação na autenticação: {str(e)}")
            flash('Formato de email ou senha inválido.', 'error')
        except KeyError as e:
            # Erro de chave ausente na resposta
            logger.error(f"Erro de chave na resposta de autenticação: {str(e)}")
            flash('Erro na resposta do servidor de autenticação. Contate o administrador.', 'error')
        except requests.exceptions.ConnectionError:
            # Erro de conexão com o Supabase
            logger.error("Erro de conexão com o Supabase")
            flash('Não foi possível conectar ao servidor de autenticação. Verifique sua conexão de internet.', 'error')
        except requests.exceptions.Timeout:
            # Timeout na requisição
            logger.error("Timeout na requisição de autenticação ao Supabase")
            flash('O servidor de autenticação está demorando para responder. Tente novamente mais tarde.', 'error')
        except Exception as e:
            # Captura erros específicos do Supabase
            error_message = str(e)
            logger.error(f"Erro de autenticação: {error_message}")
            
            if "invalid_grant" in error_message or "Invalid login credentials" in error_message:
                flash('Email ou senha incorretos. Por favor, verifique suas credenciais.', 'error')
            elif "User not found" in error_message:
                flash('Usuário não encontrado. Verifique se o email está correto.', 'error')
            elif "Email not confirmed" in error_message:
                flash('Email não confirmado. Por favor, verifique seu email para confirmar sua conta.', 'error')
            elif "Too many requests" in error_message:
                flash('Muitas tentativas de login. Por favor, aguarde alguns minutos antes de tentar novamente.', 'error')
            else:
                # Mensagem genérica para outros erros
                flash(f'Erro de autenticação: {error_message}', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    # Remove all session data
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    
    # If using Supabase, sign out the user
    try:
        if supabase_auth:
            supabase_auth.auth.sign_out()
    except Exception as e:
        print(f"Erro ao fazer logout no Supabase: {str(e)}")
    
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

# API Routes para CRUD de produtos
@app.route('/api/produtos', methods=['GET'])
@admin_required
def get_produtos():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        response = supabase.table('produtos').select('*').eq('ativo', True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos', methods=['POST'])
@admin_required
def create_produto():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        data = request.json
        response = supabase.table('produtos').insert(data).execute()
        return jsonify(response.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/<produto_id>', methods=['PUT'])
@admin_required
def update_produto(produto_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        data = request.json
        data['updated_at'] = datetime.now().isoformat()
        response = supabase.table('produtos').update(data).eq('id', produto_id).execute()
        return jsonify(response.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/<produto_id>', methods=['DELETE'])
@admin_required
def delete_produto(produto_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Soft delete - marca como inativo
        response = supabase.table('produtos').update({'ativo': False}).eq('id', produto_id).execute()
        return jsonify({'message': 'Produto removido com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/categorias', methods=['GET'])
def get_categorias():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        response = supabase.table('produtos').select('categoria, classe, tipo').eq('ativo', True).execute()
        
        categorias = {}
        for item in response.data:
            categoria = item['categoria']
            classe = item['classe']
            tipo = item['tipo']
            
            if categoria not in categorias:
                categorias[categoria] = {}
            if classe not in categorias[categoria]:
                categorias[categoria][classe] = set()
            categorias[categoria][classe].add(tipo)
        
        # Converter sets para listas
        for categoria in categorias:
            for classe in categorias[categoria]:
                categorias[categoria][classe] = list(categorias[categoria][classe])
        
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quotation', methods=['GET', 'POST'])
@admin_required
def api_quotation():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        if request.method == 'GET':
            # Buscar orçamentos salvos
            response = supabase.table('cotacoes').select('*').order('created_at', desc=True).execute()
            return jsonify(response.data)
        else:  # POST - Criar novo orçamento
            data = request.json
            
            # Validar dados mínimos
            if not data.get('produtos') or len(data.get('produtos', [])) == 0:
                return jsonify({'error': 'Nenhum produto selecionado'}), 400
            
            if not data.get('cliente_nome'):
                return jsonify({'error': 'Nome do cliente é obrigatório'}), 400
            
            # Preparar dados do orçamento
            cotacao_id = data.get('quotation_id', f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}")
              # Buscar configurações do sistema
            try:
                config_response = supabase.table('configuracoes').select('*').limit(1).execute()
                if config_response.data:
                    config = config_response.data[0]
                else:
                    # Configurações padrão se não existir
                    config = {
                        'taxa_servicos': 50.0,
                        'mao_de_obra': 35.0,
                        'margem_equipamentos': 30.0,
                        'mensalidade_plano': 149.90,
                        'incluir_mao_de_obra': True
                    }
            except:
                # Em caso de erro, usar configurações padrão
                config = {
                    'taxa_servicos': 50.0,
                    'mao_de_obra': 35.0,
                    'margem_equipamentos': 30.0,
                    'mensalidade_plano': 149.90,
                    'incluir_mao_de_obra': True
                }
              # Calcular totais
            subtotal_produtos = sum(float(p.get('valor_total', 0)) * p.get('quantidade', 1) for p in data.get('produtos', []))
            
            # Verificar se há horas de mão de obra definidas para cálculo personalizado
            has_mo_hours = any(p.get('mo_horas') for p in data.get('produtos', []))
            has_install_hours = any(p.get('tempo_instalacao') for p in data.get('produtos', []))
            
            # Taxa de serviços (configuração criação da aplicação)
            taxa_servicos = subtotal_produtos * (float(config.get('taxa_servicos', 50)) / 100)
            
            # Mão de obra (se habilitada)
            mo_valor = 0
            if config.get('incluir_mao_de_obra', True):
                if not has_mo_hours:
                    mo_valor = subtotal_produtos * (float(config.get('mao_de_obra', 35)) / 100)
                else:
                    # Calcular com base nas horas e na taxa horária
                    mo_valor = sum(
                        float(p.get('mo_horas', 0)) * 150 * p.get('quantidade', 1) 
                        for p in data.get('produtos', [])
                        if p.get('mo_horas')
                    )
            
            # Taxa de instalação permanece como estava (30% ou baseado em horas)
            if not has_install_hours:
                taxa_instalacao = subtotal_produtos * 0.3  # 30% do valor dos produtos
            else:
                # Calcular com base nas horas e na taxa horária
                taxa_instalacao = sum(
                    float(p.get('tempo_instalacao', 0)) * 120 * p.get('quantidade', 1) 
                    for p in data.get('produtos', [])
                    if p.get('tempo_instalacao')
                )
            
            # Valor total à vista (produtos + taxa de serviços + mão de obra)
            valor_total = subtotal_produtos + taxa_servicos + mo_valor
            
            # Mensalidade do plano (separada do valor à vista)
            mensalidade_plano = float(config.get('mensalidade_plano', 149.90))
            
            # Montar objeto para salvar
            cotacao = {
                'id': cotacao_id,
                'cliente_nome': data.get('cliente_nome', ''),
                'cliente_contato': data.get('cliente_contato', ''),
                'cliente_endereco': data.get('cliente_endereco', ''),
                'produtos': data.get('produtos', []),
                'subtotal_produtos': subtotal_produtos,
                'mo_valor': mo_valor,
                'taxa_instalacao': taxa_instalacao,
                'valor_total': valor_total,
                'parcelas': data.get('parcelas', 1),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            result = supabase.table('cotacoes').insert(cotacao).execute()
            
            return jsonify(result.data[0]), 201
            
    except Exception as e:
        print(f"Erro ao processar orçamento: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
        
@app.route('/api/quotation/<quotation_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_quotation_detail(quotation_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        if request.method == 'GET':
            # Buscar detalhes de um orçamento específico
            response = supabase.table('cotacoes').select('*').eq('id', quotation_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Orçamento não encontrado'}), 404
                
            return jsonify(response.data[0])
            
        elif request.method == 'PUT':
            # Atualizar orçamento
            data = request.json
            data['updated_at'] = datetime.now().isoformat()
              # Recalcular valores se necessário
            if 'produtos' in data:
                subtotal_produtos = sum(float(p.get('valor_total', 0)) * p.get('quantidade', 1) for p in data.get('produtos', []))
                has_mo_hours = any(p.get('mo_horas') for p in data.get('produtos', []))
                has_install_hours = any(p.get('tempo_instalacao') for p in data.get('produtos', []))
                
                if not has_mo_hours:
                    data['mo_valor'] = subtotal_produtos * 0.5
                else:
                    data['mo_valor'] = sum(
                        float(p.get('mo_horas', 0)) * 150 * p.get('quantidade', 1) 
                        for p in data.get('produtos', [])
                        if p.get('mo_horas')
                    )
                
                if not has_install_hours:
                    data['taxa_instalacao'] = subtotal_produtos * 0.3
                else:
                    data['taxa_instalacao'] = sum(
                        float(p.get('tempo_instalacao', 0)) * 120 * p.get('quantidade', 1) 
                        for p in data.get('produtos', [])
                        if p.get('tempo_instalacao')
                    )
                
                data['subtotal_produtos'] = subtotal_produtos
                data['valor_total'] = subtotal_produtos + data['mo_valor'] + data['taxa_instalacao']
            
            response = supabase.table('cotacoes').update(data).eq('id', quotation_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Orçamento não encontrado'}), 404
                
            return jsonify(response.data[0])
            
        else:  # DELETE
            # Excluir orçamento
            response = supabase.table('cotacoes').delete().eq('id', quotation_id).execute()
            return '', 204
            
    except Exception as e:
        print(f"Erro ao processar orçamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/contato', methods=['POST'])
def contato():
    try:
        # Captura os dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        mensagem = request.form.get('mensagem')
        
        # Dados para salvar no Supabase e enviar via webhook
        dados_contato = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'mensagem': mensagem,
            'origem': 'site',  # Adicionar origem explicitamente
            'status': 'novo'   # Adicionar status padrão
        }
        
        # Salvar dados no Supabase na nova tabela contatos_site
        contato_id = None
        if supabase:
            try:
                response = supabase.table('contatos_site').insert(dados_contato).execute()
                
                if response.data and len(response.data) > 0:
                    contato_id = response.data[0]['id']
                    print(f"Contato site salvo com ID: {contato_id}")
            except Exception as e:
                print(f"Erro ao salvar contato no Supabase: {e}")
                # Continue com o fluxo mesmo se falhar o salvamento no Supabase
        
        # Dados para enviar via webhook (incluindo o ID do contato)
        dados_webhook = {
            **dados_contato,
            'timestamp': datetime.now().isoformat(),
            'contato_id': contato_id
        }
        
        # Enviar dados para o webhook (se configurado)
        if WEBHOOK_URL and WEBHOOK_URL != 'https://seu-webhook-url-aqui.com':
            response = requests.post(WEBHOOK_URL, json=dados_webhook, timeout=10)
            
            if response.status_code == 200:
                return jsonify({
                    'status': 'success',
                    'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.',
                    'contato_id': contato_id
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Erro interno. Tente novamente em alguns instantes.'                }), 500
        else:
            # Se não tiver webhook configurado mas tiver salvo no Supabase
            if contato_id:
                return jsonify({
                    'status': 'success',
                    'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.',
                    'contato_id': contato_id
                })
            else:
                # Para desenvolvimento - apenas simula o envio
                print(f"Dados recebidos: {dados_webhook}")
                return jsonify({
                    'status': 'success',
                    'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
                })
            
    except Exception as e:
        print(f"Erro ao processar contato: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno. Tente novamente em alguns instantes.'
        }), 500

# Rotas de API para CRUD de produtos
@app.route('/api/products', methods=['GET','POST'])
def api_products():
    if request.method == 'GET':
        try:
            data = supabase.table('produtos').select('*').order('created_at', desc=True).execute()
            return jsonify(data.data)
        except Exception as e:
            print(f"Erro ao buscar produtos: {str(e)}")
            return jsonify({"error": str(e)}), 500
    else:
        try:
            payload = request.json
            # Adiciona timestamps
            payload['created_at'] = datetime.now().isoformat()
            payload['updated_at'] = datetime.now().isoformat()
              # Converte valores numéricos corretamente
            if 'valor_total' in payload:
                try:
                    payload['valor_total'] = float(payload['valor_total'])
                except (TypeError, ValueError):
                    payload['valor_total'] = 0
                    
            # Garante que campos numéricos sejam números válidos
            for field in ['mo_horas', 'tempo_instalacao']:
                if field in payload:
                    if payload[field] == '' or payload[field] is None:
                        payload[field] = None
                    else:
                        try:
                            payload[field] = float(payload[field])
                        except (TypeError, ValueError):
                            payload[field] = None
                            
            # Garante que campos de texto não sejam None
            for field in ['categoria', 'nome_produto', 'descricao', 'classe', 'tipo', 'link', 'imagem_produto',
                         'fabricante', 'modelo', 'protocolo', 'detalhes_tecnicos']:
                if field in payload and payload[field] is None:
                    payload[field] = ''
                    
            print(f"Inserindo produto: {payload}")
            result = supabase.table('produtos').insert(payload).execute()
            return jsonify(result.data[0]), 201
        except Exception as e:
            print(f"Erro ao criar produto: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/api/products/<uuid:id>', methods=['PUT','DELETE'])
@admin_required
def api_product_detail(id):
    if request.method == 'PUT':
        try:
            payload = request.json
            # Atualiza timestamp
            payload['updated_at'] = datetime.now().isoformat()
              # Garante que campos numéricos sejam números válidos
            for field in ['valor_total', 'mo_horas', 'tempo_instalacao']:
                if field in payload and payload[field] == '':
                    payload[field] = None
                    
            result = supabase.table('produtos').update(payload).eq('id', str(id)).execute()
            return jsonify(result.data[0])
        except Exception as e:
            print(f"Erro ao atualizar produto: {str(e)}")
            return jsonify({"error": str(e)}), 500
    else:
        try:
            supabase.table('produtos').delete().eq('id', str(id)).execute()
            return '', 204
        except Exception as e:
            print(f"Erro ao excluir produto: {str(e)}")
            return jsonify({"error": str(e)}), 500

# Páginas de administração separadas
@app.route('/admin/products')
@admin_required
def admin_products():
    return render_template('admin/products.html')

@app.route('/admin/quotation')
@admin_required
def admin_quotation():
    return render_template('admin/quotation.html')

@app.route('/admin/quotation/<orcamento_id>')
@admin_required
def admin_quotation_view(orcamento_id):
    """Visualizar um orçamento específico"""
    return render_template('admin/quotation.html', orcamento_id=orcamento_id)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

@app.route('/api/configuracoes', methods=['GET', 'POST'])
@admin_required
def api_configuracoes():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
        
        if request.method == 'GET':
            # Buscar todas as configurações
            response = supabase.table('configuracoes').select('chave, valor').execute()
              # Converter para formato de objeto
            config = {}
            for item in response.data:
                chave = item['chave']
                valor = item['valor']
                
                # Converter valores para os tipos corretos
                if chave in ['taxa_servicos_percentual', 'mao_obra_percentual', 'desconto_vista_percentual']:
                    config[chave.replace('_percentual', '')] = float(valor)
                elif chave == 'mensalidade_plano':
                    config[chave] = float(valor)
                elif chave == 'incluir_mao_de_obra':
                    config[chave] = valor.lower() == 'true'
                else:
                    config[chave] = valor
            
            # Garantir valores padrão se não existirem
            default_config = {
                'taxa_servicos': 50.0,
                'mao_de_obra': 35.0,
                'mensalidade_plano': 149.90,
                'desconto_vista': 5.0,
                'incluir_mao_de_obra': True
            }
            
            for key, default_value in default_config.items():
                if key not in config:
                    config[key] = default_value
            
            return jsonify(config)
        
        else:  # POST - Salvar configurações
            data = request.json
              # Mapeamento de campos para chaves da tabela
            field_mapping = {
                'taxa_servicos': 'taxa_servicos_percentual',
                'mao_de_obra': 'mao_obra_percentual',
                'mensalidade_plano': 'mensalidade_plano',
                'desconto_vista': 'desconto_vista_percentual',
                'incluir_mao_de_obra': 'incluir_mao_de_obra'
            }
              # Atualizar cada configuração
            for field, db_key in field_mapping.items():
                if field in data:
                    valor = str(data[field])
                    
                    # Verificar se a configuração já existe
                    existing = supabase.table('configuracoes').select('id').eq('chave', db_key).execute()
                    
                    if existing.data:
                        # Atualizar configuração existente
                        supabase.table('configuracoes').update({
                            'valor': valor,
                            'updated_at': datetime.now().isoformat()
                        }).eq('chave', db_key).execute()
                    else:
                        # Criar nova configuração
                        supabase.table('configuracoes').insert({
                            'chave': db_key,
                            'valor': valor,
                            'tipo': 'number' if field not in ['incluir_mao_de_obra'] else 'boolean',
                            'categoria': 'orcamento',
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }).execute()
            
            return jsonify({'success': True, 'message': 'Configurações salvas com sucesso'}), 200
            
    except Exception as e:
        print(f"Erro ao processar configurações: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contatos/stats', methods=['GET'])
@admin_required
def api_contatos_stats():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Obter estatísticas básicas
        # 1. Total de contatos
        total_response = supabase.table('contatos_site').select('id', count='exact').execute()
        total_contatos = total_response.count if hasattr(total_response, 'count') else 0
        
        # 2. Contatos novos (últimos 30 dias)
        trinta_dias_atras = (datetime.now() - timedelta(days=30)).isoformat()
        novos_response = supabase.table('contatos_site').select('id', count='exact').gte('created_at', trinta_dias_atras).execute()
        novos_contatos = novos_response.count if hasattr(novos_response, 'count') else 0
        
        # 3. Contatos por status
        status_counts = {}
        status_response = supabase.table('contatos_site').select('status').execute()
        if status_response.data:
            for item in status_response.data:
                status = item.get('status', 'novo')
                status_counts[status] = status_counts.get(status, 0) + 1
        
        # 4. Último contato recebido
        ultimo_response = supabase.table('contatos_site').select('*').order('created_at', desc=True).limit(1).execute()
        ultimo_contato = ultimo_response.data[0] if ultimo_response.data else None
        
        return jsonify({
            'total': total_contatos,
            'novos_30_dias': novos_contatos,
            'por_status': status_counts,
            'ultimo_contato': ultimo_contato
        })
        
    except Exception as e:
        print(f"Erro ao obter estatísticas de contatos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contatos', methods=['GET'])
@admin_required
def api_contatos_list():
    try:
        if not supabase:
            logger.error("Supabase não configurado")
            return jsonify({'error': 'Supabase não configurado'}), 500
        
        # Parâmetros para filtro e paginação
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_desc = request.args.get('sort_desc', 'true').lower() == 'true'
        
        # Iniciar a query
        query = supabase.table('contatos_site').select('*')
        
        # Aplicar filtro por status se fornecido
        if status:
            query = query.eq('status', status)
        
        # Aplicar ordenação
        query = query.order(sort_by, desc=sort_desc)
        
        # Aplicar paginação
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        
        # Executar a query
        response = query.execute()
        
        # Obter total de registros para paginação
        count_query = supabase.table('contatos_site').select('id', count='exact')
        if status:
            count_query = count_query.eq('status', status)
        count_response = count_query.execute()
        
        total = count_response.count if hasattr(count_response, 'count') else len(response.data)
        total_pages = math.ceil(total / per_page)
        
        result = {
            'contatos': response.data,
            'pagination': {
                'total': total,
                'per_page': per_page,
                'current_page': page,
                'total_pages': total_pages
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro em api_contatos_list: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/contatos/<contato_id>', methods=['PATCH'])
@admin_required
def api_contato_update(contato_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Obter dados do JSON enviado
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        # Campos permitidos para atualização
        allowed_fields = ['status', 'observacoes']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Atualizar o contato
        response = supabase.table('contatos_site').update(update_data).eq('id', contato_id).execute()
        
        if not response.data:
            return jsonify({'error': 'Contato não encontrado ou não foi possível atualizar'}), 404
            
        return jsonify({
            'status': 'success',
            'message': 'Contato atualizado com sucesso',
            'contato': response.data[0]
        })
        
    except Exception as e:
        print(f"Erro ao atualizar contato: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/setup_db', methods=['GET'])
@admin_required
def setup_db():
    """Rota de utilidade para configurar as tabelas no banco de dados"""
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # SQL para criar a tabela contatos com as permissões corretas
        sql_setup = """
        -- Verificar se a tabela contatos existe e criá-la se não existir
        CREATE TABLE IF NOT EXISTS contatos (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            mensagem TEXT,
            status TEXT DEFAULT 'novo',
            origem TEXT DEFAULT 'site',
            observacoes TEXT,
            ultima_interacao TIMESTAMP WITH TIME ZONE,
            responsavel TEXT,
            valor_orcamento NUMERIC(10,2),
            data_fechamento TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Desativar temporariamente o RLS para ajustar as políticas
        ALTER TABLE contatos DISABLE ROW LEVEL SECURITY;

        -- Excluir políticas existentes para evitar conflitos
        DROP POLICY IF EXISTS "Service role can do anything" ON contatos;
        DROP POLICY IF EXISTS "Anyone can insert contacts" ON contatos;
        DROP POLICY IF EXISTS "Service role can select all contacts" ON contatos;

        -- Permitir inserções de qualquer origem (incluindo anônimos)
        CREATE POLICY "Anyone can insert contacts" 
        ON contatos FOR INSERT
        TO anon, authenticated
        WITH CHECK (true);

        -- Permitir acesso de leitura para usuários autenticados
        CREATE POLICY "Service role can select all contacts"
        ON contatos FOR SELECT
        TO authenticated
        USING (true);

        -- Permitir atualizações para usuários autenticados
        CREATE POLICY "Service role can update contacts" 
        ON contatos FOR UPDATE
        TO authenticated
        USING (true);

        -- Reativar o RLS
        ALTER TABLE contatos ENABLE ROW LEVEL SECURITY;

        -- Atualizar índices
        CREATE INDEX IF NOT EXISTS idx_contatos_created_at ON contatos(created_at);
        CREATE INDEX IF NOT EXISTS idx_contatos_status ON contatos(status);
        
        -- Verificar se a função para atualizar o updated_at já existe
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        -- Criar o trigger (se não existir)
        DROP TRIGGER IF EXISTS update_contatos_updated_at ON contatos;
        CREATE TRIGGER update_contatos_updated_at
        BEFORE UPDATE ON contatos
        FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
        
        # Executar SQL diretamente via Postgres
        result = supabase.rpc('exec_sql', {'sql': sql_setup}).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Configuração do banco de dados concluída com sucesso.'
        })
        
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao configurar banco de dados: {str(e)}'
        }), 500

@app.route('/api/orcamentos', methods=['GET', 'POST'])
@admin_required
def api_orcamentos():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
        if request.method == 'GET':
            # Parâmetros para filtro e paginação
            status = request.args.get('status')
            cliente_nome = request.args.get('cliente_nome')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            sort_by = request.args.get('sort_by', 'created_at')
            sort_desc = request.args.get('sort_desc', 'true').lower() == 'true'
            
            # Iniciar a query
            query = supabase.table('orcamentos').select('*')
            
            # Aplicar filtros
            if status:
                query = query.eq('status', status)
            if cliente_nome:
                query = query.ilike('cliente_nome', f'%{cliente_nome}%')
            
            # Aplicar ordenação
            query = query.order(sort_by, desc=sort_desc)
            
            # Aplicar paginação
            offset = (page - 1) * per_page
            query = query.range(offset, offset + per_page - 1)
            
            # Executar a query
            response = query.execute()
            
            # Obter total de registros para paginação
            count_query = supabase.table('orcamentos').select('id', count='exact')
            if status:
                count_query = count_query.eq('status', status)
            if cliente_nome:
                count_query = count_query.ilike('cliente_nome', f'%{cliente_nome}%')
            count_response = count_query.execute()
            
            total = count_response.count if hasattr(count_response, 'count') else len(response.data)
            total_pages = math.ceil(total / per_page)
            
            return jsonify({
                'orcamentos': response.data,
                'pagination': {
                    'total': total,
                    'per_page': per_page,
                    'current_page': page,
                    'total_pages': total_pages
                }
            })
              
        else:  # POST - Criar novo orçamento
            data = request.get_json()
            
            # Validar dados mínimos
            if not data.get('produtos') or len(data.get('produtos', [])) == 0:
                return jsonify({'error': 'Produtos são obrigatórios'}), 400
                
            if not data.get('cliente_nome'):
                return jsonify({'error': 'Nome do cliente é obrigatório'}), 400
              # Buscar dados do contato se fornecido
            contato = None
            if data.get('contato_site_id'):
                contato_response = supabase.table('contatos_site').select('*').eq('id', data.get('contato_site_id')).execute()
                
                if contato_response.data:
                    contato = contato_response.data[0]
              # Gerar código de orçamento único
            codigo_orcamento = data.get('codigo_orcamento') or f"ORC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Preparar dados do orçamento
            orcamento_data = {
                'contato_site_id': data.get('contato_site_id'),
                'codigo_orcamento': codigo_orcamento,
                'cliente_nome': contato.get('nome', '') if contato else data.get('cliente_nome', ''),
                'cliente_email': contato.get('email', '') if contato else data.get('cliente_email', ''),
                'cliente_telefone': contato.get('telefone', '') if contato else data.get('cliente_telefone', ''),
                'cliente_endereco': data.get('cliente_endereco', ''),
                'produtos': data.get('produtos', []),
                'subtotal_produtos': data.get('subtotal_produtos', 0),
                'mo_valor': data.get('mo_valor', 0),
                'taxa_instalacao': data.get('taxa_instalacao', 0),
                'valor_total': data.get('valor_total', 0),
                'parcelas': data.get('parcelas', 1),
                'status': 'em_analise',
                'observacoes': data.get('observacoes', ''),
                'responsavel': data.get('responsavel', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Salvar no Supabase
            result = supabase.table('orcamentos').insert(orcamento_data).execute()
              # Atualizar status do contato para "orçamento_criado" se houver contato vinculado
            if data.get('contato_site_id'):
                supabase.table('contatos_site').update({'status': 'orçamento_criado'}).eq('id', data.get('contato_site_id')).execute()
            
            return jsonify(result.data[0]), 201
            
    except Exception as e:
        print(f"Erro ao processar orçamentos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orcamentos/<orcamento_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_orcamento_detail(orcamento_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        if request.method == 'GET':
            # Buscar detalhes de um orçamento específico
            response = supabase.table('orcamentos').select('*').eq('id', orcamento_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Orçamento não encontrado'}), 404
                
            return jsonify(response.data[0])
            
        elif request.method == 'PUT':
            # Atualizar orçamento
            data = request.json
            data['updated_at'] = datetime.now().isoformat()
            
            # Calcular valor total automaticamente se necessário
            if 'subtotal_produtos' in data and 'mo_valor' in data and 'taxa_instalacao' in data:
                data['valor_total'] = data['subtotal_produtos'] + data['mo_valor'] + data['taxa_instalacao']
            
            response = supabase.table('orcamentos').update(data).eq('id', orcamento_id).execute()
            
            if not response.data:
                return jsonify({'error': 'Orçamento não encontrado'}), 404
                
            return jsonify(response.data[0])
            
        else:  # DELETE
            # Excluir orçamento
            response = supabase.table('orcamentos').delete().eq('id', orcamento_id).execute()
            return '', 204
            
    except Exception as e:
        print(f"Erro ao processar orçamento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/setup_database', methods=['GET'])
@admin_required
def setup_database():
    """Configura a estrutura do banco de dados com as tabelas e políticas corretas"""
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Ler SQL do arquivo de tabelas
        with open('sqls/tabelas_contato_orcamento.sql', 'r') as file:
            sql_setup = file.read()
            
        # Ler SQL de configuração de autenticação
        try:
            with open('sqls/auth_permissions.sql', 'r') as file:
                auth_setup = file.read()
            sql_setup += "\n" + auth_setup
        except:
            print("Arquivo de configuração de autenticação não encontrado. Usando apenas configuração de tabelas.")
        
        # Dividir o SQL em comandos separados para executar um por um
        # Isso é necessário porque o método supabase.rpc('exec_sql', {'sql': sql}) pode não existir
        # ou não suportar múltiplos comandos
        
        # Aqui aplicamos cada comando SQL individualmente direto no banco de dados
        # Esta é uma abordagem mais segura
        try:
            # Criar tabela contatos_site
            supabase.from_('contatos_site').select('id').limit(1).execute()
            print("Tabela contatos_site já existe")
        except:
            # Se der erro é porque a tabela não existe, então criamos
            create_contatos = """
            CREATE TABLE IF NOT EXISTS contatos_site (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT NOT NULL,
                mensagem TEXT,
                status TEXT DEFAULT 'novo',
                origem TEXT DEFAULT 'site',
                observacoes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            supabase.sql(create_contatos).execute()
            print("Criada tabela contatos_site")
        
        # Configurar RLS para permitir inserções anônimas
        rls_config = """
        ALTER TABLE contatos_site DISABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS "Anyone can insert contacts site" ON contatos_site;
        CREATE POLICY "Anyone can insert contacts site" 
        ON contatos_site FOR INSERT
        TO anon, authenticated
        WITH CHECK (true);
        ALTER TABLE contatos_site ENABLE ROW LEVEL SECURITY;
        """
        supabase.sql(rls_config).execute()
        
        # Verificar se a tabela orcamentos existe
        try:
            supabase.from_('orcamentos').select('id').limit(1).execute()
            print("Tabela orcamentos já existe")
        except:
            create_orcamentos = """
            CREATE TABLE IF NOT EXISTS orcamentos (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                contato_site_id UUID REFERENCES contatos_site(id),
                codigo_orcamento TEXT UNIQUE,
                cliente_nome TEXT NOT NULL,
                cliente_email TEXT NOT NULL,
                cliente_telefone TEXT NOT NULL,
                cliente_endereco TEXT,
                produtos JSONB,
                subtotal_produtos NUMERIC(10,2),
                mo_valor NUMERIC(10,2),
                taxa_instalacao NUMERIC(10,2),
                valor_total NUMERIC(10,2),
                parcelas INTEGER DEFAULT 1,
                status TEXT DEFAULT 'em_analise',
                observacoes TEXT,
                responsavel TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            supabase.sql(create_orcamentos).execute()
            print("Criada tabela orcamentos")
        
        # Configurar RLS para tabela orcamentos
        rls_orcamentos = """
        ALTER TABLE orcamentos DISABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS "Admin can manage orcamentos" ON orcamentos;
        CREATE POLICY "Admin can manage orcamentos" 
        ON orcamentos
        TO authenticated
        USING (true);
        ALTER TABLE orcamentos ENABLE ROW LEVEL SECURITY;
        """
        supabase.sql(rls_orcamentos).execute()
        
        # Verificar se a tabela configuracoes existe
        try:
            supabase.from_('configuracoes').select('id').limit(1).execute()
            print("Tabela configuracoes já existe")
        except:
            # Se der erro é porque a tabela não existe, então criamos
            create_configuracoes = """
            CREATE TABLE IF NOT EXISTS configuracoes (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                taxa_servicos NUMERIC(5,2) DEFAULT 50.0,
                mao_de_obra NUMERIC(5,2) DEFAULT 35.0,
                margem_equipamentos NUMERIC(5,2) DEFAULT 30.0,
                mensalidade_plano NUMERIC(10,2) DEFAULT 149.90,
                periodo_amortizacao INTEGER DEFAULT 24,
                custo_vm NUMERIC(10,2) DEFAULT 12.50,
                incluir_mao_de_obra BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            supabase.sql(create_configuracoes).execute()
            print("Criada tabela configuracoes")
            
            # Inserir configuração padrão
            default_config = """
            INSERT INTO configuracoes (taxa_servicos, mao_de_obra, margem_equipamentos, mensalidade_plano, periodo_amortizacao, custo_vm, incluir_mao_de_obra)
            VALUES (50.0, 35.0, 30.0, 149.90, 24, 12.50, true);
            """
            supabase.sql(default_config).execute()
            print("Inserida configuração padrão")
        
        # Configurar RLS para tabela configuracoes
        rls_configuracoes = """
        ALTER TABLE configuracoes DISABLE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS "Admin can manage configuracoes" ON configuracoes;
        CREATE POLICY "Admin can manage configuracoes" 
        ON configuracoes
        TO authenticated
        USING (true);
        ALTER TABLE configuracoes ENABLE ROW LEVEL SECURITY;
        """
        supabase.sql(rls_configuracoes).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Configuração do banco de dados concluída com sucesso.'
        })
        
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao configurar banco de dados: {str(e)}'
        }), 500

@app.route('/api/estatisticas/contatos', methods=['GET'])
@admin_required
def api_estatisticas_contatos():
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
        
        # Buscar total de contatos
        response_total = supabase.table('contatos_site').select('count', count='exact').execute()
        total_contatos = response_total.count
        
        # Buscar contatos pendentes (novos ou em análise)
        response_pendentes = supabase.table('contatos_site').select('count', count='exact').in_('status', ['novo', 'em_analise']).execute()
        contatos_pendentes = response_pendentes.count
        
        # Buscar contatos dos últimos 7 dias
        sete_dias_atras = (datetime.now() - timedelta(days=7)).isoformat()
        response_recentes = supabase.table('contatos_site').select('count', count='exact').gte('created_at', sete_dias_atras).execute()
        contatos_recentes = response_recentes.count
        
        # Retornar estatísticas
        return jsonify({
            'total': total_contatos,
            'pendentes': contatos_pendentes,
            'recentes': contatos_recentes
        })
        
    except Exception as e:
        print(f"Erro ao obter estatísticas de contatos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contatos/<contato_id>', methods=['GET'])
@admin_required
def api_contato_detail(contato_id):
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Buscar o contato pelo ID
        response = supabase.table('contatos_site').select('*').eq('id', contato_id).execute()
        
        if not response.data:
            return jsonify({'error': 'Contato não encontrado'}), 404
            
        return jsonify(response.data[0])
        
    except Exception as e:
        print(f"Erro ao buscar detalhes do contato: {e}")
        return jsonify({'error': str(e)}), 500

# Rota de teste para debug
@app.route('/api/test-connection', methods=['GET'])
@admin_required
def test_connection():
    logger.info("=== TESTE DE CONEXÃO SUPABASE ===")
    try:
        if not supabase:
            logger.error("Cliente Supabase não inicializado")
            return jsonify({
                'status': 'error',
                'message': 'Cliente Supabase não inicializado',
                'supabase_url': SUPABASE_URL,
                'has_service_key': bool(SUPABASE_SERVICE_KEY)
            }), 500
        
        # Testar query simples
        logger.info("Testando query simples na tabela contatos_site...")
        response = supabase.table('contatos_site').select('id').limit(1).execute()
        logger.info(f"Query teste executada. Dados: {response.data}")
        
        # Verificar estrutura da tabela
        logger.info("Verificando estrutura da tabela...")
        schema_response = supabase.table('contatos_site').select('*').limit(1).execute()
        
        columns = []
        if schema_response.data and len(schema_response.data) > 0:
            columns = list(schema_response.data[0].keys())
        
        return jsonify({
            'status': 'success',
            'message': 'Conexão com Supabase OK',
            'test_data': response.data,
            'table_columns': columns,
            'row_count': len(response.data)
        })
        
    except Exception as e:
        logger.error(f"Erro no teste de conexão: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/admin/add_impostos_columns', methods=['GET'])
@admin_required
def add_impostos_columns():
    """Rota de utilidade para adicionar as colunas impostos e valor_total na tabela produtos"""
    try:
        if not supabase:
            return jsonify({'error': 'Supabase não configurado'}), 500
            
        # Ler o script SQL
        with open('sqls/add_impostos_valor_total_columns.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Dividir o script em comandos separados
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        results = []
        for command in commands:
            if command and not command.startswith('--'):
                try:
                    result = supabase.sql(command).execute()
                    results.append(f"✓ Comando executado: {command[:50]}...")
                except Exception as e:
                    # Alguns comandos podem falhar se a coluna já existir
                    if "already exists" in str(e) or "relation already exists" in str(e):
                        results.append(f"⚠ Já existia: {command[:50]}...")
                    else:
                        results.append(f"✗ Erro: {command[:50]}... - {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Script de adição de colunas executado',
            'details': results
        })
        
    except Exception as e:
        print(f"Erro ao executar script: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro ao executar script: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
