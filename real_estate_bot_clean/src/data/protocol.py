"""
Protocol optimization module implementing gRPC-style patterns for efficient data transfer.
Maintains our hybrid data approach while optimizing network communication.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import zlib
import logging
from enum import Enum

class MessageType(Enum):
    PROPERTY_REQUEST = "PROPERTY_REQUEST"
    PROPERTY_RESPONSE = "PROPERTY_RESPONSE"
    MARKET_REQUEST = "MARKET_REQUEST"
    MARKET_RESPONSE = "MARKET_RESPONSE"
    ERROR = "ERROR"

@dataclass
class Message:
    type: MessageType
    payload: Dict
    timestamp: datetime
    request_id: str
    compressed: bool = False

class ProtocolOptimizer:
    def __init__(self):
        self.compression_threshold = 1024  # Bytes
        self.logger = logging.getLogger(__name__)
    
    def encode_request(
        self,
        message_type: MessageType,
        payload: Dict,
        request_id: str
    ) -> bytes:
        """
        Encode request data in binary format for efficient transfer.
        Similar to gRPC's binary encoding but simplified for our use case.
        """
        try:
            message = Message(
                type=message_type,
                payload=payload,
                timestamp=datetime.now(),
                request_id=request_id
            )
            
            # Convert to JSON first
            json_data = {
                "type": message.type.value,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat(),
                "request_id": message.request_id
            }
            
            encoded = json.dumps(json_data).encode('utf-8')
            
            # Apply compression if payload is large
            if len(encoded) > self.compression_threshold:
                compressed = zlib.compress(encoded)
                if len(compressed) < len(encoded):
                    return compressed, True
            
            return encoded, False
            
        except Exception as e:
            self.logger.error(f"Encoding error: {e}")
            return self._encode_error(str(e)), False
    
    def decode_response(
        self,
        data: bytes,
        compressed: bool = False
    ) -> Message:
        """
        Decode binary response data back into usable format.
        Handles both compressed and uncompressed data.
        """
        try:
            # Decompress if needed
            if compressed:
                data = zlib.decompress(data)
            
            # Decode JSON
            json_data = json.loads(data.decode('utf-8'))
            
            return Message(
                type=MessageType(json_data["type"]),
                payload=json_data["payload"],
                timestamp=datetime.fromisoformat(json_data["timestamp"]),
                request_id=json_data["request_id"],
                compressed=compressed
            )
            
        except Exception as e:
            self.logger.error(f"Decoding error: {e}")
            return self._create_error_message(str(e))
    
    def optimize_property_request(
        self,
        zip_code: str,
        filters: Optional[Dict] = None
    ) -> bytes:
        """
        Optimize property search request for network transfer.
        """
        payload = {
            "zip_code": zip_code,
            "filters": filters or {}
        }
        
        encoded, compressed = self.encode_request(
            MessageType.PROPERTY_REQUEST,
            payload,
            self._generate_request_id()
        )
        
        return encoded, compressed
    
    def optimize_property_response(
        self,
        properties: List[Dict],
        request_id: str
    ) -> bytes:
        """
        Optimize property data response for network transfer.
        Uses selective field inclusion to minimize payload size.
        """
        # Only include essential fields for initial response
        optimized_properties = [
            {
                "id": p.get("id"),
                "address": p.get("address"),
                "price": p.get("price"),
                "sqft": p.get("sqft"),
                "beds": p.get("bedrooms"),
                "baths": p.get("bathrooms"),
                "year_built": p.get("year_built"),
                "property_type": p.get("property_type"),
                "confidence_score": p.get("confidence_score", 0.0)
            }
            for p in properties
        ]
        
        encoded, compressed = self.encode_request(
            MessageType.PROPERTY_RESPONSE,
            {"properties": optimized_properties},
            request_id
        )
        
        return encoded, compressed
    
    def optimize_market_request(
        self,
        zip_code: str,
        metrics: List[str]
    ) -> bytes:
        """
        Optimize market analysis request for network transfer.
        """
        payload = {
            "zip_code": zip_code,
            "metrics": metrics
        }
        
        encoded, compressed = self.encode_request(
            MessageType.MARKET_REQUEST,
            payload,
            self._generate_request_id()
        )
        
        return encoded, compressed
    
    def optimize_market_response(
        self,
        market_data: Dict,
        request_id: str
    ) -> bytes:
        """
        Optimize market data response for network transfer.
        Includes confidence scores for ML predictions.
        """
        # Only include requested metrics and their confidence scores
        optimized_data = {
            "metrics": market_data.get("metrics", {}),
            "confidence_scores": market_data.get("confidence_scores", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        encoded, compressed = self.encode_request(
            MessageType.MARKET_RESPONSE,
            optimized_data,
            request_id
        )
        
        return encoded, compressed
    
    def _encode_error(self, error_message: str) -> bytes:
        """Encode error message in consistent format."""
        error_data = {
            "type": MessageType.ERROR.value,
            "payload": {"error": error_message},
            "timestamp": datetime.now().isoformat(),
            "request_id": "error"
        }
        return json.dumps(error_data).encode('utf-8')
    
    def _create_error_message(self, error: str) -> Message:
        """Create error message in consistent format."""
        return Message(
            type=MessageType.ERROR,
            payload={"error": error},
            timestamp=datetime.now(),
            request_id="error"
        )
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking."""
        from uuid import uuid4
        return str(uuid4())
