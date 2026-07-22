# Sigmatic

> **Sistema de Governança e Gestão de CTIC — SESP/PR**

O **Sigmatic** é um sistema informatizado e estruturado de forma modular, desenvolvido para auxiliar os processos de governança e gestão da Coordenadoria de Tecnologia da Informação e Comunicação (CTIC). A plataforma permite o registro, o acompanhamento e a consolidação das informações relacionadas às ações e iniciativas da área de TIC no âmbito da **Secretaria da Segurança Pública do Paraná (SESP/PR)**.

---

### 📋 Pré-requisitos

O projeto roda inteiramente via Docker — não é necessário instalar Python, PostgreSQL ou nenhuma dependência do `requirements.txt` na sua máquina. Antes de iniciar, certifique-se de ter instalado:
* **Docker** e **Docker Compose** (`docker compose`)
* **Git**
* **Make** (opcional, mas recomendado — os comandos abaixo usam os atalhos do `Makefile`)

---

### Configuração Local

#### 1. Clonar o Repositório

```bash
git clone https://github.com/Public-Brasil-Code/SIGMATIC
cd SIGMATIC
```

#### 2. Configurar as Variáveis de Ambiente (`.env`)

```bash
make env
# equivalente a: cp .env.example .env
```

Os valores padrão de `.env.example` já funcionam de imediato com o `docker compose` (Postgres e Mailhog inclusos). Ajuste-os apenas se quiser apontar para um banco ou SMTP diferentes.

> ⚠️ **Importante:** Nunca envie o arquivo `.env` para o repositório Git. Ele já está incluído no `.gitignore` por motivos de segurança para proteger suas credenciais.

#### 3. Subir a Aplicação

```bash
make up
# equivalente a: docker compose up -d
```

Esse comando builda a imagem (na primeira vez), sobe o PostgreSQL e o Mailhog, aplica as migrações do Django automaticamente e inicia o servidor com autoreload.

* Aplicação: `http://localhost:8000/`
* E-mails capturados pelo Mailhog: `http://localhost:8025/`

---

## Executando a Aplicação

Com os containers no ar, o dia a dia de desenvolvimento passa pelos atalhos do `Makefile` (todos executam dentro do container `web`):

| Comando | Descrição |
|---|---|
| `make up` | Sobe os containers (web, db, mailhog) |
| `make down` | Derruba os containers |
| `make logs` | Acompanha os logs da aplicação |
| `make migrate` | Aplica migrações pendentes |
| `make makemigrations` | Gera novas migrações a partir dos models |
| `make superuser` | Cria um superusuário Django |
| `make shell` | Abre o shell interativo do Django |
| `make dbshell` | Abre o `psql` do banco |
| `make bash` | Abre um shell dentro do container `web` |
| `make test` | Executa a suíte de testes |

Rode `make help` para a lista completa. O código-fonte é montado dentro do container (bind mount), então alterações nos arquivos locais refletem imediatamente, sem rebuild — só é preciso `make build` de novo ao alterar `requirements.txt` ou o `Dockerfile`.

---

## 👥 Contribuição e Desenvolvimento

* Sempre faça um `git pull origin DEV` antes de iniciar uma nova feature para garantir que está com o esquema de banco padronizado atualizado.
''
