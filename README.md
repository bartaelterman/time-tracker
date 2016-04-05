# Time tracker

A web application for tracking time and generating invoices.

## Technical architecture

The application architecture was designed with one primary goal: scalability. Every component of the application can scale linearly
as the application grows. The application contains a web service in Flask with a MongoDB database. The MongoDB updates
are streamed into hadoop for BI and batch reporting.

## Components

### Web service

The web service is a Flask application with MongoDB.

### MongoDB event stream

The MongoDB event stream is implemented using [mongo-connector](https://github.com/mongodb-labs/mongo-connector) and a
custom DocManager that writes updates to Kafka topics.

### Warehouse

The warehouse is implemented on a Hadoop cluster.

## Installation

- Kafka (includes zookeeper)
- MongoDB
- This repository and its requirements

## Start the services

1. Start the MongoDB server: `mongod --config /usr/local/etc/mongod.conf --replSet singleNodeRepl` (for demonstration purposes,
I'm using a single node server here)
2. Enable the MongoDB optlog:
	a. `mongo`
	b. `rs.initiate()`
3. Start zookeeper: `bin/zookeeper-server-start.sh config/zookeeper.properties`
4. Start kafka: `bin/kafka-server-start.sh config/server.properties`
5. Create required topics: `bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic activity-app-updates`
6. Add this repo to your `PYTHONPATH` (if you don't do so, the next line will fail because it won't find the `kafka_doc_manager`)
7. Start the MongoDB optlog tailer: `mongo-connector -m localhost:27017 -t localhost:9092 -d kafka_doc_manager`
8. Start the web server: `flask manage.py runserver`

## Look at the API documentation

The API of the web service is documented in the [doc](./doc) folder. It allows you to add users, projects, activities and other data by
sending JSON data to the server. The service can even generate an invoice for a given project.