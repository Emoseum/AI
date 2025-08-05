# src/managers/gallery_manager.py

# ==============================================================================
# 이 파일은 사용자의 감정 여정 데이터를 관리하는 역할을 한다.
# MongoDB를 사용하여 각 여정(일기, 생성된 이미지, 작품 제목, 도슨트 메시지 등)을
# `GalleryItem` 객체로 저장하고 조회한다. 또한, 생성된 이미지 파일을 파일 시스템에 저장하고 관리한다.
# `ACTTherapySystem`은 이 매니저를 통해 사용자의 미술관 데이터를 생성, 조회, 업데이트한다.
# ==============================================================================

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from PIL import Image
import shutil
from pymongo.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class GalleryItem:
    """미술관 전시 아이템"""

    def __init__(
        self,
        item_id: str,
        user_id: str,
        diary_text: str,
        emotion_keywords: List[str],
        vad_scores: Tuple[float, float, float],
        reflection_prompt: str,
        reflection_image_path: str,
        artwork_title: str = "",
        docent_message: Dict[str, Any] = None,
        message_reactions: List[str] = None,
        guided_question: str = "",
        created_date: str = "",
        coping_style: str = "balanced",
        # GPT 관련 새 필드들
        gpt_prompt_used: bool = True,
        gpt_prompt_tokens: int = 0,
        gpt_docent_used: bool = True,
        gpt_docent_tokens: int = 0,
        prompt_generation_time: float = 0.0,
        prompt_generation_method: str = "gpt",
        docent_generation_method: str = "gpt",
        diary_id: str = None,
    ):

        self.item_id = item_id
        self.user_id = user_id
        self.diary_text = diary_text
        self.emotion_keywords = emotion_keywords
        self.vad_scores = vad_scores
        self.reflection_prompt = reflection_prompt
        self.reflection_image_path = reflection_image_path
        self.artwork_title = artwork_title
        self.docent_message = docent_message or {}
        self.message_reactions = message_reactions or []
        self.guided_question = guided_question
        self.created_date = created_date or datetime.now().isoformat()
        self.coping_style = coping_style
        self.diary_id = diary_id

        # GPT 관련 메타데이터
        self.gpt_prompt_used = gpt_prompt_used
        self.gpt_prompt_tokens = gpt_prompt_tokens
        self.gpt_docent_used = gpt_docent_used
        self.gpt_docent_tokens = gpt_docent_tokens
        self.prompt_generation_time = prompt_generation_time
        self.prompt_generation_method = prompt_generation_method
        self.docent_generation_method = docent_generation_method

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            "item_id": self.item_id,
            "user_id": self.user_id,
            "diary_text": self.diary_text,
            "emotion_keywords": self.emotion_keywords,
            "vad_scores": self.vad_scores,
            "reflection_prompt": self.reflection_prompt,
            "reflection_image_path": self.reflection_image_path,
            "artwork_title": self.artwork_title,
            "docent_message": self.docent_message,
            "message_reactions": self.message_reactions,
            "guided_question": self.guided_question,
            "created_date": self.created_date,
            "coping_style": self.coping_style,
            "diary_id": self.diary_id,
            # GPT 메타데이터
            "gpt_prompt_used": self.gpt_prompt_used,
            "gpt_prompt_tokens": self.gpt_prompt_tokens,
            "gpt_docent_used": self.gpt_docent_used,
            "gpt_docent_tokens": self.gpt_docent_tokens,
            "prompt_generation_time": self.prompt_generation_time,
            "prompt_generation_method": self.prompt_generation_method,
            "docent_generation_method": self.docent_generation_method,
        }

    def get_completion_status(self) -> Dict[str, bool]:
        """각 단계별 완료 상태 반환"""
        return {
            "reflection": bool(self.reflection_image_path),
            "artwork_title": bool(self.artwork_title),
            "docent_message": bool(
                self.docent_message
                and isinstance(self.docent_message, dict)
                and self.docent_message
            ),
            "completed": bool(
                self.docent_message
                and isinstance(self.docent_message, dict)
                and self.docent_message
            ),
        }

    def get_next_step(self) -> str:
        """다음 해야 할 단계 반환"""
        status = self.get_completion_status()

        if not status["reflection"]:
            return "reflection"
        elif not status["artwork_title"]:
            return "artwork_title"
        elif not status["docent_message"]:
            return "docent_message"
        else:
            return "completed"

    def get_gpt_usage_summary(self) -> Dict[str, Any]:
        """GPT 사용량 요약"""
        return {
            "total_tokens": self.gpt_prompt_tokens + self.gpt_docent_tokens,
            "prompt_tokens": self.gpt_prompt_tokens,
            "docent_tokens": self.gpt_docent_tokens,
            "prompt_method": self.prompt_generation_method,
            "docent_method": self.docent_generation_method,
            "generation_time": self.prompt_generation_time,
            "fully_gpt_generated": self.gpt_prompt_used and self.gpt_docent_used,
        }


