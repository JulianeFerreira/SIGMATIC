.DEFAULT_GOAL := help

COMPOSE := docker compose
EXEC    := $(COMPOSE) exec web

.PHONY: help env build up down restart logs migrate makemigrations superuser shell dbshell bash test clean

help: ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

env: ## Cria o .env a partir de .env.example (não sobrescreve se já existir)
	@test -f .env || cp .env.example .env

build: ## Builda as imagens Docker (web)
	$(COMPOSE) build

up: env ## Sobe os containers (web, db, mailhog); aplica migrações automaticamente
	$(COMPOSE) up -d

down: ## Derruba os containers
	$(COMPOSE) down

restart: ## Reinicia os containers
	$(COMPOSE) restart

logs: ## Acompanha os logs do container web
	$(COMPOSE) logs -f web

migrate: ## Aplica as migrações pendentes no banco
	$(EXEC) python manage.py migrate

makemigrations: ## Gera novas migrações a partir dos models
	$(EXEC) python manage.py makemigrations

superuser: ## Cria um superusuário Django
	$(EXEC) python manage.py createsuperuser

shell: ## Abre o shell interativo do Django
	$(EXEC) python manage.py shell

dbshell: ## Abre o shell do banco de dados (psql)
	$(EXEC) python manage.py dbshell

bash: ## Abre um shell dentro do container web
	$(EXEC) bash

test: ## Executa a suíte de testes Django
	$(EXEC) python manage.py test

clean: ## Remove caches e arquivos temporários locais
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
