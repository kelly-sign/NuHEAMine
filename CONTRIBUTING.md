# Contributing

Contributions should preserve the existing database schema and API contracts
unless a migration and compatibility plan are included.

1. Create a focused branch and avoid committing `.env`, databases, uploads,
   logs, caches, generated model runs, `node_modules`, or `dist`.
2. Follow the existing Vue 3, Element Plus, Django REST Framework, and PEP 8
   conventions.
3. Add or update tests for behavioural changes.
4. Run `python manage.py check`, `python manage.py test predictions.tests`,
   `npm run lint`, and `npm run build` before submitting a change.
5. Document new model inputs, outputs, units, validation range, endpoint, model
   status, provenance, dependency versions, and limitations.

Do not commit third-party data or model artifacts unless redistribution rights
and source attribution have been confirmed.

