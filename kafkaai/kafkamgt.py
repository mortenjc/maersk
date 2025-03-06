from kafka import KafkaAdminClient, KafkaProducer, KafkaConsumer
from kafka.admin import NewTopic
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka broker configuration
KAFKA_BROKERS = 'localhost:9092,localhost:9093,localhost:9094,localhost:9095'

def create_topics(topic_names, partitions=3, replication_factor=3):
    """
    Create Kafka topics
    
    Args:
        topic_names (list): List of topic names to create
        partitions (int): Number of partitions for each topic
        replication_factor (int): Replication factor for each topic
    """
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKERS)
        
        # Create topic objects
        topics = [
            NewTopic(
                name=topic_name,
                num_partitions=partitions,
                replication_factor=replication_factor
            ) for topic_name in topic_names
        ]
        
        # Create the topics
        admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info(f"Created topics: {topic_names}")
        admin_client.close()
    except Exception as e:
        logger.error(f"Error creating topics: {e}")

def produce_messages(topic_name, num_messages=10, key_prefix="key-", value_prefix="message-"):
    """
    Produce sample messages to a Kafka topic
    
    Args:
        topic_name (str): Name of the topic to send messages to
        num_messages (int): Number of messages to send
        key_prefix (str): Prefix for message keys
        value_prefix (str): Prefix for message values
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8')
        )
        
        # Send messages
        for i in range(num_messages):
            # Create a sample message
            timestamp = datetime.now().isoformat()
            message_value = {
                'index': i,
                'message': f"{value_prefix}{i}",
                'timestamp': timestamp
            }
            
            # Create a message key
            message_key = f"{key_prefix}{i}"
            
            # Send the message
            future = producer.send(
                topic=topic_name,
                key=message_key,
                value=message_value
            )
            
            # Wait for the message to be sent
            result = future.get(timeout=60)
            logger.info(f"Sent message {i} to topic {topic_name}, partition {result.partition}, offset {result.offset}")
            
            # Small delay between messages
            time.sleep(0.1)
        
        # Flush and close the producer
        producer.flush()
        producer.close()
        logger.info(f"Finished sending {num_messages} messages to topic {topic_name}")
    except Exception as e:
        logger.error(f"Error producing messages: {e}")

def consume_messages(topic_name, group_id="my-consumer-group", timeout_ms=10000):
    """
    Consume messages from a Kafka topic
    
    Args:
        topic_name (str): Name of the topic to consume from
        group_id (str): Consumer group ID
        timeout_ms (int): Poll timeout in milliseconds
    """
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BROKERS,
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None
        )
        
        logger.info(f"Starting to consume from topic {topic_name}")
        
        # Poll for messages
        messages = consumer.poll(timeout_ms=timeout_ms)
        
        if not messages:
            logger.info(f"No messages received from topic {topic_name} within timeout")
        
        # Process messages
        for tp, records in messages.items():
            logger.info(f"Received {len(records)} messages from {tp.topic}, partition {tp.partition}")
            for record in records:
                logger.info(f"Offset: {record.offset}, Key: {record.key}, Value: {record.value}")
        
        # Close the consumer
        consumer.close()
        logger.info(f"Finished consuming from topic {topic_name}")
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")

def listen_continuously(topic_name, group_id="my-consumer-group", duration_seconds=60):
    """
    Listen continuously for messages on a Kafka topic
    
    Args:
        topic_name (str): Name of the topic to consume from
        group_id (str): Consumer group ID
        duration_seconds (int): How long to listen for messages in seconds
    """
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BROKERS,
            group_id=group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None
        )
        
        logger.info(f"Starting to listen continuously to topic {topic_name} for {duration_seconds} seconds")
        
        # Calculate end time
        end_time = time.time() + duration_seconds
        
        # Poll for messages until timeout
        while time.time() < end_time:
            msg = next(consumer, None)
            if msg:
                logger.info(f"Received message: Topic={msg.topic}, Partition={msg.partition}, Offset={msg.offset}")
                logger.info(f"Key: {msg.key}, Value: {msg.value}")
            time.sleep(0.1)
        
        # Close the consumer
        consumer.close()
        logger.info(f"Finished listening to topic {topic_name}")
    except Exception as e:
        logger.error(f"Error listening to messages: {e}")

def list_topics():
    """List all available Kafka topics"""
    try:
        consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKERS)
        topics = consumer.topics()
        logger.info(f"Available topics: {topics}")
        consumer.close()
        return topics
    except Exception as e:
        logger.error(f"Error listing topics: {e}")
        return []

if __name__ == "__main__":
    # Demo usage
    
    # Create topics
    create_topics(['test-topic', 'data-events', 'logs'], partitions=3, replication_factor=3)
    
    # Wait for topics to be created
    time.sleep(2)
    
    # List topics
    available_topics = list_topics()
    
    # Produce messages to topics
    if 'test-topic' in available_topics:
        produce_messages('test-topic', num_messages=5)
    
    if 'data-events' in available_topics:
        produce_messages('data-events', num_messages=3, key_prefix="event-", value_prefix="data-")
    
    # Wait for messages to be processed
    time.sleep(1)
    
    # Consume messages from a topic
    if 'test-topic' in available_topics:
        consume_messages('test-topic')
    
    # Continuously listen to a topic
    if 'data-events' in available_topics:
        listen_continuously('data-events', duration_seconds=10)