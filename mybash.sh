#!/bin/bash

# https://github.com/bobbyiliev/introduction-to-bash-scripting
refreshdb="refreshdb"
install="install"
function initdb() {
    rm mysite/media/db.sqlite3
    python manage.py migrate
    python manage.py loaddata datas
    echo "completed migrations you can run: ./manage.py runserver 8001"
}


if [[ ${1} == ${install} ]]
then 
 python3 -m venv env
 source env/bin/activate
 cp .env.example .env
 pip install -r requirements.txt
 initdb
 python manage.py runserver
elif [[ ${1} == ${refreshdb} ]]
then
 initdb
 python manage.py runserver $2
else
 echo "no commands"
fi
