"""
AI 服務統一接口
支援 OpenAI 和 Google Gemini
"""

import logging
from typing import Optional, Dict, List
import openai
import google.generativeai as genai
from config import config

logger = logging.getLogger(__name__)


class AIService:
    """AI 服務管理器"""

    def __init__(self):
        """初始化 AI 服務"""
        self.openai_client = None
        self.gemini_models = {}

        # 初始化 OpenAI
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
            self.openai_client = openai
            logger.info("OpenAI 服務已初始化")

        # 初始化 Gemini
        if config.GOOGLE_AI_API_KEY:
            genai.configure(api_key=config.GOOGLE_AI_API_KEY)
            self.gemini_models = {
                'flash': genai.GenerativeModel(config.GEMINI_MODEL),
                'pro': genai.GenerativeModel(config.GEMINI_PRO_MODEL)
            }
            logger.info("Gemini 服務已初始化")

    def generate_prompt(self, user_requirements: Dict, provider: str = None) -> str:
        """
        根據使用者需求生成提示詞

        Args:
            user_requirements: 使用者需求字典
            provider: 指定使用的 AI 服務 ('openai' 或 'gemini')

        Returns:
            生成的提示詞內容
        """
        # 決定使用哪個 provider
        if not provider:
            provider = config.DEFAULT_AI_PROVIDER

        # 建構生成提示詞的 prompt
        system_prompt = self._build_generation_prompt(user_requirements)

        # 呼叫對應的 AI 服務
        if provider == 'openai' and self.openai_client:
            return self._generate_with_openai(system_prompt)
        elif provider == 'gemini' and self.gemini_models:
            return self._generate_with_gemini(system_prompt)
        else:
            raise ValueError(f"AI 服務不可用: {provider}")

    def optimize_prompt(self, original_prompt: str, provider: str = None) -> Dict:
        """
        優化現有提示詞

        Args:
            original_prompt: 原始提示詞
            provider: 指定使用的 AI 服務

        Returns:
            {'optimized': 優化後的提示詞, 'suggestions': 改進建議列表}
        """
        if not provider:
            provider = config.DEFAULT_AI_PROVIDER

        optimization_prompt = f"""請優化以下提示詞，使其更清晰、更有效：

原始提示詞:
{original_prompt}

請提供:
1. 優化後的提示詞
2. 3-5 個具體的改進建議

回應格式（JSON）:
{{
  "optimized": "優化後的完整提示詞",
  "suggestions": ["建議1", "建議2", "建議3"]
}}
"""

        if provider == 'openai' and self.openai_client:
            result = self._generate_with_openai(optimization_prompt, response_format="json")
        elif provider == 'gemini' and self.gemini_models:
            result = self._generate_with_gemini(optimization_prompt, response_format="json")
        else:
            raise ValueError(f"AI 服務不可用: {provider}")

        # 解析 JSON 回應
        import json
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                'optimized': result,
                'suggestions': []
            }

    def analyze_quality(self, prompt: str, provider: str = None) -> Dict:
        """
        分析提示詞質量

        Args:
            prompt: 要分析的提示詞
            provider: 指定使用的 AI 服務

        Returns:
            {'score': 評分(0-100), 'strengths': 優點列表, 'weaknesses': 缺點列表}
        """
        if not provider:
            provider = config.DEFAULT_AI_PROVIDER

        analysis_prompt = f"""請分析以下提示詞的質量：

{prompt}

請評估以下方面：
1. 清晰度
2. 完整性
3. 結構性
4. 可執行性

回應格式（JSON）:
{{
  "score": 85,
  "strengths": ["優點1", "優點2"],
  "weaknesses": ["缺點1", "缺點2"]
}}
"""

        if provider == 'openai' and self.openai_client:
            result = self._generate_with_openai(analysis_prompt, response_format="json")
        elif provider == 'gemini' and self.gemini_models:
            result = self._generate_with_gemini(analysis_prompt, response_format="json")
        else:
            raise ValueError(f"AI 服務不可用: {provider}")

        import json
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                'score': 75,
                'strengths': [],
                'weaknesses': []
            }

    def _build_generation_prompt(self, requirements: Dict) -> str:
        """建構生成提示詞的 system prompt"""
        prompt = f"""你是一個專業的提示詞工程師。請根據以下需求生成一個詳細、有效的提示詞：

專案類型: {requirements.get('project_type', '未指定')}
主要功能: {', '.join(requirements.get('features', []))}
詳細程度: {requirements.get('detail_level', '中等')}
語言風格: {requirements.get('language', '繁體中文')}
目標平台: {requirements.get('target_platform', '未指定')}

額外需求:
{requirements.get('additional_requirements', '無')}

請生成一個結構完整、清晰明確的提示詞，包含：
1. 專案概述
2. 技術需求
3. 功能規格
4. 實作細節
5. 測試要求
6. 部署指南
"""
        return prompt

    def _generate_with_openai(self, prompt: str, response_format: str = "text") -> str:
        """使用 OpenAI 生成內容"""
        try:
            messages = [
                {"role": "system", "content": "你是一個專業的提示詞工程師和技術文件撰寫專家。"},
                {"role": "user", "content": prompt}
            ]

            if response_format == "json":
                response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
            else:
                response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.7
                )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API 錯誤: {e}")
            raise

    def _generate_with_gemini(self, prompt: str, response_format: str = "text", model_type: str = "flash") -> str:
        """使用 Gemini 生成內容"""
        try:
            model = self.gemini_models.get(model_type, self.gemini_models['flash'])

            if response_format == "json":
                prompt = f"{prompt}\n\n請以 JSON 格式回應。"

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Gemini API 錯誤: {e}")
            raise

    def get_embedding(self, text: str, provider: str = None) -> List[float]:
        """
        取得文本的向量嵌入

        Args:
            text: 要嵌入的文本
            provider: 指定使用的服務

        Returns:
            向量列表
        """
        if not provider:
            provider = config.EMBEDDING_PROVIDER

        if provider == 'openai' and self.openai_client:
            return self._get_openai_embedding(text)
        else:
            # 使用 sentence-transformers（在 RAG service 中實作）
            return []

    def _get_openai_embedding(self, text: str) -> List[float]:
        """使用 OpenAI Embeddings API"""
        try:
            response = self.openai_client.embeddings.create(
                model=config.OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI Embedding 錯誤: {e}")
            raise

    def is_available(self, provider: str = None) -> bool:
        """檢查 AI 服務是否可用"""
        if provider == 'openai':
            return self.openai_client is not None
        elif provider == 'gemini':
            return len(self.gemini_models) > 0
        else:
            return self.openai_client is not None or len(self.gemini_models) > 0
