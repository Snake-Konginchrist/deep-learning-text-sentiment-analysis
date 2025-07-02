# -*- coding: utf-8 -*-
"""
文本预处理工具模块
用途：提供中英文文本的清洗、分词、标记化等预处理功能
"""

import re
import jieba
import nltk
from typing import List, Union
from transformers import AutoTokenizer

class TextProcessor:
    """
    文本预处理器类
    用途：统一处理中英文文本的预处理任务
    """
    
    def __init__(self, language: str = "chinese"):
        """
        初始化文本处理器
        参数：
            language: 语言类型，支持 "chinese" 或 "english"
        """
        self.language = language
        self.stopwords = self._load_stopwords()
        
        # 下载必要的NLTK数据（仅英文需要）
        if language == "english":
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('punkt')
                nltk.download('stopwords')
    
    def _load_stopwords(self) -> set:
        """
        加载停用词表
        返回值：停用词集合
        用途：用于过滤文本中的停用词
        """
        if self.language == "chinese":
            # 中文停用词（简化版）
            stopwords = {
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
                '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
                '你', '会', '着', '没有', '看', '好', '自己', '这', '年', '还'
            }
        else:
            # 英文停用词
            try:
                from nltk.corpus import stopwords
                stopwords = set(stopwords.words('english'))
            except:
                # 如果NLTK数据不可用，使用简化的停用词列表
                stopwords = {
                    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                    'you', 'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself',
                    'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they',
                    'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who',
                    'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
                    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                    'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before',
                    'after', 'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off'
                }
        return stopwords
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本，去除特殊字符和多余空格
        参数：
            text: 待清洗的文本
        返回值：清洗后的文本
        使用场景：预处理用户输入或数据集文本
        """
        if not text or not isinstance(text, str):
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        
        # 去除URL链接
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        if self.language == "chinese":
            # 保留中文、英文、数字和常见标点
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？；：""''（）]', '', text)
        else:
            # 保留英文、数字和常见标点
            text = re.sub(r'[^a-zA-Z0-9\s.,!?;:"\'-]', '', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """
        对文本进行分词处理
        参数：
            text: 待分词的文本
            remove_stopwords: 是否移除停用词
        返回值：分词结果列表
        使用场景：将文本转换为词汇序列用于模型训练
        """
        # 首先清洗文本
        text = self.clean_text(text)
        
        if not text:
            return []
        
        if self.language == "chinese":
            # 中文分词使用jieba
            tokens = list(jieba.cut(text))
        else:
            # 英文分词按空格分割并转小写
            tokens = text.lower().split()
        
        # 过滤停用词和空词
        if remove_stopwords:
            tokens = [token for token in tokens if token and token not in self.stopwords and len(token.strip()) > 0]
        
        return tokens
    
    def preprocess_for_model(self, texts: Union[str, List[str]], model_type: str = "traditional") -> Union[List[str], dict]:
        """
        为特定模型类型预处理文本
        参数：
            texts: 单个文本或文本列表
            model_type: 模型类型，支持 "traditional"（传统模型）或 "bert"
        返回值：预处理后的文本数据
        使用场景：为不同类型的模型准备输入数据
        """
        # 统一处理为列表格式
        if isinstance(texts, str):
            texts = [texts]
        
        if model_type == "bert":
            # BERT模型使用专门的tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                "bert-base-chinese" if self.language == "chinese" else "bert-base-uncased"
            )
            
            # 清洗文本但不分词（BERT自己处理）
            cleaned_texts = [self.clean_text(text) for text in texts]
            
            # 返回tokenizer编码结果
            return tokenizer(
                cleaned_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
        else:
            # 传统模型（TextCNN, BiLSTM）使用分词结果
            processed_texts = []
            for text in texts:
                tokens = self.tokenize(text, remove_stopwords=True)
                processed_texts.append(" ".join(tokens))
            
            return processed_texts if len(processed_texts) > 1 else processed_texts[0] 