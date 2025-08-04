# Emoseum

감정 일기 기반 이미지 생성 및 자기 전시 시스템을 활용한 우울증 디지털 치료제

## 📖 프로젝트 소개

Emoseum은 ACT(Acceptance and Commitment Therapy) 이론에 기반한 디지털 치료 시스템이다. 사용자가 작성한 감정 일기를 GPT와 Stable Diffusion을 통해 개인화된 이미지로 시각화하여, 감정 수용과 심리적 유연성을 증진시키는 혁신적인 치료적 경험을 제공한다.

본 시스템은 4단계 ACT 치료 여정(The Moment → Reflection → Defusion → Closure)을 통해 사용자가 자신의 감정을 안전하게 탐색하고 수용할 수 있도록 도우며, 궁극적으로 희망을 찾아가는 과정을 지원한다.

## 📅 개발 기간

**2024년 6월 29일 ~ 8월 14일** (약 7주)

## 👥 개발자 소개

### 팀 구성 및 역할 분담

| 역할           | 개발자 | GitHub                                       | 담당 업무                                                                                                                              |
| -------------- | ------ | -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **AI 개발**    | 박용성 | [@reo91004](https://github.com/reo91004)     | • GPT 프롬프트 엔지니어링 (이미지 생성, 큐레이터)<br>• Stable Diffusion 이미지 생성<br>• GPT API 서비스<br>• LoRA/DRaFT+ 개인화 시스템 |
| **AI 개발**    | 송인규 | [@enqueue01](https://github.com/enqueue01)   | • GPT 프롬프트 엔지니어링 (이미지 생성, 큐레이터)<br>• 안전성 검증 시스템<br>• GPT API 서비스<br>• 비용 추적 및 모니터링               |
| **백엔드**     | 이선진 | [@Seonjin-13](https://github.com/Seonjin-13) | • FastAPI 서버 구축<br>• 데이터베이스 설계<br>• 사용자 관리 시스템<br>• Unity 연동 API                                                 |
| **Unity 개발** | 추성재 | [@qOLOp](https://github.com/qOLOp)           | • 모바일 게임 UI/UX<br>• 미술관 인터페이스<br>• 클라이언트-서버 통신<br>• 게임화 요소 구현                                             |

## 💻 개발 환경

### 시스템 요구사항

- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 이상
- **GPU**: CUDA 11.8+ 지원 GPU (권장) 또는 Apple Silicon Mac
- **메모리**: 최소 8GB RAM
- **Unity**: 2022.3 LTS

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/Emoseum/AI_Backend.git
cd AI_Backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 등 설정

# 시스템 실행
python main.py
```

## 🛠 기술 스택

### AI/ML

- **OpenAI GPT-4**: 프롬프트 생성 및 큐레이터 메시지
- **Stable Diffusion 1.5**: 이미지 생성
- **PyTorch**: 딥러닝 프레임워크
- **Transformers**: 자연어 처리
- **LoRA & DRaFT+**: 개인화 모델 학습

### 백엔드

- **FastAPI**: 비동기 웹 프레임워크
- **SQLite**: 경량 데이터베이스
- **SQLAlchemy**: ORM
- **Uvicorn**: ASGI 서버

### 프론트엔드

- **Unity 2022.3 LTS**: 모바일 게임 엔진
- **C#**: Unity 스크립팅

### 데이터 처리

- **NumPy**: 수치 연산
- **Pandas**: 데이터 분석
- **Pillow**: 이미지 처리
- **TextBlob**: 감정 분석

### 개발 도구

- **Python-dotenv**: 환경 변수 관리
- **PyYAML**: 설정 파일 관리
- **Pytest**: 테스트 프레임워크
- **Black**: 코드 포매팅

## ✨ 주요 기능

### 🎭 ACT 기반 4단계 치료 여정

#### 1. The Moment - 감정 인식

- 자유로운 감정 일기 작성
- VAD(Valence-Arousal-Dominance) 모델 기반 실시간 감정 분석
- 감정 키워드 자동 추출

#### 2. Reflection - 감정 시각화

- GPT 기반 개인화 프롬프트 생성
- Stable Diffusion을 통한 감정 이미지 생성
- 대처 스타일별 맞춤형 시각적 표현

#### 3. Defusion - 인지적 탈융합

- 방명록 작성을 통한 감정 거리두기
- 제목과 태그를 통한 감정 재구성
- 부정적 사고 패턴 완화

#### 4. Closure - 희망 발견

- GPT 기반 개인화 큐레이터 메시지
- 치료적 통찰과 격려 제공
- 미래 지향적 시각 형성

### 🎯 3단계 개인화 시스템

#### Level 1: 기본 프로파일링

- **심리검사**: PHQ-9, CES-D, MEAQ, CISS
- **대처 스타일 분류**: 회피형/직면형/균형형
- **시각적 선호도**: 화풍, 색감, 복잡도 설정

#### Level 2: GPT 기반 학습

- 방명록 반응 데이터 수집
- 메시지 참여도 분석
- 실시간 개인화 조정

#### Level 3: 고급 AI 개인화

- **LoRA 훈련**: 50개 이상 긍정적 반응 시
- **DRaFT+ 강화학습**: 30개 이상 완성된 여정 시
- 사용자별 최적화된 AI 모델

### 🏛 디지털 미술관

- 개인 감정 여정 아카이브
- 시간에 따른 감정 변화 추적
- 과거 작품 재감상 및 성찰

### 🛡 안전성 시스템

- 치료적 부적절 응답 필터링
- 위험 신호 감지 및 전문가 상담 권유
- YAML 기반 안전성 규칙 관리

## 🏗 프로젝트 아키텍처

### 시스템 구조

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Unity Client  │    │  FastAPI Server │    │  AI/ML Engine   │
│                 │    │                 │    │                 │
│ • Game UI       │◄──►│ • RESTful API   │◄──►│ • GPT Service   │
│ • Gallery View  │    │ • User Manager  │    │ • Image Gen     │
│ • Mobile UX     │    │ • Data Storage  │    │ • Personalization│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 모듈 구조

```
src/
├── core/
│   └── act_therapy_system.py      # ACT 치료 시스템 코어
├── managers/
│   ├── user_manager.py            # 사용자 프로필 관리
│   ├── gallery_manager.py         # 감정 여정 데이터 관리
│   └── personalization_manager.py # 개인화 엔진
├── services/
│   ├── gpt_service.py             # GPT API 서비스
│   └── image_generator.py         # Stable Diffusion 이미지 생성
├── therapy/
│   ├── prompt_architect.py        # ACT 기반 프롬프트 생성
│   └── curator_message.py         # 큐레이터 메시지 시스템
├── training/
│   ├── lora_trainer.py           # LoRA 개인화 훈련
│   └── draft_trainer.py          # DRaFT+ 강화학습
└── utils/
    ├── safety_validator.py       # 안전성 검증
    └── cost_tracker.py           # API 비용 추적
```

### 데이터 흐름

```
감정 일기 입력
    ↓
VAD 기반 감정 분석
    ↓
대처 스타일별 프롬프트 생성 (GPT)
    ↓
개인화 이미지 생성 (Stable Diffusion)
    ↓
방명록 작성 (Defusion)
    ↓
큐레이터 메시지 생성 (GPT)
    ↓
개인화 데이터 학습 및 업데이트
```

### 데이터베이스 스키마

- **Users**: 사용자 기본 정보 및 심리검사 결과
- **GalleryItems**: 감정 여정 데이터 (일기, 이미지, 방명록, 메시지)
- **PersonalizationData**: 개인화 학습 데이터
- **CostTracking**: API 사용량 및 비용 추적

## 🔬 연구적 가치

### 혁신성

- ACT 이론의 디지털 치료 적용
- GPT와 Stable Diffusion을 활용한 감정 시각화
- 3단계 개인화 시스템의 점진적 학습
- 게임화를 통한 치료적 접근성 향상

### 주요 연구 질문

1. 대처 스타일별 차별화된 시각화가 치료 효과에 미치는 영향
2. 방명록 시스템을 통한 인지적 탈융합의 효과성
3. 개인화 수준(Level 1-3)에 따른 사용자 만족도 및 치료 성과 차이
4. 디지털 치료제의 임상적 유효성 검증

### 확장 가능성

- FDA 승인을 위한 임상 시험 준비
- 다양한 정신건강 질환으로의 적용 확대
- 멀티모달 AI를 활용한 고도화
- 메타버스 환경에서의 집단 치료 프로그램

---
