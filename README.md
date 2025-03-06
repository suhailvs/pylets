# stackcoin

## Run it locally

Clone the repo and create a virtual env, then run:
```
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample
python manage.py runserver
visit <http://localhost:8000/>
```

## Host it on pythonanywhere

on pythonanywhere webapps tab add 2 urls in `Static files` section:

URL | Directory
--- | ---
/media/ | /home/suhailvs/stackcoin/mysite/media 	 
/static/ | /home/suhailvs/stackcoin/mysite/static 	 

```
python manage.py collectstatic
```

## Host it on vercel

* https://vercel.com/suhailvs-projects -> Add New... -> Project -> import git repo -> other
* add `app = application` in `mysite/wsgi.py`
* to access profitserver's postgres database from vercel, 
    fix in profit server `80.85.156.44` add `host    stackcoin    postgres    0.0.0.0/0   md5` to `/etc/postgresql/14/main/pg_hba.conf`
* add all environment variables in vercel(ie DB_HOST: 80.85.156.44)

## The Problems with Conventional Money

https://www.community-exchange.org/home/qanda/the-problems-with-conventional-money/

As an exchange system, money fails on many counts...

* It is partisan

Money as we know it is not a neutral service provided by the government. Our money supply is created by private financial institutions on a for-profit basis. The money-based exchange system is privately owned and run as a profit-making business designed to benefit those who provide it, not those who use it.

* It is based on debt

Money is created when banks grant loans. Thus for every unit created there is one unit of debt.

* We are encouraged to think of it as a 'thing'

Money is essentially information and today has no physical existence, yet banks encourage us to think of it as a 'thing' so that they can 'lend' it to us and thereby make a profit by charging interest. 'Thing' money also has to be created, distributed and controlled so that there is not too much or too little of it. It can also be stolen, lost, bought, sold, gambled and counterfeited, with serious consequences for everyone.

* It is permanently scarce

The money to pay the interest on debt-money is never created. There is therefore a permanent shortfall of money to pay back both the principal and the interest.

* It causes cancerous growth

Banks continuously need to create more money than is required to pay back their loans so that borrowers can pay back the interest on those loans as well. This is the source of the growth imperative of our economies. There must be a continual expansion of bank credit or else the economy goes into recession. Infinite growth in a finite world is an impossibility and is the direct cause of the environmental problems we now all face.

* Its value is based on its shortage

The shortfall of money keeps it valuable. There only needs to be enough of it to buy back the goods and services that the 'market' makes available. This has nothing to do with the monetary requirements of people. Those who have none are not seen by the market and so are marginalised.

* It is expensive

Every unit of conventional money is based on a unit of debt. This debt has to be paid back with interest, and the interest on the interest is compounding. Interest is built into the prices of everything we buy, resulting in higher consumer prices.

* It redistributes wealth from the poor to the wealthy

Usury is the tool used by the wealthy to suck wealth from the poor and middle classes to the moneyed class. Parasitism and class antagonisms are the result of this.

* It promotes dishonesty and corruption

You can get it without delivering anything of value (e.g. speculation, interest, gambling etc.) so many people concentrate on 'making money' rather than producing or delivering anything of real value. It is usually far easier to get money through dishonest means than by honest work. When you have no money and no means to provide for your needs you have no choice but to try and get it dishonestly

* It leaks away from where it is created

Conventional money knows no bounds and loyalty. It always leaks away to the 'money centres' (financial centres, big businesses, etc.).

* It destroys local economies

Goods produced cheaper elsewhere replace locally produced goods. This creates a local shortage of money and reduces the market for local sellers. This also results in the irrational transportation of goods all over the world, consuming precious fossil fuels and creating pollution.

* It destroys community

Dependence on money means we no longer need our neighbours. We can get everything from anonymous strangers in return for money. We have no obligation to anyone when the bills are paid. Every trade is a complete and closed action: you provide me with something and I give you money. End of story. No one does us any favours and we need do no favours for anyone.

* It fosters competitiveness

The shortage of money means we all have to fight for a share of an amount that is too small to go around. The need to repay interest means that we have to eat others to prevent ourselves from going under.

* It creates poverty

While it makes some super rich, it makes most people poor. Poverty is caused by a lack of money (not by a lack of jobs). Usury and the need to keep money scarce ensure that money constantly moves to those who already have money.

* It causes social and cultural degradation

The elimination of local opportunities to exchange and relate to one another focuses attention on ways of getting money outside the community. Communities fall apart as they become indebted to entities outside their communities.



### Football comparison

https://www.community-exchange.org/home/qanda/two-games-of-football/


Aspect|Game 1: Traditional Money System|Game 2: Community Exchange System (CES)
--|--|--
Goal Requirement|Goals must be borrowed from a "goal bank" before the game starts | Goals are not borrowed or stored; points are earned during play
Interest | Goals borrowed from the bank require a fee (interest) based on usage time|	No interest or borrowing involved
Goal Supply	|Limited supply; borrowing required due to finite goals	|No supply limit; points are just a record of successful plays
Scoring	|Teams start with a supply of goals and win by having more than the other team	|Points are gained as teams score; no pre-set goals needed
End of Game	|Teams aim to have enough goals to repay the bank, plus interest	|Team with the most points wins, taking home a trophy
Goal Balance	|Losing team hands over goals equal to the score difference	|Winning team has a positive score, and the other has a deficit
Objective	|End with more goals than the other team, plus extra to repay the bank	|Simply score more points than the other team to win the match