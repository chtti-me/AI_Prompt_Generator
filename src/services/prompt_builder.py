"""
提示詞建構器
將使用者輸入轉換為結構化的提示詞
"""

from typing import Dict, List
from datetime import datetime


class PromptBuilder:
    """提示詞建構器"""

    # 專案類型對應的基礎架構
    PROJECT_TYPES = {
        'web_app': {
            'name': 'Web 應用程式',
            'tech_stack': ['HTML', 'CSS', 'JavaScript', 'Backend Framework'],
            'sections': ['UI/UX 設計', '前端實作', '後端 API', '資料庫設計', '部署']
        },
        'cli_tool': {
            'name': '命令列工具',
            'tech_stack': ['Python/Node.js/Go'],
            'sections': ['命令解析', '核心功能', '錯誤處理', '文件', '打包發布']
        },
        'api_service': {
            'name': 'API 服務',
            'tech_stack': ['REST/GraphQL', 'Database', 'Authentication'],
            'sections': ['端點設計', '資料模型', '認證授權', 'API 文件', '測試']
        },
        'data_analysis': {
            'name': '資料分析專案',
            'tech_stack': ['Python', 'Pandas', 'Visualization'],
            'sections': ['資料載入', '清理處理', '分析探索', '視覺化', '報告']
        },
        'tutorial': {
            'name': '教學專案',
            'tech_stack': ['依教學內容而定'],
            'sections': ['學習目標', '前置知識', '步驟教學', '實作練習', '延伸閱讀']
        }
    }

    # 詳細程度對應的內容深度
    DETAIL_LEVELS = {
        'basic': {'name': '基礎', 'depth': 1, 'examples': False},
        'intermediate': {'name': '中等', 'depth': 2, 'examples': True},
        'detailed': {'name': '詳細', 'depth': 3, 'examples': True},
        'ultra_detailed': {'name': '超詳細', 'depth': 4, 'examples': True}
    }

    def __init__(self):
        pass

    def build(self, requirements: Dict) -> str:
        """
        建構提示詞

        Args:
            requirements: 使用者需求字典
                - project_type: 專案類型
                - features: 功能列表
                - detail_level: 詳細程度
                - language: 語言
                - additional_requirements: 額外需求

        Returns:
            完整的提示詞文本
        """
        sections = []

        # 1. 標題與概述
        sections.append(self._build_header(requirements))

        # 2. 專案概述
        sections.append(self._build_overview(requirements))

        # 3. 技術需求
        sections.append(self._build_tech_requirements(requirements))

        # 4. 功能規格
        sections.append(self._build_features(requirements))

        # 5. 實作細節（根據詳細程度）
        if self._should_include_implementation(requirements):
            sections.append(self._build_implementation(requirements))

        # 6. 測試需求
        if self._should_include_testing(requirements):
            sections.append(self._build_testing(requirements))

        # 7. 部署指南
        if self._should_include_deployment(requirements):
            sections.append(self._build_deployment(requirements))

        # 8. 額外需求
        if requirements.get('additional_requirements'):
            sections.append(self._build_additional(requirements))

        # 9. 頁尾
        sections.append(self._build_footer())

        return '\n\n'.join(sections)

    def _build_header(self, req: Dict) -> str:
        """建構標題"""
        project_type = self.PROJECT_TYPES.get(req.get('project_type', 'web_app'), {})
        title = project_type.get('name', '專案')

        return f"""# [>>] {title}提示詞

> **專案類型**: {title}
> **生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **詳細程度**: {req.get('detail_level', 'intermediate')}

---"""

    def _build_overview(self, req: Dict) -> str:
        """建構專案概述"""
        features = req.get('features', [])
        feature_list = '\n'.join([f"- [OK] **{f}**" for f in features])

        return f"""## [!] 專案概述

我要建立一個專案，包含以下功能：

{feature_list}

---"""

    def _build_tech_requirements(self, req: Dict) -> str:
        """建構技術需求"""
        project_type = self.PROJECT_TYPES.get(req.get('project_type', 'web_app'), {})
        tech_stack = project_type.get('tech_stack', [])

        tech_list = '\n'.join([f"- {tech}" for tech in tech_stack])

        return f"""## 技術需求

### 核心技術棧

{tech_list}

### 開發環境

- **Python**: 3.12+（如適用）
- **Node.js**: 18+（如適用）
- **資料庫**: SQLite/PostgreSQL/MySQL（依需求）

---"""

    def _build_features(self, req: Dict) -> str:
        """建構功能規格"""
        features = req.get('features', [])
        detail_level = req.get('detail_level', 'intermediate')

        feature_sections = []
        for i, feature in enumerate(features, 1):
            if detail_level in ['detailed', 'ultra_detailed']:
                feature_sections.append(f"""### {i}. {feature}

**功能需求**:
- 主要功能描述
- 使用者操作流程
- 資料處理邏輯

**技術實作**:
- 使用的技術/套件
- API 端點（如適用）
- 資料模型（如適用）

**驗收標準**:
- 功能正常運作
- 效能符合要求
- 錯誤處理完善
""")
            else:
                feature_sections.append(f"### {i}. {feature}\n\n（詳細規格）")

        return f"""## [*] 功能詳細規格

{chr(10).join(feature_sections)}

---"""

    def _build_implementation(self, req: Dict) -> str:
        """建構實作細節"""
        return """## [PC] 實作細節

### 專案結構

```
project/
├── src/           # 原始碼
├── tests/         # 測試
├── docs/          # 文件
├── config/        # 配置
└── README.md      # 說明文件
```

### 核心模組

（根據專案需求詳細說明各模組的實作）

---"""

    def _build_testing(self, req: Dict) -> str:
        """建構測試需求"""
        return """## [TEST] 測試需求

### 單元測試
- 測試核心功能
- 測試邊界條件
- 測試錯誤處理

### 整合測試
- 測試模組間互動
- 測試 API 端點（如適用）
- 測試資料流程

### 端到端測試
- 測試完整使用流程
- 測試使用者情境

---"""

    def _build_deployment(self, req: Dict) -> str:
        """建構部署指南"""
        platform = req.get('target_platform', 'cross_platform')

        return f"""## [DEPLOY] 部署指南

### 目標平台: {platform}

### 部署步驟

1. 環境準備
2. 依賴安裝
3. 配置設定
4. 建置專案
5. 啟動服務
6. 驗證部署

---"""

    def _build_additional(self, req: Dict) -> str:
        """建構額外需求"""
        additional = req.get('additional_requirements', '')
        return f"""## [+] 額外需求

{additional}

---"""

    def _build_footer(self) -> str:
        """建構頁尾"""
        return f"""## [!] 請提供

1. [OK] 完整的專案結構
2. [OK] 所有功能的實作程式碼
3. [OK] 配置檔案
4. [OK] 說明文件
5. [OK] 測試程式碼

---

**© {datetime.now().year} | 提示詞生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
"""

    def _should_include_implementation(self, req: Dict) -> bool:
        """是否包含實作細節"""
        detail_level = req.get('detail_level', 'intermediate')
        return detail_level in ['detailed', 'ultra_detailed']

    def _should_include_testing(self, req: Dict) -> bool:
        """是否包含測試需求"""
        features = req.get('features', [])
        return 'testing' in features or len(features) > 3

    def _should_include_deployment(self, req: Dict) -> bool:
        """是否包含部署指南"""
        features = req.get('features', [])
        return 'deployment' in features or req.get('detail_level') in ['detailed', 'ultra_detailed']