class GalleryManager:
    """미술관 데이터 관리자 - MongoDB 기반"""

    def __init__(self, mongodb_client, images_dir: str = "data/gallery_images"):
        self.db: Database = mongodb_client.sync_db
        self.gallery_items = self.db.gallery_items
        self.gallery_visits = self.db.gallery_visits
        self.message_reactions = self.db.message_reactions

        self.images_dir = Path(images_dir)

        # 디렉토리 생성
        self.images_dir.mkdir(parents=True, exist_ok=True)
        (self.images_dir / "reflection").mkdir(exist_ok=True)

        self._ensure_indexes()

    def _ensure_indexes(self):
        """MongoDB 인덱스 확인 및 생성"""
        try:
            # gallery_items 컬렉션 인덱스
            self.gallery_items.create_index("user_id")
            self.gallery_items.create_index("item_id", unique=True)  # UUID 고유 인덱스
            self.gallery_items.create_index("created_date")
            self.gallery_items.create_index([("user_id", 1), ("created_date", -1)])

            # gallery_visits 컬렉션 인덱스
            self.gallery_visits.create_index("user_id")
            self.gallery_visits.create_index("item_id")

            # message_reactions 컬렉션 인덱스
            self.message_reactions.create_index("user_id")
            self.message_reactions.create_index("item_id")

            logger.info("갤러리 MongoDB 인덱스가 확인되었습니다.")
        except Exception as e:
            logger.warning(f"갤러리 인덱스 생성 중 오류: {e}")

    def create_gallery_item(
        self,
        user_id: str,
        diary_text: str,
        emotion_keywords: List[str],
        vad_scores: Tuple[float, float, float],
        reflection_prompt: str,
        reflection_image: Image.Image,
        coping_style: str = "balanced",
        gpt_prompt_tokens: int = 0,
        prompt_generation_time: float = 0.0,
        diary_id: str = None,
        emoseum_webhook_service=None
    ) -> str:
        """새 미술관 아이템 생성 (ACT 1-2단계 완료 후)"""

        # 반영 이미지 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reflection_filename = f"{user_id}_{timestamp}_reflection.png"
        reflection_path = self.images_dir / "reflection" / reflection_filename
        reflection_image.save(reflection_path)

        # MongoDB 문서 생성
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        item_id = f"{user_id}-{timestamp}"  # user-timestamp 형식
        item_doc = {
            "item_id": item_id,  # readable ID 추가
            "user_id": user_id,
            "diary_text": diary_text,
            "emotion_keywords": emotion_keywords,
            "vad_scores": list(vad_scores),
            "reflection_prompt": reflection_prompt,
            "reflection_image_path": str(reflection_path),
            "artwork_title": "",
            "docent_message": {},
            "message_reactions": [],
            "guided_question": "",
            "created_date": now.isoformat(),
            "coping_style": coping_style,
            "diary_id": diary_id,
            # GPT 메타데이터
            "gpt_prompt_used": True,
            "gpt_prompt_tokens": gpt_prompt_tokens,
            "gpt_docent_used": True,
            "gpt_docent_tokens": 0,  # 아직 생성안됨
            "prompt_generation_time": prompt_generation_time,
            "prompt_generation_method": "gpt",
            "docent_generation_method": "gpt",
        }

        try:
            result = self.gallery_items.insert_one(item_doc)
            mongo_id = str(result.inserted_id)

            logger.info(f"새 미술관 아이템이 생성되었습니다: {item_id}")
            
            # Emoseum 서버에 emotion_keywords와 vad_scores 업데이트
            if emoseum_webhook_service and diary_id:
                print(f"[DEBUG] About to send webhook: diary_id={diary_id}")
                print(f"[DEBUG] emotion_keywords={emotion_keywords}")
                print(f"[DEBUG] vad_scores={vad_scores}, type={type(vad_scores)}")
                
                import asyncio
                asyncio.create_task(
                    self._update_emotion_data_async(
                        emoseum_webhook_service, diary_id, emotion_keywords, list(vad_scores)
                    )
                )
            
            return item_id  # UUID 반환

        except Exception as e:
            logger.error(f"미술관 아이템 생성 실패: {e}")
            raise

    def complete_artwork_title(
        self,
        item_id: str,
        artwork_title: str,
        guided_question: str,
        emoseum_webhook_service=None
    ) -> bool:
        """작품 제목 작성 완료 (ACT 3단계 완료)"""

        try:
            # AI DB 업데이트
            result = self.gallery_items.update_one(
                {"item_id": item_id},
                {
                    "$set": {
                        "artwork_title": artwork_title,
                        "guided_question": guided_question,
                    }
                },
            )

            success = result.modified_count > 0
            if success:
                logger.info(f"작품 제목 작성이 완료되었습니다: 아이템 {item_id}")
                
                # artwork_title은 도슨트 메시지 완료 시 함께 업데이트됨

            return success

        except Exception as e:
            logger.error(f"작품 제목 작성 완료 실패: {e}")
            return False

    async def _update_artwork_title_async(self, webhook_service, item_id: str, artwork_title: str):
        """작품 제목을 Emoseum 서버에 비동기 업데이트"""
        try:
            gallery_item = self.gallery_items.find_one({"item_id": item_id})
            if gallery_item and gallery_item.get('diary_id'):
                result = await webhook_service.send_gallery_item_update(
                    diary_id=gallery_item['diary_id'],
                    artwork_title=artwork_title
                )
                if result.get('success'):
                    logger.info(f"Artwork title 업데이트 성공: {item_id}")
        except Exception as e:
            logger.error(f"Artwork title 비동기 업데이트 오류: {e}")
            
    async def _update_emotion_data_async(self, webhook_service, diary_id: str, emotion_keywords: List[str], vad_scores: List[float]):
        """감정 데이터(키워드, VAD)를 Emoseum 서버에 비동기 업데이트"""
        try:
            print(f"[DEBUG] Sending emotion data: diary_id={diary_id}")
            print(f"[DEBUG] Keywords: {emotion_keywords}")
            print(f"[DEBUG] VAD scores: {vad_scores}")
            print(f"[DEBUG] VAD scores type: {type(vad_scores)}")
            
            result = await webhook_service.send_gallery_item_update(
                diary_id=diary_id,
                emotion_keywords=emotion_keywords,
                vad_scores=vad_scores
            )
            
            print(f"[DEBUG] Webhook result: {result}")
            
            if result.get('success'):
                logger.info(f"Emotion data 업데이트 성공: diary_id={diary_id}")
            else:
                logger.error(f"Emotion data 업데이트 실패: {result.get('error')}")
        except Exception as e:
            print(f"[DEBUG] Exception in _update_emotion_data_async: {e}")
            logger.error(f"Emotion data 비동기 업데이트 오류: {e}")
            
    async def _update_docent_data_async(self, webhook_service, item_id: str):
        """도슨트 메시지 완료 후 모든 데이터를 Emoseum 서버에 비동기 업데이트"""
        try:
            gallery_item = self.gallery_items.find_one({"item_id": item_id})
            if gallery_item and gallery_item.get('diary_id'):
                vad_scores = gallery_item.get('vad_scores', [0, 0, 0])
                print(f"[DEBUG] Docent update - VAD scores: {vad_scores}, type: {type(vad_scores)}")
                
                result = await webhook_service.send_gallery_item_update(
                    diary_id=gallery_item['diary_id'],
                    emotion_keywords=gallery_item.get('emotion_keywords', []),
                    artwork_title=gallery_item.get('artwork_title', ''),
                    guided_question=gallery_item.get('guided_question', ''),
                    vad_scores=vad_scores
                )
                if result.get('success'):
                    logger.info(f"All gallery data 업데이트 성공: {item_id}")
        except Exception as e:
            logger.error(f"Gallery data 비동기 업데이트 오류: {e}")

    def add_docent_message(self, item_id: str, docent_message: Dict[str, Any], emoseum_webhook_service=None) -> bool:
        """도슨트 메시지 추가 (ACT 4단계 완료)"""

        try:
            # GPT 메타데이터 추출
            metadata = docent_message.get("metadata", {})
            gpt_docent_tokens = metadata.get("token_usage", {}).get("total_tokens", 0)

            # 데이터베이스 업데이트
            result = self.gallery_items.update_one(
                {"item_id": item_id},
                {
                    "$set": {
                        "docent_message": docent_message,
                        "gpt_docent_tokens": gpt_docent_tokens,
                    }
                },
            )

            success = result.modified_count > 0
            if success:
                logger.info(f"도슨트 메시지가 추가되었습니다: 아이템 {item_id}")
                
                # Emoseum 서버에 artwork_title과 guided_question 업데이트
                if emoseum_webhook_service:
                    import asyncio
                    asyncio.create_task(
                        self._update_docent_data_async(
                            emoseum_webhook_service, item_id
                        )
                    )

            return success

        except Exception as e:
            logger.error(f"도슨트 메시지 추가 실패: {e}")
            return False

    def get_gallery_item(self, item_id: str) -> Optional[GalleryItem]:
        """미술관 아이템 조회"""
        try:
            # Try to find by ObjectId first
            try:
                item_doc = self.gallery_items.find_one({"_id": ObjectId(item_id)})
                if item_doc:
                    return self._doc_to_gallery_item(item_doc)
            except:
                pass

            # If ObjectId fails, try to find by item_id field (UUID)
            item_doc = self.gallery_items.find_one({"item_id": item_id})

            if not item_doc:
                return None

            return self._doc_to_gallery_item(item_doc)

        except Exception as e:
            logger.error(f"미술관 아이템 조회 실패: {e}")
            return None

    def _doc_to_gallery_item(self, doc: Dict[str, Any]) -> GalleryItem:
        """MongoDB 문서를 GalleryItem 객체로 변환"""

        return GalleryItem(
            item_id=str(doc["_id"]),
            user_id=doc.get("user_id", ""),
            diary_text=doc.get("diary_text", ""),
            emotion_keywords=doc.get("emotion_keywords", []),
            vad_scores=tuple(doc.get("vad_scores", [0.0, 0.0, 0.0])),
            reflection_prompt=doc.get("reflection_prompt", ""),
            reflection_image_path=doc.get("reflection_image_path", ""),
            artwork_title=doc.get("artwork_title", ""),
            docent_message=doc.get("docent_message", {}),
            message_reactions=doc.get("message_reactions", []),
            guided_question=doc.get("guided_question", ""),
            created_date=doc.get("created_date", ""),
            coping_style=doc.get("coping_style", "balanced"),
            diary_id=doc.get("diary_id"),
            # GPT 메타데이터
            gpt_prompt_used=doc.get("gpt_prompt_used", True),
            gpt_prompt_tokens=doc.get("gpt_prompt_tokens", 0),
            gpt_docent_used=doc.get("gpt_docent_used", True),
            gpt_docent_tokens=doc.get("gpt_docent_tokens", 0),
            prompt_generation_time=doc.get("prompt_generation_time", 0.0),
            prompt_generation_method=doc.get("prompt_generation_method", "gpt"),
            docent_generation_method=doc.get("docent_generation_method", "gpt"),
        )

    def get_user_gallery(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[GalleryItem]:
        """사용자 미술관 조회"""
        try:
            query = {"user_id": user_id}

            # 날짜 필터링
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = date_from
                if date_to:
                    date_filter["$lte"] = date_to
                query["created_date"] = date_filter

            cursor = (
                self.gallery_items.find(query)
                .sort("created_date", -1)
                .skip(offset)
                .limit(limit)
            )

            return [self._doc_to_gallery_item(doc) for doc in cursor]

        except Exception as e:
            logger.error(f"사용자 미술관 조회 실패: {e}")
            return []

    def get_system_status(self) -> Dict[str, Any]:
        """갤러리 시스템 상태 확인"""
        try:
            # 전체 통계
            total_items = self.gallery_items.count_documents({})

            # GPT 사용률
            fully_gpt_items = self.gallery_items.count_documents(
                {"gpt_prompt_used": True, "gpt_docent_used": True}
            )

            return {
                "database_ready": True,
                "mongodb_migration_complete": True,
                "total_items": total_items,
                "gpt_adoption_rate": (
                    fully_gpt_items / total_items if total_items > 0 else 1.0
                ),
                "supports_gpt_metadata": True,
                "fallback_systems": False,
            }

        except Exception as e:
            logger.error(f"갤러리 시스템 상태 확인 실패: {e}")
            return {"database_ready": False, "error": str(e)}