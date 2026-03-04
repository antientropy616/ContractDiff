#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 处理模块
支持 PDF 文档的读取和转换
"""

import os
import tempfile
from utils.logger import logger
from utils.error_handler import FileLoadError, FileFormatError


class PDFProcessor:
    """PDF 文档处理器"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def is_pdf(self, file_path):
        """检查文件是否为 PDF"""
        return os.path.splitext(file_path)[1].lower() in self.supported_formats
    
    def pdf_to_text(self, pdf_path):
        """
        将 PDF 转换为文本
        
        注意：实际部署需要安装 pdfplumber 或 PyMuPDF
        pip install pdfplumber
        """
        try:
            import pdfplumber
            
            logger.info(f"开始转换 PDF：{pdf_path}")
            
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(f"--- 第 {i} 页 ---\n{text}")
            
            full_text = "\n\n".join(text_content)
            logger.info(f"PDF 转换成功，共 {len(pdf.pages)} 页")
            
            return full_text
            
        except ImportError:
            logger.error("缺少 pdfplumber 库，请安装：pip install pdfplumber")
            raise FileLoadError(
                "PDF 处理功能需要安装额外依赖：pdfplumber\n请运行：pip install pdfplumber",
                pdf_path
            )
        except Exception as e:
            logger.error(f"PDF 转换失败：{e}", exc_info=True)
            raise FileLoadError(f"PDF 文件读取失败：{str(e)}", pdf_path)
    
    def pdf_to_docx(self, pdf_path, output_path=None):
        """
        将 PDF 转换为 Word 文档
        
        注意：实际部署需要安装 pdf2docx
        pip install pdf2docx
        """
        try:
            from pdf2docx import Converter
            
            logger.info(f"开始转换 PDF 到 Word：{pdf_path}")
            
            if output_path is None:
                output_path = os.path.splitext(pdf_path)[0] + '.docx'
            
            cv = Converter(pdf_path)
            cv.convert(output_path)
            cv.close()
            
            logger.info(f"PDF 转换成功：{output_path}")
            return output_path
            
        except ImportError:
            logger.error("缺少 pdf2docx 库，请安装：pip install pdf2docx")
            raise FileLoadError(
                "PDF 转 Word 功能需要安装额外依赖：pdf2docx\n请运行：pip install pdf2docx",
                pdf_path
            )
        except Exception as e:
            logger.error(f"PDF 转 Word 失败：{e}", exc_info=True)
            raise FileLoadError(f"PDF 转换失败：{str(e)}", pdf_path)
    
    def extract_pdf_info(self, pdf_path):
        """提取 PDF 基本信息"""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                info = {
                    'pages': len(pdf.pages),
                    'metadata': pdf.metadata or {},
                    'file_size': os.path.getsize(pdf_path)
                }
                return info
                
        except Exception as e:
            logger.error(f"提取 PDF 信息失败：{e}")
            return None


class DocumentLoader:
    """统一文档加载器（支持 Word 和 PDF）"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def load_document(self, file_path):
        """
        加载文档（自动识别格式）
        
        返回：文档对象或文本内容
        """
        if not os.path.exists(file_path):
            raise FileLoadError(f"文件不存在：{file_path}", file_path)
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._load_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._load_word(file_path)
        else:
            raise FileFormatError(
                f"不支持的文件格式：{file_ext}",
                expected_format=".docx 或 .pdf"
            )
    
    def _load_pdf(self, pdf_path):
        """加载 PDF 文档"""
        logger.info(f"加载 PDF 文档：{pdf_path}")
        
        # 策略 1：直接提取文本进行对比
        text_content = self.pdf_processor.pdf_to_text(pdf_path)
        
        # 创建临时 Word 文档用于后续处理
        from docx import Document
        
        temp_doc = Document()
        
        # 按段落分割文本
        paragraphs = text_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                temp_doc.add_paragraph(para.strip())
        
        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.docx',
            delete=False
        )
        temp_path = temp_file.name
        temp_file.close()
        
        temp_doc.save(temp_path)
        logger.info(f"PDF 已转换为临时 Word 文档：{temp_path}")
        
        return temp_path, True  # 返回临时文件路径和是否为临时文件标记
    
    def _load_word(self, word_path):
        """加载 Word 文档"""
        logger.info(f"加载 Word 文档：{word_path}")
        return word_path, False  # 原始文件，非临时文件
    
    def cleanup_temp_file(self, temp_path):
        """清理临时文件"""
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"已清理临时文件：{temp_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败：{e}")
