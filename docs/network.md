# Mise en place du reroutage

Se connecter à la box (http://192.168.1.1/)  
Onglet Redirection de ports (NAT)  
Mettre en place une redirection entre les ports Web et python interne et externe

# Adresses utiles

Adresse IP externe de la box : 93.19.92.161
Adresse IP interne de la raspberry : 192.168.1.96  
Web server port internal : 80  
Web server port external : 3074  
Python server port internal : 50000  
Python server port external : 3724  

# Modifications locales à apporter sur le serveur

Dans index.js : Mettre l'adresse externe du serveur python pour le socket à la place de localhost:50000  
Dans pages/board/serverCom.js : Mettre l'adresse externe du serveur python pour le socket à la place de localhost:50000
Dans server/Database.py : Disable TEST_ENABLE si besoin
Lancer le serveur avec la commande suivante : python server/server.py --socketAddr <PI_INTERNAL_ADDR> --port 50000

# Commandes Apache utiles pour lancer le serveur

Les configurations de sites apache sont dans /etc/apache2/sites-available  
Les sites doivent être dans var/html  

systemctl status apache2	# Checker si apache est allumé  
sudo a2ensite SITE_NAME		# Activer un site  
sudo a2dissite SITE_NAME	# Désactiver un site  
sudo systemctl reload apache2	# A faire après chaque modif  
apache2ctl -S 			# Lister les sites activés  