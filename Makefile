PYTHON := ./.venv/Scripts/python.exe

.PHONY: bootstrap lint verify test

bootstrap:
	powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1

lint:
	powershell -ExecutionPolicy Bypass -File .\scripts\wiki.ps1 lint

verify:
	powershell -ExecutionPolicy Bypass -File .\scripts\wiki.ps1 verify

test:
	$(PYTHON) -m pytest -q
