from kafka import KafkaConsumer
import json
import asyncio
from typing import Dict, Any
import logging

from app.core.config import settings
from app.services.feature_service import FeatureService

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'user_events',
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.feature_service = FeatureService()
    
    async def process_message(self, message: Dict[str, Any]):
        """
        Processa uma mensagem do Kafka
        """
        try:
            logger.info(f"Processando evento: {message}")
            await self.feature_service.process_event(message)
        except Exception as e:
            logger.error(f"Erro ao processar evento: {str(e)}")
    
    async def start(self):
        """
        Inicia o consumo de eventos
        """
        logger.info("Iniciando consumer de eventos...")
        
        try:
            for message in self.consumer:
                await self.process_message(message.value)
        except Exception as e:
            logger.error(f"Erro no consumer: {str(e)}")
        finally:
            self.consumer.close()

async def main():
    consumer = EventConsumer()
    await consumer.start()

if __name__ == "__main__":
    asyncio.run(main()) 