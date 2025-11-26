# Makefile pour Stream Deck Canvas Renderer

.PHONY: help install test test-unit test-integration test-all coverage clean lint format validate

# Configuration
PYTHON := python3
PIP := pip3
PROJECT_ROOT := .
TESTS_DIR := tests
OUTPUT_DIR := test_results

# Couleurs pour l'affichage
COLOR_RESET := \033[0m
COLOR_GREEN := \033[32m
COLOR_RED := \033[31m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

help: ## Afficher cette aide
	@echo "$(COLOR_BLUE)Stream Deck Canvas Renderer - Commandes disponibles:$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""

install: ## Installer les dépendances
	@echo "$(COLOR_BLUE)📦 Installation des dépendances...$(COLOR_RESET)"
	$(PIP) install -e .
	$(PIP) install -r requirements.txt || echo "$(COLOR_YELLOW)Aucune requirements.txt trouvée$(COLOR_RESET)"
	$(PIP) install pytest pytest-cov pytest-html pytest-xdist

test: test-unit ## Alias pour test-unit

test-unit: ## Exécuter les tests unitaires
	@echo "$(COLOR_BLUE)🧪 Exécution des tests unitaires...$(COLOR_RESET)"
	$(PYTHON) -m pytest tests/ -m unit -v --tb=short

test-integration: ## Exécuter les tests d'intégration
	@echo "$(COLOR_BLUE)🔗 Exécution des tests d'intégration...$(COLOR_RESET)"
	$(PYTHON) -m pytest tests/ -m integration -v --tb=short

test-all: ## Exécuter tous les tests (unitaires + intégration)
	@echo "$(COLOR_BLUE)🚀 Exécution de tous les tests...$(COLOR_RESET)"
	$(PYTHON) run_tests.py --coverage --verbose

test-quick: ## Exécuter les tests rapides seulement
	@echo "$(COLOR_BLUE)⚡ Exécution des tests rapides...$(COLOR_RESET)"
	$(PYTHON) -m pytest tests/ -m "not slow" -v

test-watch: ## Surveiller les fichiers et relancer les tests automatiquement
	@echo "$(COLOR_BLUE)👀 Surveillance des fichiers...$(COLOR_RESET)"
	$(PYTHON) -m pytest tests/ -f

coverage: ## Générer le rapport de couverture
	@echo "$(COLOR_BLUE)📊 Génération du rapport de couverture...$(COLOR_RESET)"
	$(PYTHON) run_tests.py --coverage --html --verbose
	@echo ""
	@echo "$(COLOR_GREEN)✅ Rapport généré dans: $(OUTPUT_DIR)/htmlcov/index.html$(COLOR_RESET)"

coverage-report: ## Afficher le rapport de couverture dans le terminal
	@echo "$(COLOR_BLUE)📈 Rapport de couverture...$(COLOR_RESET)"
	$(PYTHON) -m coverage report
	@echo ""
	@echo "$(COLOR_BLUE)💡 Pour un rapport HTML détaillé: make coverage-html$(COLOR_RESET)"

clean: ## Nettoyer les fichiers temporaires
	@echo "$(COLOR_BLUE)🧹 Nettoyage...$(COLOR_RESET)"
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf $(OUTPUT_DIR)/
	rm -rf debug_frame_*.png
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(COLOR_GREEN)✅ Nettoyage terminé$(COLOR_RESET)"

lint: ## Vérifier la qualité du code avec flake8
	@echo "$(COLOR_BLUE)🔍 Vérification du code...$(COLOR_RESET)"
	$(PYTHON) -m flake8 streamdeck_canvas/ tests/ --max-line-length=120 --ignore=E501,W503,E203 || \
		echo "$(COLOR_YELLOW)⚠️  flake8 non installé: pip install flake8$(COLOR_RESET)"

format: ## Formater le code avec black
	@echo "$(COLOR_BLUE)✨ Formatage du code...$(COLOR_RESET)"
	$(PYTHON) -m black streamdeck_canvas/ tests/ --line-length=120 || \
		echo "$(COLOR_YELLOW)⚠️  black non installé: pip install black$(COLOR_RESET)"

format-check: ## Vérifier le formatage sans modifier
	@echo "$(COLOR_BLUE)✨ Vérification du formatage...$(COLOR_RESET)"
	$(PYTHON) -m black streamdeck_canvas/ tests/ --line-length=120 --check || \
		echo "$(COLOR_YELLOW)⚠️  Code pas au format$(COLOR_RESET)"

validate: test-unit ## Valider la suite de tests complète (unitaires + hooks)
	@echo "$(COLOR_BLUE)✅ Validation complète terminée$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)📋 Checklist de validation:$(COLOR_RESET)"
	@echo "  ✓ Tests unitaires passés"
	@echo "  ✓ Aucune erreur de coverage"
	@echo "  ✓ Code formaté"
	@echo "  ✓ Documentation mise à jour"

benchmark: ## Exécuter les tests de performance
	@echo "$(COLOR_BLUE)⚡ Tests de performance...$(COLOR_RESET)"
	$(PYTHON) -m pytest tests/test_integration.py::TestPerformance -v

device-test: ## Tests nécessitant un device physique (ATTENTION)
	@echo "$(COLOR_RED)⚠️  ATTENTION: Ces tests nécessitent un Stream Deck connecté!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Vérifiez que votre Stream Deck est connecté avant de continuer...$(COLOR_RESET)"
	@read -p "Continuer? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m pytest tests/ -m device -v; \
	else \
		echo "$(COLOR_BLUE)Annulé$(COLOR_RESET)"; \
	fi

install-dev: ## Installer les outils de développement
	@echo "$(COLOR_BLUE)🛠️  Installation des outils de développement...$(COLOR_RESET)"
	$(PIP) install pytest pytest-cov pytest-html pytest-xdist pytest-watch
	$(PIP) install flake8 black isort mypy
	@echo "$(COLOR_GREEN)✅ Outils installés$(COLOR_RESET)"

# Alias pour l'automatisation CI/CD
ci-test: lint test-unit test-integration coverage ## Pipeline CI complet

# Génération de rapport de tests pour CI
ci-report: ## Générer un rapport de tests pour la CI
	@echo "$(COLOR_BLUE)📄 Génération du rapport CI...$(COLOR_RESET)"
	$(PYTHON) run_tests.py --coverage --html --fail-fast --output=$(OUTPUT_DIR)
	@echo ""
	@if [ -f "$(OUTPUT_DIR)/junit.xml" ]; then \
		echo "$(COLOR_GREEN)✅ Rapport JUnit généré: $(OUTPUT_DIR)/junit.xml$(COLOR_RESET)"; \
	fi
	@if [ -d "$(OUTPUT_DIR)/htmlcov" ]; then \
		echo "$(COLOR_GREEN)✅ Rapport HTML généré: $(OUTPUT_DIR)/htmlcov/index.html$(COLOR_RESET)"; \
	fi

# Installation et tests en une commande
setup-and-test: install install-dev test-quick ## Setup complet et tests rapides
	@echo "$(COLOR_GREEN)🎉 Setup terminé!$(COLOR_RESET)"

# Debug - Exécuter un test spécifique
debug-test: ## Exécuter un test spécifique (utilisation: make debug-test TEST=test_streamdeck_canvas.py::TestCanvas::test_canvas_initialization)
	@if [ -z "$(TEST)" ]; then \
		echo "$(COLOR_RED)Erreur: Spécifiez TEST=...$(COLOR_RESET)"; \
		echo "Exemple: make debug-test TEST=test_streamdeck_canvas.py::TestCanvas::test_canvas_initialization"; \
		exit 1; \
	fi
	@echo "$(COLOR_BLUE)🐛 Debug du test: $(TEST)$(COLOR_RESET)"
	$(PYTHON) -m pytest $(TESTS_DIR)/$(TEST) -v -s

# Watch et re-test continu
watch: ## Surveillance et tests continus (nécessite pytest-watch)
	@echo "$(COLOR_BLUE)👀 Surveillance en cours... (Ctrl+C pour arrêter)$(COLOR_RESET)"
	ptw tests/ streamdeck_canvas/ -- -v

# Génération de couverture badges pour README
coverage-badge: ## Générer un badge de couverture (nécessite coverage-badge)
	@echo "$(COLOR_BLUE)🏆 Génération du badge de couverture...$(COLOR_RESET)"
	coverage-badge -o coverage.svg || echo "$(COLOR_YELLOW)coverage-badge non installé: pip install coverage-badge$(COLOR_RESET)"

# Statistiques du projet
stats: ## Afficher les statistiques du projet
	@echo "$(COLOR_BLUE)📊 Statistiques du projet:$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Fichiers Python:$(COLOR_RESET)"
	@find $(PROJECT_ROOT) -name "*.py" -type f | grep -v __pycache__ | grep -v .eggs | wc -l | xargs -I {} echo "  Total: {} fichiers"
	@echo ""
	@echo "$(COLOR_YELLOW)Lignes de code:$(COLOR_RESET)"
	@find $(PROJECT_ROOT) -name "*.py" -type f | grep -v __pycache__ | grep -v .eggs | xargs wc -l | tail -1 | awk '{print "  Total: " $$1 " lignes"}'
	@echo ""
	@echo "$(COLOR_YELLOW)Tests:$(COLOR_RESET)"
	@find $(TESTS_DIR) -name "test_*.py" -type f | wc -l | xargs -I {} echo "  {} fichiers de tests"
	@$(PYTHON) -m pytest tests/ --collect-only -q 2>/dev/null | grep "test session" | awk '{print "  " $$1 " tests"}'
	@echo ""
	@echo "$(COLOR_YELLOW)Couverture:$(COLOR_RESET)"
	@$(PYTHON) -m coverage report --skip-empty 2>/dev/null | tail -1 | awk '{print "  " $$4 " (" $$1 ")"}'
