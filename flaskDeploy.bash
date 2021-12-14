#!/bin/bash

################################
# Name: Sandeep Kumar Paul     #
# Email: #######@ucmo.edu     #
################################

# Referred from: https://linuxize.com/post/how-to-install-flask-on-ubuntu-20-04/


# Upgrade the ubuntu repository and install 'Apache2' module
sudo apt update -y
sudo apt upgrade -y
sudo apt install apache2 -y

# Allowing Apache module in the firewall
sudo ufw disable
yes | sudo ufw enable
sudo ufw reload

sudo ufw status | grep 'inactive' &> /dev/null
if [ $? == 0 ]; then
   yes | sudo ufw enable
   wait
   sudo ufw reload
   sudo ufw allow apache
else
   sudo ufw allow apache
fi


# sudo systemctl status apache2


echo "Installing Apache-WSGI & Python3 dev tools......"
sudo apt-get install libapache2-mod-wsgi-py3 python3-dev python3-pip python3-venv -y


# 
sudo pip install Flask flask_sqlalchemy
cd /var/www/
mkdir sqlAtlas
cd sqlAtlas
mkdir sqlAtlas
cd sqlAtlas
mkdir static templates

# sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install Flask
deactivate






########## copy all the python/flask files including __init__.py file

apache_config=/etc/apache2/sites-available/sqlAtlas.conf

echo "<VirtualHost *:80>" > $apache_config
echo "		ServerName ip" >> $apache_config
echo "		ServerAdmin sxp82050@ucmo.edu" >> $apache_config
echo "		WSGIScriptAlias / /var/www/sqlAtlas/sqlatlas.wsgi" >> $apache_config
echo "		<Directory /var/www/sqlAtlas/sqlAtlas/>" >> $apache_config
echo "			Order allow,deny" >> $apache_config
echo "			Allow from all" >> $apache_config
echo "		</Directory>" >> $apache_config
echo "		Alias /static /var/www/sqlAtlas/sqlAtlas/static" >> $apache_config
echo "		<Directory /var/www/sqlAtlas/sqlAtlas/static/>" >> $apache_config
echo "			Order allow,deny" >> $apache_config
echo "			Allow from all" >> $apache_config
echo "		</Directory>" >> $apache_config
echo "		ErrorLog ${APACHE_LOG_DIR}/error.log" >> $apache_config
echo "		LogLevel warn" >> $apache_config
echo "		CustomLog ${APACHE_LOG_DIR}/access.log combined" >> $apache_config
echo "</VirtualHost>" >> $apache_config

# To finalize the apache-config, need to enable the Apache2 site configuration and reload the service
sudo a2ensite sqlAtlas
systemctl reload apache2



cd /var/www/sqlAtlas  # Not necessary
wsgi_script=/var/www/sqlAtlas/sqlatlas.wsgi

echo "#!/usr/bin/python3" > $wsgi_script
echo "import sys" >> $wsgi_script
echo "import logging" >> $wsgi_script
echo "logging.basicConfig(stream=sys.stderr)" >> $wsgi_script
echo "sys.path.insert(0,'/var/www/sqlAtlas/')" >> $wsgi_script
echo "from sqlAtlas import app as application" >> $wsgi_script
echo "application.secret_key = 'D@t@C0m1@b!'" >> $wsgi_script


sudo pip install pandas
sudo pip install pandas-profiling
sudo apt-get install unixodbc-dev -y
sudo pip install pyodbc


# Finally, restarting the Apache2 http service module, to make consistent the communication
sudo service apache2 restart

# Converting all subdirectories and it's files from dos to unix file format
find . -type f -print0 | xargs -0 -n 1 -P 4 dos2unix 




