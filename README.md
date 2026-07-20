# NuHEAMine

NuHEAMine is a web platform for managing, searching, analysing, and predicting
properties of nuclear high-entropy alloys. The repository contains the Vue 3
frontend, Django REST API, MySQL schema, hardness-prediction workflow, training
data, feature engineering code, and the deployed model artifact.

## Features

- JWT-based registration, login, and user management.
- CRUD, search, batch import, and export for materials, processes, mechanical
  properties, irradiation conditions, microstructures, irradiation hardening,
  irradiation embrittlement, irradiation creep, and references.
- Data visualisation for the database records.
- A deployed Vickers hardness prediction model.
- Uniform extension pages and versioned API paths for yield strength, tensile
  strength, phase composition, irradiation hardening, and irradiation
  embrittlement models that are still under development.

## Repository layout

```text
NuHEAMine/
├── backend/                 Django configuration and prediction API service
├── database/schema.sql      Empty MySQL schema; no research records are included
├── HV-Prediction/           Training, inference, data, and model artifacts
├── materials/               Material database models, serializers, and endpoints
├── predictions/             Prediction history model and API tests
├── public/                  Vue public assets
├── reports/                 Report-domain models
├── src/                     Vue 3 application
├── system/                  System-domain models
├── users/                   Custom user model and authentication endpoints
├── .env.example             Backend configuration template
├── requirements.txt         Runtime Python dependencies
└── requirements-training.txt Additional model-training dependencies
```

Generated folders such as `.venv`, `node_modules`, `dist`, `build`, caches,
logs, uploaded files, local secrets, and prediction temporary files are
intentionally excluded.

## Prerequisites

- CPython 3.8.x (the bundled model was tested with Python 3.8.19)
- MySQL 8.0
- Node.js 18 LTS and npm 9 or 10

The scientific Python packages are pinned because joblib/scikit-learn model
artifacts are sensitive to dependency-version changes.

## Local installation

### 1. Create the Python environment

Windows PowerShell:

```powershell
py -3.8 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux or macOS:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configure Django

Copy the example file and generate a unique secret key:

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

On Linux or macOS, use `cp .env.example .env`. Put the generated value in
`DJANGO_SECRET_KEY` and set the MySQL credentials in `.env`. Never commit the
resulting `.env` file.

### 3. Create and initialise MySQL

Run the following as a MySQL administrator, replacing the example password:

```sql
CREATE DATABASE high_entropy_alloys
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hea_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON high_entropy_alloys.* TO 'hea_user'@'localhost';
FLUSH PRIVILEGES;
```

Import the empty schema from a shell that supports input redirection:

```bash
mysql -u hea_user -p high_entropy_alloys < database/schema.sql
```

In Windows PowerShell, the same import can be invoked through `cmd`:

```powershell
cmd /c "mysql -u hea_user -p high_entropy_alloys < database\schema.sql"
```

The schema contains all 25 application and Django support tables but no
business records, user accounts, password hashes, prediction history, or other
live database data. Because this platform maps an existing research schema and
retains legacy migration history, mark the included schema as the migration
baseline after importing it:

```bash
python manage.py migrate --fake
python manage.py migrate
python manage.py createsuperuser
```

Only use `--fake` after importing `database/schema.sql` into an empty database.
The second command does not recreate those tables; it populates Django's
content-type and permission metadata after the migration baseline is recorded.

### 4. Install the frontend

```bash
npm ci
```

### 5. Start the platform

Use two terminals from the repository root:

```bash
python manage.py runserver 127.0.0.1:8000
```

```bash
npm run serve
```

Open <http://localhost:8080>. The development server proxies `/api` to Django.
Windows users may alternatively run `start.bat` after `.env`, `.venv`, and
`node_modules` have been prepared. Linux/macOS users may run `sh start.sh`.

## Hardness prediction

The deployed endpoint is:

```text
POST /api/v1/prediction/hardness
```

It requires a JWT access token and accepts non-negative compositions for the
15 supported elements:

```json
{
  "composition": {
    "Al": 20,
    "Co": 20,
    "Cr": 20,
    "Fe": 20,
    "Ni": 20
  }
}
```

Values may be atomic fractions or percentages; the inference workflow
normalises the supplied composition. A successful response contains
`Pred_HV`, and the authenticated request is recorded in `prediction_records`.

The following versioned endpoints are reserved for future models and currently
return a `developing` status:

```text
/api/v1/prediction/yield_strength
/api/v1/prediction/tensile_strength
/api/v1/prediction/phase
/api/v1/prediction/irradiation_hardening
/api/v1/prediction/irradiation_embrittlement
```

See [MODEL_CARD.md](MODEL_CARD.md) for artifact hashes, supported inputs, and
limitations.

## Re-training the hardness model

Install the additional packages, then run the script from its own directory:

```bash
python -m pip install -r requirements-training.txt
cd HV-Prediction
python train.py
```

Training output is intentionally ignored by Git except for the deployed model
directory. Review generated metrics and artifacts before replacing the
deployed pipeline.

## Verification

Backend and prediction checks:

```bash
python manage.py check
python manage.py test predictions.tests
```

Frontend checks:

```bash
npm run lint
npm run build
```

## Production notes

- Set `DJANGO_DEBUG=False`, use a fresh `DJANGO_SECRET_KEY`, restrict
  `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and
  `CSRF_TRUSTED_ORIGINS`, and enable secure cookies behind HTTPS.
- Serve the generated `dist` directory through a web server that sends `/api`
  requests to Django and falls back to `index.html` for Vue history routes.
- Do not use Django's development server in production.
- Load only model artifacts obtained from a trusted copy of this repository;
  Python pickle/joblib files can execute code when loaded.
- Back up the MySQL database and uploaded media separately. Neither is part of
  this source distribution.

## Research data and citation

The bundled training spreadsheet and elemental parameter tables are supplied
for reproducibility. Before assigning a DOI or redistributing the project,
repository maintainers should add the precise source publications and confirm
redistribution rights for each research dataset. Update `CITATION.cff` with the
authors and repository URL used for the final publication.

## License

This repository is released under the [MIT License](LICENSE). Third-party
dependencies remain subject to their own licenses.
