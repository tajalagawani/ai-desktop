#!/bin/bash
# Create UFW application profiles for AI Desktop services

echo "Creating UFW application profiles..."

# MySQL Databases
sudo tee /etc/ufw/applications.d/ai-desktop-mysql <<EOF
[AI-Desktop-MySQL]
title=MySQL 8.0 Database
description=MySQL 8.0 relational database server
ports=3306/tcp

[AI-Desktop-MySQL57]
title=MySQL 5.7 Database
description=MySQL 5.7 legacy database server
ports=3307/tcp

[AI-Desktop-MariaDB]
title=MariaDB Database
description=MariaDB MySQL fork database server
ports=3308/tcp
EOF

# PostgreSQL
sudo tee /etc/ufw/applications.d/ai-desktop-postgresql <<EOF
[AI-Desktop-PostgreSQL]
title=PostgreSQL Database
description=PostgreSQL advanced relational database
ports=5432/tcp

[AI-Desktop-TimescaleDB]
title=TimescaleDB
description=PostgreSQL extension for time-series
ports=5433/tcp
EOF

# NoSQL Databases
sudo tee /etc/ufw/applications.d/ai-desktop-nosql <<EOF
[AI-Desktop-MongoDB]
title=MongoDB Database
description=MongoDB NoSQL document database
ports=27017/tcp

[AI-Desktop-Redis]
title=Redis Cache
description=Redis in-memory data store
ports=6379/tcp

[AI-Desktop-KeyDB]
title=KeyDB Cache
description=KeyDB high-performance cache
ports=6380/tcp

[AI-Desktop-CouchDB]
title=CouchDB Database
description=CouchDB NoSQL database with HTTP API
ports=5984/tcp

[AI-Desktop-ArangoDB]
title=ArangoDB
description=ArangoDB multi-model database
ports=8529/tcp

[AI-Desktop-Memcached]
title=Memcached
description=Memcached distributed memory caching
ports=11211/tcp
EOF

# Graph Databases
sudo tee /etc/ufw/applications.d/ai-desktop-graph <<EOF
[AI-Desktop-Neo4j]
title=Neo4j Graph Database
description=Neo4j graph database for connected data
ports=7474,7687/tcp
EOF

# Time-Series Databases
sudo tee /etc/ufw/applications.d/ai-desktop-timeseries <<EOF
[AI-Desktop-InfluxDB]
title=InfluxDB
description=InfluxDB time-series database
ports=8086/tcp

[AI-Desktop-QuestDB]
title=QuestDB
description=QuestDB fast time-series database
ports=9000,8812/tcp

[AI-Desktop-VictoriaMetrics]
title=VictoriaMetrics
description=VictoriaMetrics time-series database
ports=8428/tcp
EOF

# Column-Family Databases
sudo tee /etc/ufw/applications.d/ai-desktop-widecolumn <<EOF
[AI-Desktop-Cassandra]
title=Apache Cassandra
description=Cassandra distributed NoSQL database
ports=9042/tcp

[AI-Desktop-ScyllaDB]
title=ScyllaDB
description=ScyllaDB Cassandra-compatible database
ports=9043/tcp
EOF

# Analytics Databases
sudo tee /etc/ufw/applications.d/ai-desktop-analytics <<EOF
[AI-Desktop-ClickHouse]
title=ClickHouse
description=ClickHouse OLAP database for analytics
ports=8123,9000/tcp
EOF

# Search Engines
sudo tee /etc/ufw/applications.d/ai-desktop-search <<EOF
[AI-Desktop-Elasticsearch]
title=Elasticsearch
description=Elasticsearch distributed search engine
ports=9200,9300/tcp
EOF

# Web Servers & Tools
sudo tee /etc/ufw/applications.d/ai-desktop-web <<EOF
[AI-Desktop-Nginx]
title=Nginx Web Server
description=Nginx high-performance web server
ports=8080/tcp

[AI-Desktop-PHPMyAdmin]
title=phpMyAdmin
description=phpMyAdmin MySQL web interface
ports=8081/tcp

[AI-Desktop-Adminer]
title=Adminer
description=Adminer database management tool
ports=8082/tcp
EOF

# Message Queues
sudo tee /etc/ufw/applications.d/ai-desktop-queue <<EOF
[AI-Desktop-RabbitMQ]
title=RabbitMQ
description=RabbitMQ message broker
ports=5672,15672/tcp
EOF

# SQL Server
sudo tee /etc/ufw/applications.d/ai-desktop-mssql <<EOF
[AI-Desktop-MSSQL]
title=Microsoft SQL Server
description=Microsoft SQL Server for Linux
ports=1433/tcp
EOF

# CockroachDB
sudo tee /etc/ufw/applications.d/ai-desktop-cockroach <<EOF
[AI-Desktop-CockroachDB]
title=CockroachDB
description=CockroachDB distributed SQL database
ports=26257,8080/tcp
EOF

# Reload UFW to recognize new profiles
sudo ufw app update all

echo ""
echo "✓ UFW application profiles created"
echo ""
echo "Available profiles:"
sudo ufw app list | grep AI-Desktop

echo ""
echo "Usage examples:"
echo "  sudo ufw allow 'AI-Desktop-MySQL'"
echo "  sudo ufw allow 'AI-Desktop-PostgreSQL'"
echo "  sudo ufw status"
