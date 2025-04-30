# LETS Backend

Local Exchange Trading System Backend

## Run it locally

Run the following in your terminal:
```
wget https://raw.githubusercontent.com/suhailvs/pylets/refs/heads/peer2peer/pylets.sh
bash pylets.sh install
bash pylets.sh refreshdb
visit <http://localhost:8000/>
```

## Tests

#### Unittest

to run unittests:
```
./manage.py test
```

#### Functional Tests 

to run functional tests for Peer2Peer using pytest
+ `wget https://raw.githubusercontent.com/suhailvs/pylets/refs/heads/peer2peer/pylets.sh`
+ clone 2 nodes, `bash pylets.sh install node1` and `bash pylets.sh install node2`
+ initiate the db and runserver, `bash pylets.sh refreshdb 8001`
+ run pytest `pytest`

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
