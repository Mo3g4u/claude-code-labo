# Todo App Development Makefile

.PHONY: help setup start stop test lint format clean

help: ## Show help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "Setting up development environment..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@echo "Setup completed!"

start: ## Start local development environment
	@echo "Starting LocalStack..."
	docker-compose up -d localstack
	@echo "Waiting for LocalStack to be ready..."
	sleep 10
	@echo "Starting SAM local API..."
	cd backend && sam local start-api --docker-network todo-app-local --parameter-overrides "ParameterKey=TableName,ParameterValue=todos" &
	@echo "Development environment started!"

stop: ## Stop local development environment
	@echo "Stopping development environment..."
	docker-compose down
	@echo "Development environment stopped!"

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "All tests completed!"

test-backend: ## Run backend tests only
	cd backend && pytest

test-frontend: ## Run frontend tests only
	cd frontend && npm test

lint: ## Run linting
	@echo "Running backend linting..."
	cd backend && ruff check src
	@echo "Running frontend linting..."
	cd frontend && npm run lint
	@echo "Linting completed!"

backend-lint: ## Run backend linting only
	cd backend && ruff check src

frontend-lint: ## Run frontend linting only
	cd frontend && npm run lint

format: ## Format code
	@echo "Formatting backend code..."
	cd backend && ruff format src
	@echo "Formatting frontend code..."
	cd frontend && npm run lint:fix
	@echo "Code formatting completed!"

clean: ## Clean up development environment
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "Cleanup completed!"

# Development shortcuts
dev-backend: ## Start backend development server
	cd backend && sam local start-api --docker-network todo-app-local --parameter-overrides "ParameterKey=TableName,ParameterValue=todos"

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

# LocalStack management
localstack-up: ## Start LocalStack
	docker-compose up -d localstack
	@echo "Waiting for LocalStack to be ready..."
	sleep 10

localstack-down: ## Stop LocalStack
	docker-compose down

backend-start: ## Start SAM Local API
	cd backend && sam local start-api --docker-network todo-app-local --parameter-overrides "ParameterKey=TableName,ParameterValue=todos"

frontend-start: ## Start frontend development server
	cd frontend && npm run dev

# Testing shortcuts
tdd-backend: ## Run backend tests in watch mode
	cd backend && pytest-watch

tdd-frontend: ## Run frontend tests in watch mode
	cd frontend && npm run test -- --watch

# Deployment
deploy: ## Deploy to AWS
	cd backend && sam deploy --guided
	@echo "Deployment completed!"

build: ## Build for production
	@echo "Building backend..."
	cd backend && sam build
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build completed!"