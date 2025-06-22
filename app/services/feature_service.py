from typing import Dict, Any
import redis
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import deque

from app.core.config import settings
from app.db.session import get_db
from app.models.user_feature import UserFeature

class FeatureService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        # Parâmetro: quantos eventos manter no histórico
        self.HISTORICO_TRANSACOES = 20
        self.HISTORICO_LOGINS = 10
    
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
            "total_transactions": 0,
            # Novas features
            "tempo_medio_entre_transacoes": 0.0,
            "variacao_categoria_uso": 0,
            "geodispersao_ips": 0,
            "frequencia_reembolsos": 0.0,
            "mudanca_subita_device": 0,
            "dias_desde_ultima_transacao": 0,
            "total_chargebacks": 0,
            "media_valor_reembolsos": 0.0,
            # Históricos mínimos para cálculo
            "historico_transacoes": [],  # lista de dicts: {timestamp, valor, categoria, reembolsada, chargeback}
            "historico_logins": []       # lista de dicts: {timestamp, device_id, cidade, estado}
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
        features = await self.get_user_features(user_id)
        historico_transacoes = features.get("historico_transacoes", [])
        historico_logins = features.get("historico_logins", [])
        now = datetime.utcnow()
        # Atualiza históricos e features conforme o tipo de evento
        if event_type == "pix_payment":
            transacao = {
                "timestamp": now,
                "valor": event_data.get("amount", 0),
                "categoria": event_data.get("categoria", "pix"),
                "reembolsada": event_data.get("reembolsada", False),
                "chargeback": False
            }
            historico_transacoes.append(transacao)
            historico_transacoes = historico_transacoes[-self.HISTORICO_TRANSACOES:]
            features["pix_volume"] = features.get("pix_volume", 0.0) + event_data.get("amount", 0)
            features["total_transactions"] = features.get("total_transactions", 0) + 1
            features["last_transaction_date"] = now.isoformat()
            features["avg_transaction_value"] = features["pix_volume"] / features["total_transactions"]
        elif event_type == "chargeback":
            # Marca a última transação como chargeback
            if historico_transacoes:
                historico_transacoes[-1]["chargeback"] = True
            features["total_chargebacks"] = features.get("total_chargebacks", 0) + 1
            features["chargeback_rate"] = features["total_chargebacks"] / features.get("total_transactions", 1)
        elif event_type == "refund":
            # Marca a última transação como reembolsada
            if historico_transacoes:
                historico_transacoes[-1]["reembolsada"] = True
        elif event_type == "app_connection":
            features["app_connections"] = features.get("app_connections", 0) + 1
        elif event_type == "login":
            login = {
                "timestamp": now,
                "device_id": event_data.get("device_id", "unknown"),
                "cidade": event_data.get("cidade", ""),
                "estado": event_data.get("estado", "")
            }
            historico_logins.append(login)
            historico_logins = historico_logins[-self.HISTORICO_LOGINS:]
        # Atualiza históricos
        features["historico_transacoes"] = historico_transacoes
        features["historico_logins"] = historico_logins
        # Recalcula features comportamentais avançadas
        features["tempo_medio_entre_transacoes"] = self.calcular_tempo_medio_entre_transacoes(historico_transacoes)
        features["variacao_categoria_uso"] = self.calcular_variacao_categoria_uso(historico_transacoes)
        features["geodispersao_ips"] = self.calcular_geodispersao_ips(historico_logins)
        features["frequencia_reembolsos"] = self.calcular_frequencia_reembolsos(historico_transacoes)
        features["mudanca_subita_device"] = self.calcular_mudanca_subita_device(historico_logins)
        features["dias_desde_ultima_transacao"] = self.calcular_dias_desde_ultima_transacao(historico_transacoes)
        features["total_chargebacks"] = self.calcular_total_chargebacks(historico_transacoes)
        features["media_valor_reembolsos"] = self.calcular_media_valor_reembolsos(historico_transacoes)
        await self.update_features(user_id, features)
    
    # Funções utilitárias para cálculo das novas features
    def calcular_tempo_medio_entre_transacoes(self, transacoes):
        if len(transacoes) < 2:
            return 0.0
        transacoes_ordenadas = sorted(transacoes, key=lambda x: x['timestamp'])
        intervalos = [
            (transacoes_ordenadas[i]['timestamp'] - transacoes_ordenadas[i-1]['timestamp']).total_seconds()/3600
            for i in range(1, len(transacoes_ordenadas))
        ]
        return sum(intervalos) / len(intervalos)

    def calcular_variacao_categoria_uso(self, transacoes):
        categorias = set([t.get('categoria') for t in transacoes if t.get('categoria')])
        return len(categorias)

    def calcular_geodispersao_ips(self, logins):
        localidades = set()
        for login in logins:
            if 'cidade' in login and 'estado' in login:
                localidades.add((login['cidade'], login['estado']))
        return len(localidades)

    def calcular_frequencia_reembolsos(self, transacoes):
        total = len(transacoes)
        reembolsos = sum(1 for t in transacoes if t.get('reembolsada', False))
        return reembolsos / total if total > 0 else 0.0

    def calcular_mudanca_subita_device(self, logins):
        if not logins:
            return 0
        devices = [login.get('device_id') for login in sorted(logins, key=lambda x: x['timestamp'])]
        trocas = sum(1 for i in range(1, len(devices)) if devices[i] != devices[i-1])
        return trocas

    def calcular_dias_desde_ultima_transacao(self, transacoes):
        if not transacoes:
            return 0
        ultima = max(transacoes, key=lambda x: x['timestamp'])['timestamp']
        return (datetime.utcnow() - ultima).days

    def calcular_total_chargebacks(self, transacoes):
        return sum(1 for t in transacoes if t.get('chargeback', False))

    def calcular_media_valor_reembolsos(self, transacoes):
        valores = [t['valor'] for t in transacoes if t.get('reembolsada', False) and t.get('valor') is not None]
        return sum(valores) / len(valores) if valores else 0.0 