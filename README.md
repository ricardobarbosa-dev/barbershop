# 💈 Sistema de Gestão para Barbearia

Sistema completo de agendamentos para barbearia desenvolvido com
**Python e Django**, focado em regras reais de negócio, organização de
agenda e experiência do usuário.

------------------------------------------------------------------------

## 🚀 Funcionalidades

### 👤 Área do Cliente

-   Cadastro e login com autenticação
-   Agendamento online de serviços
-   Visualização de histórico
-   Cancelamento de agendamentos
-   Cobrança automática de taxa para cancelamento com menos de 30
    minutos

### ✂️ Área do Barbeiro

-   Dashboard personalizado
-   Visualização da agenda por data
-   Confirmação e conclusão de atendimentos
-   Cancelamento de horários
-   Bloqueio de períodos específicos da agenda

### 🛠️ Área Administrativa

-   Gerenciamento completo de usuários
-   Controle de serviços
-   Controle de barbeiros
-   Relatórios mensais
-   Controle financeiro
-   Sistema de pacotes de cortes
-   Atualização de status em tempo real

------------------------------------------------------------------------

## ⚙️ Tecnologias Utilizadas

-   Python 3
-   Django
-   HTML5
-   CSS3
-   JavaScript (puro)
-   SweetAlert2
-   SQLite (ambiente local)
-   Deploy compatível com PythonAnywhere

------------------------------------------------------------------------

## 🧠 Regras de Negócio Implementadas

-   Controle de permissões (Cliente / Staff / Admin)
-   Sistema de bloqueio de horários
-   Sistema de pacotes de cortes com controle de validade
-   Penalidade automática por cancelamento tardio
-   Controle de status do atendimento
-   Redirecionamento dinâmico por perfil
-   Proteção de rotas com decorators

------------------------------------------------------------------------

## 📂 Estrutura do Projeto

    barbershop/
    │
    ├── accounts/          # Autenticação e usuários
    ├── agendamentos/      # Sistema principal de agenda
    ├── core/              # Configurações do projeto
    ├── static/            # Arquivos estáticos
    ├── templates/         # Templates HTML
    └── manage.py

------------------------------------------------------------------------

## 🖥️ Como Rodar o Projeto Localmente

### 1️⃣ Clone o repositório

``` bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2️⃣ Crie e ative o ambiente virtual

``` bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Instale as dependências

``` bash
pip install -r requirements.txt
```

### 4️⃣ Rode as migrações

``` bash
python manage.py migrate
```

### 5️⃣ Crie um superusuário

``` bash
python manage.py createsuperuser
```

### 6️⃣ Execute o servidor

``` bash
python manage.py runserver
```

Acesse:

    http://127.0.0.1:8000/

------------------------------------------------------------------------

## 🔐 Controle de Acesso

-   Usuário comum → Cliente
-   Usuário is_staff=True → Barbeiro
-   Superuser → Admin

------------------------------------------------------------------------

## 📈 Objetivo do Projeto

Este sistema foi desenvolvido com foco em:

-   Aplicar boas práticas de backend
-   Implementar regras reais de negócio
-   Simular um sistema comercial real
-   Evoluir habilidades em Django
-   Criar um projeto pronto para produção

------------------------------------------------------------------------

## 🔮 Possíveis Melhorias Futuras

-   Integração com gateway de pagamento
-   Sistema de notificações por e-mail
-   Integração com WhatsApp API
-   Dashboard com gráficos avançados
-   Deploy automatizado com CI/CD

------------------------------------------------------------------------

## 👨‍💻 Autor

Desenvolvido por Ricardo Barbosa\

