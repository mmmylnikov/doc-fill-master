style:
	uv run ruff format && uv run ruff check --fix

types:
	uv run mypy .

check:
	make style && make types

app:
	cd src && uv run python main.py

pybabel_extract:
	pybabel extract \
		-F babel.cfg \
		-o doc_fill_master/messages.pot \
		--project="doc-fill-master" \
		--version="0.2.1" \
		--msgid-bugs-address="<not used>" \
		--copyright-holder="" \
		doc_fill_master/.

pybabel_init:
	pybabel init \
		-i doc_fill_master/messages.pot \
		-d doc_fill_master/translations \
		-l ru &&\
	pybabel init \
		-i doc_fill_master/messages.pot \
		-d doc_fill_master/translations \
		-l en

pybabel_compile:
	pybabel compile -d doc_fill_master/translations

pybabel_update:
	pybabel update -i doc_fill_master/messages.pot -d doc_fill_master/translations

build_app:
	pyinstaller \
		--onefile \
		--noconsole \
		src/main.py
