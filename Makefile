
run:
	cd src && python3 -m app.main

test:
	@python -m pip install --upgrade pip || true
	@python -m pip install -e . || true
	pytest --cov=src --cov-report=term
