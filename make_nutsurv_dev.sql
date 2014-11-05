
-- Database: nutsurv_dev
-- using a command like: sudo -u postgres psql -f make_nutsurv_dev.sql
-- password will be 'nutsurv_dev_password'


DROP DATABASE nutsurv_dev;

CREATE DATABASE nutsurv_dev
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       CONNECTION LIMIT = -1
       TEMPLATE template0;

-- Role: nutsurv_dev

DROP ROLE nutsurv_dev;

CREATE ROLE nutsurv_dev LOGIN
  UNENCRYPTED PASSWORD 'nutsurv_dev_password'
  SUPERUSER INHERIT CREATEDB NOCREATEROLE REPLICATION;
