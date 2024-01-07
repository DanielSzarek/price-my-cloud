#!/bin/bash
psql -U postgres -c "CREATE DATABASE testdb;"
psql -U postgres -d testdb -c "CREATE TABLE logs (id SERIAL PRIMARY KEY, log_data TEXT);"
