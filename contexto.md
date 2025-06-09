LinkarCasa - Portal/Landing Page
Uma landing page moderna e responsiva para a LinkarCasa, focada em apresentar nossa solução de forma clara e envolvente.

Sobre o Projeto
A LinkarCasa é um serviço inovador e completo que oferece a infraestrutura e o gerenciamento para a sua casa inteligente, utilizando a poderosa plataforma Home Assistant. Nosso objetivo é simplificar a automação residencial, eliminando as preocupações com servidores, configurações complexas e manutenção.

Pontos Chave da Solução:
Infraestrutura Gerenciada: Fornecemos instâncias robustas de Home Assistant hospedadas em ambiente de nuvem, garantindo desempenho e estabilidade.

Conectividade Zigbee Avançada: Utilizamos a antena SLZB-06 para criar uma rede Zigbee potente e confiável, conectando todos os seus dispositivos (luzes, tomadas, sensores, etc.) à sua central Home Assistant.

Acesso Externo Personalizado: Oferecemos um domínio exclusivo para cada cliente (ex: suacasa.linkarcasa.com.br), permitindo controle total da sua casa de qualquer lugar do mundo de forma segura.

Serviço Completo: Da instalação física da antena e dispositivos iniciais à configuração das automações e dashboards, cuidamos de tudo para que você apenas aproveite os benefícios da sua casa inteligente.

Público-Alvo
Nosso serviço é ideal para pessoas e famílias que desejam o poder e a flexibilidade do Home Assistant, mas preferem não lidar com a complexidade técnica de montar e manter a infraestrutura por conta própria. Queremos transformar a automação residencial avançada em uma experiência acessível e sem preocupações.

# Configuração do Supabase Auth

## Visão Geral
A nova versão do sistema administrativo da LinkarCasa utiliza o Supabase Auth para autenticação segura, substituindo o sistema anterior de credenciais codificadas. Esta implementação melhora significativamente a segurança e a gestão de usuários administradores.

## Instruções de Configuração

### No Dashboard do Supabase:
1. Crie um projeto no Supabase (ou use um existente)
2. Ative a autenticação por email na seção "Authentication > Providers"
3. Opcional: Configure políticas de senha (comprimento mínimo, requisitos de complexidade)
4. Obtenha as chaves de API: URL, Service Key e Anon Key

### Na Aplicação LinkarCasa:
1. Execute o script de configuração:
   ```powershell
   .\Setup-Supabase-Auth.ps1
   ```
   O script irá guiá-lo na configuração das variáveis de ambiente necessárias.

2. Configure as tabelas no banco de dados:
   ```powershell
   python app.py
   # Acesse: http://localhost:5000/setup_database (após login)
   ```

3. Crie um usuário administrador:
   ```powershell
   python create_admin_user.py
   ```
   Siga as instruções para criar o usuário administrador inicial.

## Benefícios da Nova Autenticação
- **Segurança aprimorada**: Senhas armazenadas com hash e salt
- **Gerenciamento de usuários**: Facilidade para adicionar/remover administradores
- **Recuperação de senha**: Suporte a fluxos de recuperação de senha
- **Tokens JWT**: Autenticação baseada em tokens para maior segurança
- **Controle de acesso**: Restrição por email para maior segurança

## Próximos Passos
- Implementar dois fatores de autenticação (2FA)
- Adicionar login social (opcional)
- Desenvolver sistema de permissões granulares para diferentes funções administrativas