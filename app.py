"""
AI Prompt Generator Platform - Flask 主應用
智能提示詞生成平台
"""

import os
import logging
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

# 導入配置
from config import config

# 導入服務
from src.services.ai_service import AIService
from src.services.rag_service import RAGService
from src.services.prompt_builder import PromptBuilder

# 導入資料庫管理器
from src.utils.db_manager import init_db

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 建立 Flask 應用
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# 啟用 CORS
CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})

# 初始化服務
db_manager = None
ai_service = None
rag_service = None
prompt_builder = None


def init_services():
    """初始化所有服務"""
    global db_manager, ai_service, rag_service, prompt_builder

    logger.info("正在初始化服務...")

    # 初始化資料庫
    db_manager = init_db(config.DATABASE_URL)
    logger.info("資料庫已初始化")

    # 初始化 AI 服務
    ai_service = AIService()
    logger.info(f"AI 服務已初始化: {config.get_ai_status()}")

    # 初始化 RAG 服務（如果啟用）
    if config.ENABLE_RAG:
        try:
            rag_service = RAGService()
            logger.info("RAG 服務已初始化")
        except Exception as e:
            logger.warning(f"RAG 服務初始化失敗: {e}")
            rag_service = None

    # 初始化 Prompt Builder
    prompt_builder = PromptBuilder()
    logger.info("Prompt Builder 已初始化")


# ============================================================================
# 路由 - 頁面
# ============================================================================

