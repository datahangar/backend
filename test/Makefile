.PHONY: test

test:
	@rm -rf data/ || true
	@mkdir -p data
	@PYTHONPATH=`pwd`/../src/ pytest -v
