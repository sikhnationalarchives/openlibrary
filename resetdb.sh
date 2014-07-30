sudo stop ol-web
sudo stop ol-infobase
sudo -u vagrant dropdb openlibrary
sudo -u vagrant dropdb coverstore
sudo -u vagrant createdb openlibrary
sudo -u vagrant createdb coverstore
sudo -u vagrant psql coverstore < openlibrary/coverstore/schema.sql
wget http://archive.org/download/ol_vendor/openlibrary-devinstance.pg_dump.gz -O /tmp/openlibrary-devinstance.pg_dump.gz
zcat /tmp/openlibrary-devinstance.pg_dump.gz | sudo -u vagrant psql openlibrary
#sudo -u vagrant pg_dump -s openlibrary > oldb-schema.sql
#zcat openlibrary/schema/oldb-schema.sql.gz | sudo -u vagrant psql openlibrary
#change git instead of http .gitmodules
#change git instead of http .git/config
sudo make
sudo start ol-infobase
sudo start ol-web
sudo start ol-solr-updater
