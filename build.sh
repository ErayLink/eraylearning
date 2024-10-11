#!/bin/bash

cat banner.txt


sudo apt update && sudo apt upgrade -y

pip3 install -r requirements.txt --break-system-packages

python3 manage.py migrate

echo "Cree le superuser/Admin lessy ry lerony eee :) !!"

echo "-----------------------------------------------------"

echo "Ohatra: admin@eray.mg / password: admin1234 "

echo "-----------------------------------------------------"

python3 manage.py createsuperuser

python3 manage.py runserver


cat banner.txt
