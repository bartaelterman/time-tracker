"""
A mongo-connector DocManager to publish mongodb events to kafka

Thanks to https://github.com/tjj5036/mongo-connector-kafka-doc-manager for example code.
"""

from mongo_connector.doc_managers.doc_manager_base import DocManagerBase

TOPICS = {
    'activity': 'activity-app-updates',
    'session': 'session-logs'
}

class DocManager(DocManagerBase):

    def __init__(self, url, auto_commit_interval=1, unique_key='_id', chunk_size=10):
        try:
            from kafka import KafkaProducer
        except ImportError:
            raise SystemError

        self.producer = KafkaProducer(bootstrap_servers=[url])

    def get_topic_key(self, namespace):
        if namespace == 'timetracker.session':
            topic_key = 'session'
        else:
            topic_key = 'activity'
        return topic_key

    def doc_to_message_data(self, doc, namespace, timestamp):
        data = {'timestamp': timestamp,
                'namespace': namespace,
                'action': 'upsert',
                'data': doc}
        return str(data)

    def update_to_message_data(self, doc_id, update_spec, namespace, timestamp):
        data = {'timestamp': timestamp,
                'namespace': namespace,
                'document_id': doc_id,
                'action': 'update',
                'data': update_spec['$set']
                }
        return str(data)

    def remove_to_message_data(self, doc_id, namespace, timestamp):
        data = {'timestamp': timestamp,
                'namespace': namespace,
                'document_id': doc_id,
                'action': 'remove'
                }
        return str(data)

    def publish_data(self, data, topic_key):
        self.producer.send(TOPICS[topic_key], data)
        self.producer.flush()

    def stop(self):
        self.producer.close()

    def upsert(self, doc, namespace, timestamp):
        data = self.doc_to_message_data(doc, namespace, timestamp)
        topic_key = self.get_topic_key(namespace)
        self.publish_data(data, topic_key)


    def update(self, document_id, update_spec, namespace, timestamp):
        data = self.update_to_message_data(document_id, update_spec, namespace, timestamp)
        topic_key = self.get_topic_key(namespace)
        self.publish_data(data, topic_key)

    def remove(self, document_id, namespace, timestamp):
        data = self.remove_to_message_data(document_id, namespace, timestamp)
        topic_key = self.get_topic_key(namespace)
        self.publish_data(data, topic_key)

    def search(selfself, start_ts, end_ts):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def get_last_doc(self):
        raise NotImplementedError

    def handle_command(self, doc, namespace, timestamp):
        pass
