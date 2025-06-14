from typing import Dict, Any
import redis
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user_feature import UserFeature

class FeatureService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    async def get_user_features(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém as features de um usuário, combinando dados do Redis e PostgreSQL
        """
        # Tenta obter do cache (Redis)
        cached_features = self._get_from_cache(user_id)
        if cached_features:
            return cached_features
        
        # Se não estiver em cache, busca do banco
        db_features = await self._get_from_db(user_id)
        
        # Atualiza o cache
        self._update_cache(user_id, db_features)
        
        return db_features
    
    def _get_from_cache(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém features do Redis
        """
        cache_key = f"user_features:{user_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def _get_from_db(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém features do PostgreSQL
        """
        db = next(get_db())
        features = db.query(UserFeature).filter(
            UserFeature.user_id == user_id
        ).first()
        
        if not features:
            return self._get_default_features()
        
        return features.feature_data
    
    def _update_cache(self, user_id: str, features: Dict[str, Any]):
        """
        Atualiza o cache no Redis
        """
        cache_key = f"user_features:{user_id}"
        self.redis_client.setex(
            cache_key,
            timedelta(hours=1),  # Cache por 1 hora
            json.dumps(features)
        )
    
    def _get_default_features(self) -> Dict[str, Any]:
        """
        Retorna features padrão para novos usuários
        """
        return {
            "pix_volume": 0.0,
            "avg_transaction_value": 0.0,
            "transaction_frequency": 0.0,
            "chargeback_rate": 0.0,
            "app_connections": 0,
            "last_transaction_date": None,
            "account_age_days": 0,
            "total_transactions": 0
        }
    
    async def update_features(
        self,
        user_id: str,
        new_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza as features de um usuário
        """
        # Obtém features atuais
        current_features = await self.get_user_features(user_id)
        
        # Atualiza com novas features
        updated_features = {**current_features, **new_features}
        
        # Salva no banco
        db = next(get_db())
        feature_record = db.query(UserFeature).filter(
            UserFeature.user_id == user_id
        ).first()
        
        if not feature_record:
            feature_record = UserFeature(
                user_id=user_id,
                feature_data=updated_features
            )
            db.add(feature_record)
        else:
            feature_record.feature_data = updated_features
        
        db.commit()
        
        # Atualiza cache
        self._update_cache(user_id, updated_features)
        
        return updated_features
    
    async def process_event(self, event: Dict[str, Any]):
        """
        Processa um evento e atualiza as features do usuário
        """
        user_id = event.get("user_id")
        event_type = event.get("type")
        event_data = event.get("data", {})
        
        if not user_id or not event_type:
            return
        
        # Atualiza features baseado no tipo de evento
        if event_type == "pix_payment":
            await self._process_pix_payment(user_id, event_data)
        elif event_type == "chargeback":
            await self._process_chargeback(user_id, event_data)
        elif event_type == "app_connection":
            await self._process_app_connection(user_id, event_data)
    
    async def _process_pix_payment(self, user_id: str, event_data: Dict[str, Any]):
        """
        Processa um evento de pagamento via Pix
        """
        current_features = await self.get_user_features(user_id)
        
        # Atualiza features relacionadas a Pix
        new_features = {
            "pix_volume": current_features["pix_volume"] + event_data.get("amount", 0),
            "total_transactions": current_features["total_transactions"] + 1,
            "last_transaction_date": datetime.utcnow().isoformat(),
            "avg_transaction_value": (
                (current_features["pix_volume"] + event_data.get("amount", 0)) /
                (current_features["total_transactions"] + 1)
            )
        }
        
        await self.update_features(user_id, new_features)
    
    async def _process_chargeback(self, user_id: str, event_data: Dict[str, Any]):
        """
        Processa um evento de chargeback
        """
        current_features = await self.get_user_features(user_id)
        
        # Atualiza taxa de chargeback
        total_chargebacks = current_features.get("total_chargebacks", 0) + 1
        new_features = {
            "total_chargebacks": total_chargebacks,
            "chargeback_rate": total_chargebacks / current_features["total_transactions"]
        }
        
        await self.update_features(user_id, new_features)
    
    async def _process_app_connection(self, user_id: str, event_data: Dict[str, Any]):
        """
        Processa um evento de conexão com app
        """
        current_features = await self.get_user_features(user_id)
        
        # Atualiza número de apps conectados
        new_features = {
            "app_connections": current_features["app_connections"] + 1
        }
        
        await self.update_features(user_id, new_features) 