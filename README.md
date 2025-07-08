# pyLETS
[![Django CI](https://github.com/suhailvs/pylets/actions/workflows/django.yml/badge.svg)](https://github.com/suhailvs/pylets/actions/workflows/django.yml)
[![Python Version](https://img.shields.io/badge/python-3.12-brightgreen.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-5.1-brightgreen.svg)](https://djangoproject.com)
[![Django Rest Framework Version](https://img.shields.io/badge/django--rest--framework-3.15.2-brightgreen.svg)](https://www.django-rest-framework.org/)

pyLETS is an open source local exchange trading system (http://en.wikipedia.org/wiki/Local_Exchange_Trading_Systems) using python. LETS eliminates the systemic trap of needing endless growth to pay unpayable debts.

## Run it locally

Run the following in your terminal:
```
curl -s https://raw.githubusercontent.com/suhailvs/pylets/main/pylets.sh | bash
```
visit: http://localhost:8000/

## Run Tests

Run the following in your terminal:
+ to run unittests: `./manage.py test`
+ to run functional tests: `pytest`
