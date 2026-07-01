```markdown
# Sigmatic 📊
> **Sistema de Governança e Gestão de CTIC - SESP/PR**

---

## 📋 Descrição do Projeto

O **Sigmatic** é um sistema informatizado, estruturado de forma modular, desenvolvido para auxiliar os processos de governança e gestão da Coordenadoria de Tecnologia da Informação e Comunicação (CTIC). A plataforma permite o registro, o acompanhamento e a consolidação das informações relacionadas às ações e iniciativas da área de TIC no âmbito da **Secretaria da Segurança Pública do Paraná (SESP/PR)**.

---

## 🛠️ Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina local:
* **Python 3.11+**
* **PostgreSQL** (Instância local ativa)
* **Git**

---

## 🚀 Passo a Passo para Configuração Local

Siga as instruções abaixo para clonar o projeto, configurar o banco de dados padronizado, instalar as dependências e rodar as migrações do Django.

### 1. Clonar o Repositório
Abra o seu terminal e baixe a versão mais recente do código:
```bash
git clone [https://github.com/Public-Brasil-Code/SIGMATIC](https://github.com/Public-Brasil-Code/SIGMATIC)
cd SIGMATIC

```

### 2. Instalar as Dependências (Requirements)

Para que o código funcione corretamente, é necessário instalar todas as bibliotecas que o sistema utiliza. Recomenda-se a utilização de um ambiente virtual (`venv`):

```bash
# Criar o ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instalar as bibliotecas do código através do arquivo de requirements
pip install --upgrade pip
pip install -r requirements.txt

```

### 3. Configurar o Banco de Dados (PostgreSQL Local)

O banco de dados do projeto foi totalmente padronizado para o ambiente de desenvolvimento. Cada desenvolvedor precisará criar uma instância local do Postgres:

1. Abra o seu gerenciador do PostgreSQL (pgAdmin, DBeaver ou terminal via `psql`).
2. Crie um novo banco de dados local (ex: `sigmatic_db`).
3. Guarde o nome do usuário, senha, host e porta do seu banco local para utilizar na próxima etapa.

### 4. Configurar as Variáveis de Ambiente (`.env`)

Para que o Django se conecte ao seu banco local, você deve criar o arquivo de configuração de ambiente utilizando o modelo deixado no projeto:

1. Na raiz do projeto, localize o arquivo `.env.exemplo`.
2. Duplique ou renomeie o arquivo para **`.env`**:
```bash
cp .env.exemplo .env

```


3. Abra o arquivo `.env` recém-criado e preencha as variáveis com os dados correspondentes ao seu banco de dados PostgreSQL local.

> ⚠️ **Importante:** Nunca envie o arquivo `.env` para o repositório Git. Ele já está incluído no `.gitignore` por motivos de segurança para proteger suas credenciais locais.

### 5. Executar as Migrações do Banco

Com o banco criado e o `.env` configurado, prepare e aplique a estrutura das tabelas do Django rodando os comandos:

```bash
# Detectar novas alterações nos modelos
python manage.py makemigrations

# Aplicar as alterações e criar as tabelas no banco local
python manage.py migrate

```

---

## 🏃‍♂️ Executando a Aplicação

Após concluir a instalação das dependências, configuração do `.env` e execução do `migrate`, inicie o servidor de desenvolvimento do Django:

```bash
python manage.py runserver

```

O sistema estará disponível localmente no endereço: `http://127.0.0.1:8000/`

---

## 👥 Contribuição e Desenvolvimento

* Sempre faça um `git pull origin <dev>` antes de iniciar uma nova feature para garantir que está com o esquema de banco padronizado atualizado.
''
