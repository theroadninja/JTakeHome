.PHONY: test format analyze run wheel clean

test:
	python3 -m pytest tests/*

format:
	python3 -m black encounters

analyze:
	bandit -r encounters -c pyproject.toml

run:
	API_KEY=testkey fastapi dev encounters/service

wheel:
	python3 -m build

clean:
	rm -rf build/ dist/ *.egg-info
