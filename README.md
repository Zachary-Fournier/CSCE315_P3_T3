# CSCE315_P3_T3
webapp address: https://baszl.herokuapp.com/

this is the project for TAMU CSCE_315 Team #30
Heroku would not connect to our tamu github, so we are using our personal github.

SCRUM meeting timestamps were updated on the tamu github: https://github.tamu.edu/zfournier/CSCE315_Project3_Team30

Run Django: pipenv shell
	    python3 manage.py runserver 

Run React: npm start


Both work given the necessary tools are installed.
Instabot Starter Code:

from instabot import Bot

bot = Bot()
 
bot.login(username = xxxxx,
          password = x)

bot.upload_photo("xxxx.jpg",
                 caption ="xxx")