@app.route('/')
def index():
    """首頁 - 互動式建置教學"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """系統儀表板（原首頁）"""
    return render_template('dashboard.html')


@app.route('/generator')
def generator():
    """提示詞生成器頁面"""
    return render_template('generator.html')


@app.route('/library')
def library():
    """RAG 知識庫頁面"""
    return render_template('library.html')


@app.route('/history')
def history():
    """歷史記錄頁面"""
    return render_template('history.html')


@app.route('/settings')
def settings():
    """設定頁面"""
    return render_template('settings.html')


# ============================================================================
# API 路由 - 系統
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Prompt Generator Platform',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """取得系統狀態"""
    status = {
        'ai_service': {
            'available': ai_service is not None,
            'openai': ai_service.is_available('openai') if ai_service else False,
            'gemini': ai_service.is_available('gemini') if ai_service else False
        },
        'rag_service': {
            'enabled': config.ENABLE_RAG,
            'available': rag_service is not None
        },
        'google_sheets': {
            'enabled': config.GOOGLE_SHEETS_ENABLED
        }
    }

    if rag_service:
        status['rag_service']['stats'] = rag_service.get_stats()

    return jsonify(status)


# ============================================================================
# API 路由 - 提示詞生成
# ============================================================================

@app.route('/api/generate', methods=['POST'])
def generate_prompt():
    """生成提示詞"""
    try:
        data = request.json
        requirements = {
            'project_type': data.get('project_type', 'web_app'),
            'features': data.get('features', []),
            'detail_level': data.get('detail_level', 'intermediate'),
            'language': data.get('language', 'zh_tw'),
            'target_platform': data.get('target_platform', 'cross_platform'),
            'additional_requirements': data.get('additional_requirements', '')
        }

        # 使用 AI 生成還是模板生成
        use_ai = data.get('use_ai', False)
        ai_provider = data.get('ai_provider', config.DEFAULT_AI_PROVIDER)

        if use_ai and ai_service and ai_service.is_available(ai_provider):
            # 使用 AI 生成
            logger.info(f"使用 AI 生成提示詞: {ai_provider}")
            generated_content = ai_service.generate_prompt(requirements, ai_provider)
        else:
            # 使用模板生成
            logger.info("使用模板生成提示詞")
            generated_content = prompt_builder.build(requirements)

        # 儲存到資料庫（簡化版，實際應該使用 ORM）
        # TODO: 實作完整的資料庫儲存邏輯

        return jsonify({
            'success': True,
            'content': generated_content,
            'method': 'ai' if use_ai else 'template',
            'provider': ai_provider if use_ai else None
        })

    except Exception as e:
        logger.error(f"生成提示詞失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_prompt():
    """優化提示詞"""
    try:
        data = request.json
        original_prompt = data.get('prompt', '')
        ai_provider = data.get('provider', config.DEFAULT_AI_PROVIDER)

        if not ai_service or not ai_service.is_available(ai_provider):
            return jsonify({
                'success': False,
                'error': 'AI 服務不可用'
            }), 503

        result = ai_service.optimize_prompt(original_prompt, ai_provider)

        return jsonify({
            'success': True,
            'optimized': result.get('optimized', ''),
            'suggestions': result.get('suggestions', [])
        })

    except Exception as e:
        logger.error(f"優化提示詞失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API 路由 - RAG 知識庫
# ============================================================================

@app.route('/api/rag/search', methods=['POST'])
def rag_search():
    """RAG 語義搜尋"""
    try:
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG 服務未啟用'
            }), 503

        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', config.RAG_TOP_K)

        results = rag_service.search(query, top_k)

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        logger.error(f"RAG 搜尋失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/upload', methods=['POST'])
def rag_upload():
    """上傳文件到 RAG 知識庫"""
    try:
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG 服務未啟用'
            }), 503

        # 檢查檔案
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '沒有上傳檔案'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '檔案名稱為空'
            }), 400

        # 取得檔案副檔名
        filename = file.filename.lower()
        file_ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
        
        # 根據檔案類型提取內容
        content = None
        if file_ext == 'pdf':
            # 處理 PDF 檔案
            try:
                from PyPDF2 import PdfReader
                import io
                pdf_file = io.BytesIO(file.read())
                pdf_reader = PdfReader(pdf_file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
                logger.info(f"成功解析 PDF 檔案: {file.filename}")
            except Exception as e:
                logger.error(f"PDF 解析失敗: {e}")
                return jsonify({
                    'success': False,
                    'error': f'PDF 檔案解析失敗: {str(e)}'
                }), 400
                
        elif file_ext == 'docx':
            # 處理 Word 檔案
            try:
                from docx import Document
                import io
                doc_file = io.BytesIO(file.read())
                doc = Document(doc_file)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                logger.info(f"成功解析 DOCX 檔案: {file.filename}")
            except Exception as e:
                logger.error(f"DOCX 解析失敗: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Word 檔案解析失敗: {str(e)}'
                }), 400
                
        else:
            # 處理文字檔案（.txt, .md 等）
            file_bytes = file.read()
            
            # 嘗試多種編碼
            encodings = ['utf-8', 'utf-8-sig', 'big5', 'gb2312', 'gbk', 'gb18030', 'windows-1252', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    content = file_bytes.decode(encoding)
                    logger.info(f"成功使用 {encoding} 編碼讀取檔案: {file.filename}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                # 如果所有編碼都失敗，使用 errors='replace' 或 'ignore'
                try:
                    content = file_bytes.decode('utf-8', errors='replace')
                    logger.warning(f"使用 UTF-8 並替換無效字元讀取檔案: {file.filename}")
                except Exception as e:
                    logger.error(f"檔案解碼失敗: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'無法讀取檔案內容，可能是編碼問題: {str(e)}'
                    }), 400

        if not content or not content.strip():
            return jsonify({
                'success': False,
                'error': '檔案內容為空或無法提取文字'
            }), 400

        doc_id = f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 新增到 RAG 知識庫
        success = rag_service.add_document(
            doc_id=doc_id,
            content=content,
            metadata={'filename': file.filename, 'file_type': file_ext}
        )

        if success:
            return jsonify({
                'success': True,
                'doc_id': doc_id,
                'filename': file.filename
            })
        else:
            return jsonify({
                'success': False,
                'error': '新增文件失敗'
            }), 500

    except Exception as e:
        logger.error(f"上傳文件失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/documents', methods=['GET'])
def rag_documents():
    """取得所有已上傳的文件列表"""
    try:
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG 服務未啟用'
            }), 503

        documents = rag_service.get_all_documents()
        return jsonify({
            'success': True,
            'documents': documents
        })

    except Exception as e:
        logger.error(f"取得文件列表失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 錯誤處理
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """404 錯誤處理"""
    return jsonify({'error': '找不到資源'}), 404


@app.errorhandler(500)
def internal_error(e):
    """500 錯誤處理"""
    logger.error(f"內部伺服器錯誤: {e}")
    return jsonify({'error': '內部伺服器錯誤'}), 500


# ============================================================================
# 應用啟動
# ============================================================================

if __name__ == '__main__':
    # 初始化服務
    init_services()

    # 啟動應用
    logger.info(f"正在啟動 AI Prompt Generator Platform...")
    logger.info(f"伺服器位址: http://{config.HOST}:{config.PORT}")

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
