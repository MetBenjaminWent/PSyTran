all: install

install:
	@echo "Installing psyacc..."
	@python3 -m pip install -r requirements.txt
	@python3 -m pip install -e .
	@echo "Done."

lint:
	@echo "Checking lint..."
	@flake8 --ignore=E501,E226,E402,E741,F403,F405,W503
	@echo "PASS"

# TODO: Fix testing so it can be done from this level
test: lint
	@echo "testing psyacc..."
	@cd test && python3 -m pytest -v
	@echo "PASS"
