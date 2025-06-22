import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime
from typing import Dict, Any
from app.core.config import settings
from fastapi import Request

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['environment'] = settings.ENVIRONMENT

def setup_logger(name: str) -> logging.Logger:
    """
    Configura um logger estruturado em JSON
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(environment)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

class ScoreLogger:
    """
    Logger específico para scores com campos LGPD
    """
    def __init__(self):
        self.logger = setup_logger('score_engine')

    def log_score_calculation(
        self,
        user_id: str,
        score: float,
        features: Dict[str, Any],
        model_version: str,
        source_app: str,
        explanation: Dict[str, Any],
        trace_id: str = None
    ) -> None:
        """
        Registra o cálculo de score com metadados LGPD
        """
        self.logger.info(
            "Score calculation",
            extra={
                "user_id": user_id,
                "score": score,
                "features": features,
                "model_version": model_version,
                "source_app": source_app,
                "explanation": explanation,
                "event_type": "score_calculation",
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id
            }
        )

    def log_score_contest(
        self,
        user_id: str,
        reason: str,
        original_score: float,
        new_score: float = None,
        trace_id: str = None
    ) -> None:
        """
        Registra contestação de score
        """
        self.logger.info(
            "Score contest",
            extra={
                "user_id": user_id,
                "reason": reason,
                "original_score": original_score,
                "new_score": new_score,
                "event_type": "score_contest",
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id
            }
        ) 