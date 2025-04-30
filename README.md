# LETS Backend

Local Exchange Trading System Backend

## Run it locally

Clone the repo, then run the bash script:
```

./mybash.sh install
visit <http://localhost:8000/>
```

## Tests

#### Unittest

to run unittest the project run:

```
./manage.py test
```

#### Functional Tests 

to run functional tests for Peer2Peer using pytest

+ clone repo in 2 folder, and run `./mybash.sh install`
+ now an env folder will be created. activate it `source env/bin/activate`
+ run `./manage.py runserver 0:8000` on a folder and `./manage.py runserver 8001` on another folder.
+ run pytest `pytest`
+ if you want to reset the db, run `./mybash.sh refreshdb 8001`


## Hosting

#### Host it on pythonanywhere

on pythonanywhere webapps tab add 2 urls in `Static files` section:

URL | Directory
--- | ---
/media/ | /home/suhailvs/pylets/mysite/media 	 
/static/ | /home/suhailvs/pylets/mysite/static 	 

```
python manage.py collectstatic
```

#### Host it on vercel

* https://vercel.com/suhailvs-projects -> Add New... -> Project -> import git repo -> other
* add `app = application` in `mysite/wsgi.py`
* to access profitserver's postgres database from vercel, 
    fix in profit server `80.85.156.44` add `host    pylets    postgres    0.0.0.0/0   md5` to `/etc/postgresql/14/main/pg_hba.conf`
* add all environment variables in vercel(ie DB_HOST: 80.85.156.44)
