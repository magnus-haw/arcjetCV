# arcjetCV documentation (django-wiki)

This is the documentation site for arcjetCV, powered by [django-wiki](https://github.com/django-wiki/django-wiki). All user/operator docs should live here rather than in Sphinx/MkDocs.

## Quick start
1) Create and activate a virtual environment.

```bash
cd wiki_site
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Apply migrations and create an admin user.

```bash
python manage.py migrate
python manage.py createsuperuser
```

3) Run the dev server.

```bash
python manage.py runserver
```

Browse to http://127.0.0.1:8000/ to view and edit the wiki. Log in with the admin user you created to add or edit pages. Static files are collected to `wiki_site/static/` and uploads go to `wiki_site/media/` when running locally.

## Notes
- This configuration is for local/demo use (DEBUG=True, sqlite DB, permissive hosts). Harden settings before deploying.
- The wiki uses built-in auth views at `/accounts/` (login/logout/password reset). Admin is available at `/admin/`.

## Using the wiki for documentation
- Create a root page (e.g., "arcjetCV Documentation") and add child pages for topics like installation, GUI usage, calibration workflows, and troubleshooting.
- Use the Attachments plugin to upload images or small assets; larger videos should live elsewhere with links.
- Prefer the web editor for edits; you can also paste Markdown and let django-wiki convert formatting.
- If migrating content from the old Sphinx/MkDocs docs, paste the text into new pages and re-upload only the assets you need.
- Back up the SQLite DB (`wiki_site/db.sqlite3`) and `media/` uploads if you want to preserve content between runs.
