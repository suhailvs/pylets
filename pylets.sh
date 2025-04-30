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
 git clone https://github.com/suhailvs/pylets.git $2
 if [[ -z ${2} ]]
 then
  cd pylets
 else
  cd $2
 fi
 git switch peer2peer 
 python3 -m venv env
 source env/bin/activate
 cp .env.example .env
 pip install -r requirements.txt 
elif [[ ${1} == ${refreshdb} ]]
then
 source env/bin/activate
 initdb
 python manage.py runserver $2
else
 echo "no commands"
fi
