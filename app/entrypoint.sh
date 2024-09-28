#!/bin/bash

export FLASK_APP=__init__.py

# Modifier pg_hba.conf pour autoriser les connexions
echo "host    all             all             0.0.0.0/0            trust" >> /var/lib/postgresql/data/pg_hba.conf

# Recharger PostgreSQL pour appliquer les changements
pg_ctl reload -D /var/lib/postgresql/data

# Exécuter les migrations
flask db init
flask db migrate
flask db upgrade

flask run --host=0.0.0.0