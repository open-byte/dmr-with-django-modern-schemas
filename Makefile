MANAGE := uv run python src/manage.py
FIXTURE := src/app/fixtures/library.json
DB := src/db.sqlite3

.PHONY: install run check test shell migrations migrate superuser load dump reset

install:
	uv sync

run:
	$(MANAGE) runserver

check:
	$(MANAGE) check

test:
	$(MANAGE) test app

shell:
	$(MANAGE) shell

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	DJANGO_SUPERUSER_PASSWORD=admin123 $(MANAGE) createsuperuser \
		--no-input --username admin --email admin@biblioteca.test

load:
	$(MANAGE) loaddata $(FIXTURE)

dump:
	$(MANAGE) dumpdata app.Author app.Book app.Review app.BookInstance app.User \
		--indent 2 --output $(FIXTURE)

reset:
	rm -f $(DB)
	$(MAKE) migrate
	$(MAKE) load
