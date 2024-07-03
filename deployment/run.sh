python3 -m venv env
. ./env/bin/activate
pip install -r requirements.txt

cp deployment/bot.service /etc/systemd/system/
systemctl start bot.service
systemctl enable bot.service
 