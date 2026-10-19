# Sources and Disclosure - E-commerce Store

## Open-source libraries (used as dependencies, not copied)
| Library | License | Use |
|---|---|---|
| Django | BSD-3-Clause | Web framework/ORM |
| Django REST Framework | BSD-3-Clause | API layer |
| djangorestframework-simplejwt | MIT | JWT creation/validation |
| django-filter | BSD-3-Clause | Filter backend |
| drf-spectacular | BSD-3-Clause | OpenAPI/Swagger |
| redis-py | MIT | Redis client |
| psycopg | LGPL-3.0 | PostgreSQL driver |
| pytest, pytest-django | MIT / BSD-3-Clause | Testing |


Reused repository code: My Own project I started some weeks ago and left at UI and simple models - .
Original work: all application code in authen, products, inventory, carts, orders, test suite and documents. Except below:

## AI usage - EDIT TO BE TRUE
- Tool: Claude (Anthropic) - used in this weekend to Generate Tests, And other Delivereable files from My Source Code: reviewing the code for defects, drafting the test workbook text, generating README, schema.sql, api-spec.md, engineering-decisions.md, submission index, and PDF diagrams (architecture, ERD, API workflows), mock-payment.
- Not AI-assisted: Frontend UI, Complete Frontend (In the End Used AI to Check for errors, resolved), Backend Models, views, serializers .
- Verification done: ran pytest on 2026-10-19; checked each route against urls.py; There are some blocked tests and falied ones>.


## External pricing / technical claims
None (cost-and-scaling file not part of this submission - listed as incomplete).