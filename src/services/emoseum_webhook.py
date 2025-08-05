# src/services/emoseum_webhook.py

import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class EmoseumWebhookService:
    """Emoseum 서버로 데이터를 전송하는 웹훅 서비스"""
    
    def __init__(self, emoseum_server_url: str):
        self.emoseum_server_url = emoseum_server_url.rstrip('/')
        
    async def send_gallery_item_update(
        self, 
        diary_id: str, 
        emotion_keywords: list = None,
        artwork_title: str = None,
        guided_question: str = None,
        vad_scores: list = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """갤러리 아이템 데이터를 Emoseum 서버에 업데이트"""
        
        try:
            webhook_url = f"{self.emoseum_server_url}/api/ai/webhook/gallery-update"
            
            payload = {
                "diary_id": diary_id,
                "updated_at": datetime.now().isoformat()
            }
            
            if emotion_keywords:
                payload["keywords"] = emotion_keywords
            if artwork_title:
                payload["title"] = artwork_title
            if guided_question:
                payload["guided_question"] = guided_question
            if vad_scores:
                payload["vad_scores"] = vad_scores
            if user_id:
                payload["user_id"] = user_id
                
            print(f"[DEBUG] Webhook payload: {payload}")
            print(f"[DEBUG] VAD scores in payload: {payload.get('vad_scores')}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    print(f"[DEBUG] Response status: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"[DEBUG] Response data: {result}")
                        logger.info(f"Gallery item 업데이트 성공: diary_id={diary_id}")
                        return {
                            "success": True,
                            "message": "Gallery item updated successfully",
                            "data": result
                        }
                    else:
                        error_text = await response.text()
                        print(f"[DEBUG] Error response: {error_text}")
                        logger.error(f"Gallery item 업데이트 실패: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "retry_recommended": True
                        }
                        
        except asyncio.TimeoutError:
            logger.error(f"Gallery item 업데이트 타임아웃: diary_id={diary_id}")
            return {
                "success": False,
                "error": "Request timeout",
                "retry_recommended": True
            }
        except Exception as e:
            logger.error(f"Gallery item 업데이트 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "retry_recommended": True
            }