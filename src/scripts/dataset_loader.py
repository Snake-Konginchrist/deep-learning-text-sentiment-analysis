# -*- coding: utf-8 -*-
"""
数据集加载模块
用途：从Hugging Face下载并处理中英文情感分析数据集，支持Kaggle备用下载
"""

import os
import pandas as pd
import requests
import zipfile
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from datasets import load_dataset, Dataset
from sklearn.model_selection import train_test_split
from ..utils.config import Config
from ..utils.text_processor import TextProcessor

class DatasetLoader:
    """
    数据集加载器类
    用途：统一管理数据集的下载、加载和预处理，支持多数据源
    """
    
    def __init__(self, language: str = "chinese"):
        """
        初始化数据集加载器
        参数：
            language: 语言类型，支持 "chinese" 或 "english"
        """
        self.language = language
        self.dataset_name = Config.DATASETS[language]
        self.text_processor = TextProcessor(language)
        
        # Kaggle备用数据源配置
        self.kaggle_sources = {
            "chinese": {
                "dataset_name": "kaggleyxz/chnsenticorp", 
                "url": "https://www.kaggle.com/datasets/kaggleyxz/chnsenticorp/download",
                "file_name": "chnsenticorp.csv",
                "text_column": "text",
                "label_column": "label"
            },
            "english": {
                "dataset_name": "lakshmi25npathi/imdb-dataset-of-50k-movie-reviews",
                "url": "https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews/download", 
                "file_name": "IMDB Dataset.csv",
                "text_column": "review",
                "label_column": "sentiment"
            }
        }
        
        # 确保数据目录存在
        Config.create_directories()
    
    def download_from_huggingface(self, cache_dir: str = None) -> Optional[Dataset]:
        """
        从Hugging Face下载数据集
        参数：
            cache_dir: 缓存目录路径，默认使用项目data目录
        返回值：下载的数据集对象或None（如果失败）
        """
        if cache_dir is None:
            cache_dir = str(Config.DATASETS_DIR)
        
        print(f"正在从Hugging Face下载 {self.language} 数据集: {self.dataset_name}")
        
        try:
            if self.language == "chinese":
                # 下载中文情感数据集（信任远程代码）
                dataset = load_dataset(self.dataset_name, cache_dir=cache_dir, trust_remote_code=True)
                # ChnSentiCorp只有训练集，需要手动分割
                if 'train' in dataset:
                    dataset = dataset['train']
                else:
                    # 如果数据结构不同，取第一个可用分割
                    dataset = dataset[list(dataset.keys())[0]]
                    
            else:
                # 下载英文电影评论数据集
                dataset = load_dataset(self.dataset_name, cache_dir=cache_dir, trust_remote_code=True)
                # IMDb有train和test分割，合并后重新分割
                train_data = dataset['train']
                test_data = dataset['test']
                
                # 合并训练集和测试集
                combined_texts = train_data['text'] + test_data['text']
                combined_labels = train_data['label'] + test_data['label']
                
                # 创建新的数据集
                dataset = Dataset.from_dict({
                    'text': combined_texts,
                    'label': combined_labels
                })
            
            print(f"Hugging Face数据集下载完成，共 {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            print(f"从Hugging Face下载数据集失败: {str(e)}")
            return None
    
    def download_from_kaggle(self, cache_dir: str = None) -> Optional[Dataset]:
        """
        从Kaggle下载数据集
        参数：
            cache_dir: 缓存目录路径，默认使用项目data目录
        返回值：下载的数据集对象或None（如果失败）
        """
        if cache_dir is None:
            cache_dir = str(Config.DATASETS_DIR)
        
        kaggle_config = self.kaggle_sources.get(self.language)
        if not kaggle_config:
            print(f"不支持的语言类型: {self.language}")
            return None
        
        print(f"正在从Kaggle下载 {self.language} 数据集: {kaggle_config['dataset_name']}")
        
        try:
            # 检查是否已安装kaggle API
            try:
                import kaggle
                print("使用Kaggle官方API下载...")
                
                # 下载数据集
                kaggle.api.dataset_download_files(
                    kaggle_config['dataset_name'],
                    path=cache_dir,
                    unzip=True
                )
                
                # 查找下载的CSV文件
                csv_files = list(Path(cache_dir).glob("*.csv"))
                if not csv_files:
                    print("未找到CSV数据文件")
                    return None
                
                # 读取第一个CSV文件
                csv_file = csv_files[0]
                print(f"读取数据文件: {csv_file}")
                
            except ImportError:
                print("未安装kaggle包，尝试直接下载...")
                return self._download_kaggle_direct(cache_dir, kaggle_config)
                
        except Exception as e:
            print(f"Kaggle API下载失败: {str(e)}")
            print("尝试直接下载...")
            return self._download_kaggle_direct(cache_dir, kaggle_config)
        
        # 读取并处理CSV数据
        try:
            df = pd.read_csv(csv_file)
            
            # 标准化列名
            if kaggle_config['text_column'] in df.columns and kaggle_config['label_column'] in df.columns:
                df = df.rename(columns={
                    kaggle_config['text_column']: 'text',
                    kaggle_config['label_column']: 'label'
                })
            else:
                print(f"未找到期望的列: {kaggle_config['text_column']}, {kaggle_config['label_column']}")
                return None
            
            # 处理标签编码
            if self.language == "chinese":
                # 中文数据集：假设positive=1, negative=0
                df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
            else:
                # 英文数据集：positive=1, negative=0
                df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
            
            # 过滤无效数据
            df = df.dropna(subset=['text', 'label'])
            
            # 转换为Dataset格式
            dataset = Dataset.from_pandas(df[['text', 'label']], preserve_index=False)
            
            print(f"Kaggle数据集处理完成，共 {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            print(f"处理Kaggle数据集失败: {str(e)}")
            return None
    
    def _download_kaggle_direct(self, cache_dir: str, kaggle_config: Dict) -> Optional[Dataset]:
        """
        直接下载Kaggle数据集（不使用API）
        参数：
            cache_dir: 缓存目录
            kaggle_config: Kaggle配置信息
        返回值：数据集对象或None
        """
        try:
            # 使用公开的备用数据源
            fallback_urls = {
                "chinese": "https://raw.githubusercontent.com/SophonPlus/ChineseNlpCorpus/master/datasets/ChnSentiCorp_htl_all/ChnSentiCorp_htl_all.csv",
                "english": "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
            }
            
            url = fallback_urls.get(self.language)
            if not url:
                print(f"无可用的备用数据源")
                return None
            
            print(f"从备用源下载数据: {url}")
            
            if self.language == "chinese":
                # 直接下载CSV文件
                response = requests.get(url, timeout=300)
                response.raise_for_status()
                
                csv_path = Path(cache_dir) / "chinese_sentiment.csv"
                with open(csv_path, 'wb') as f:
                    f.write(response.content)
                
                # 读取CSV数据
                df = pd.read_csv(csv_path, encoding='utf-8')
                
                # 假设列名为 'review' 和 'label'
                if 'review' in df.columns and 'label' in df.columns:
                    df = df.rename(columns={'review': 'text'})
                elif len(df.columns) >= 2:
                    # 使用前两列作为文本和标签
                    df.columns = ['text', 'label'] + list(df.columns[2:])
                
                # 过滤和清理数据
                df = df.dropna(subset=['text', 'label'])
                df['label'] = df['label'].astype(int)
                
                dataset = Dataset.from_pandas(df[['text', 'label']], preserve_index=False)
                
            else:
                # 英文数据集需要解压和处理
                print("英文备用数据源下载较复杂，建议手动下载或使用Kaggle API")
                return None
            
            print(f"备用数据源下载完成，共 {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            print(f"备用数据源下载失败: {str(e)}")
            return None
    
    def download_dataset(self, cache_dir: str = None) -> Dataset:
        """
        下载数据集（支持多数据源回退）
        参数：
            cache_dir: 缓存目录路径，默认使用项目data目录
        返回值：下载的数据集对象
        使用场景：首次下载或更新数据集
        """
        if cache_dir is None:
            cache_dir = str(Config.DATASETS_DIR)
        
        # 首先尝试从Hugging Face下载
        dataset = self.download_from_huggingface(cache_dir)
        
        if dataset is not None:
            return dataset
        
        print("Hugging Face下载失败，尝试使用Kaggle备用数据源...")
        
        # 如果Hugging Face失败，尝试从Kaggle下载
        dataset = self.download_from_kaggle(cache_dir)
        
        if dataset is not None:
            return dataset
        
        # 如果都失败了，抛出异常
        raise Exception(f"无法从任何数据源下载 {self.language} 数据集。请检查网络连接或手动下载数据集。")
    
    def preprocess_dataset(self, dataset: Dataset, max_samples: int = None) -> Dataset:
        """
        预处理数据集文本
        参数：
            dataset: 原始数据集
            max_samples: 最大样本数量，用于快速测试
        返回值：预处理后的数据集
        使用场景：清洗和标准化数据集文本
        """
        print("正在预处理数据集...")
        
        # 限制样本数量（用于快速测试）
        if max_samples and len(dataset) > max_samples:
            dataset = dataset.select(range(max_samples))
            print(f"限制样本数量为: {max_samples}")
        
        def preprocess_function(examples):
            """
            预处理函数，应用于数据集的每个批次
            """
            # 处理文本字段名称差异
            if 'text' in examples:
                texts = examples['text']
            elif 'review' in examples:
                texts = examples['review']
            else:
                # 查找第一个字符串类型的字段作为文本
                for key, value in examples.items():
                    if isinstance(value[0], str) and key != 'label':
                        texts = value
                        break
                else:
                    raise ValueError("未找到文本字段")
            
            # 预处理文本
            processed_texts = []
            for text in texts:
                if text:  # 确保文本不为空
                    processed_text = self.text_processor.clean_text(text)
                    processed_texts.append(processed_text)
                else:
                    processed_texts.append("")
            
            return {
                'text': processed_texts,
                'label': examples['label']
            }
        
        # 应用预处理函数
        processed_dataset = dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=[col for col in dataset.column_names if col not in ['text', 'label']]
        )
        
        # 过滤空文本
        processed_dataset = processed_dataset.filter(lambda x: len(x['text'].strip()) > 0)
        
        print(f"预处理完成，剩余 {len(processed_dataset)} 条有效记录")
        return processed_dataset
    
    def split_dataset(self, dataset: Dataset, test_size: float = 0.2, val_size: float = 0.1) -> Tuple[Dataset, Dataset, Dataset]:
        """
        划分数据集为训练集、验证集和测试集
        参数：
            dataset: 预处理后的数据集
            test_size: 测试集比例
            val_size: 验证集比例（相对于训练集）
        返回值：(训练集, 验证集, 测试集)
        使用场景：为模型训练准备数据划分
        """
        print(f"正在划分数据集，测试集比例: {test_size}, 验证集比例: {val_size}")
        
        # 转换为pandas DataFrame便于操作
        df = dataset.to_pandas()
        
        # 首先分离出测试集
        train_val_df, test_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=42, 
            stratify=df['label']  # 保持标签分布
        )
        
        # 再从训练集中分离出验证集
        train_df, val_df = train_test_split(
            train_val_df, 
            test_size=val_size, 
            random_state=42, 
            stratify=train_val_df['label']
        )
        
        # 转换回Dataset格式
        train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
        val_dataset = Dataset.from_pandas(val_df, preserve_index=False)
        test_dataset = Dataset.from_pandas(test_df, preserve_index=False)
        
        print(f"数据集划分完成:")
        print(f"  训练集: {len(train_dataset)} 条")
        print(f"  验证集: {len(val_dataset)} 条") 
        print(f"  测试集: {len(test_dataset)} 条")
        
        return train_dataset, val_dataset, test_dataset
    
    def get_processed_data(self, max_samples: int = None) -> Tuple[Dataset, Dataset, Dataset]:
        """
        获取完整的预处理数据
        参数：
            max_samples: 最大样本数量，用于快速测试
        返回值：(训练集, 验证集, 测试集)
        使用场景：一键获取训练就绪的数据集
        """
        # 下载数据集
        raw_dataset = self.download_dataset()
        
        # 预处理数据集
        processed_dataset = self.preprocess_dataset(raw_dataset, max_samples)
        
        # 划分数据集
        train_data, val_data, test_data = self.split_dataset(processed_dataset)
        
        return train_data, val_data, test_data
    
    def check_dataset_exists(self, cache_dir: str = None) -> bool:
        """
        检查数据集是否已经下载并且完整
        参数：
            cache_dir: 缓存目录路径，默认使用项目data目录
        返回值：数据集是否存在且完整
        """
        if cache_dir is None:
            cache_dir = str(Config.DATASETS_DIR)
        
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            return False
        
        # 检查Hugging Face缓存是否存在且完整
        if self.language == "chinese":
            # 中文数据集：检查是否有 seamew 相关文件夹和数据文件
            seamew_dirs = list(cache_path.glob("**/seamew*")) + list(cache_path.glob("**/ChnSentiCorp*"))
            for seamew_dir in seamew_dirs:
                # 检查是否有实际的数据文件
                data_files = list(seamew_dir.rglob("*.arrow")) + list(seamew_dir.rglob("*.parquet")) + list(seamew_dir.rglob("dataset_info.json"))
                if len(data_files) > 0:
                    # 有数据文件存在，认为数据集完整
                    return True
        elif self.language == "english":
            # 英文数据集：检查是否有 imdb 相关文件夹和数据文件
            imdb_dirs = list(cache_path.glob("**/imdb*")) + list(cache_path.glob("**/IMDb*"))
            for imdb_dir in imdb_dirs:
                # 检查是否有实际的数据文件
                data_files = list(imdb_dir.rglob("*.arrow")) + list(imdb_dir.rglob("*.parquet")) + list(imdb_dir.rglob("dataset_info.json"))
                if len(data_files) > 0:
                    # 有数据文件存在，认为数据集完整
                    return True
        
        # 检查Kaggle CSV文件是否存在
        kaggle_config = self.kaggle_sources.get(self.language)
        if kaggle_config:
            csv_files = list(cache_path.glob(f"**/{kaggle_config['file_name']}"))
            if not csv_files:
                csv_files = list(cache_path.glob("**/*.csv"))
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    if len(df) > 0 and kaggle_config['text_column'] in df.columns and kaggle_config['label_column'] in df.columns:
                        return True
                except:
                    continue
        
        # 检查TSV文件是否存在（特别是ChnSentiCorp格式）
        tsv_files = list(cache_path.glob("**/*.tsv"))
        for tsv_file in tsv_files:
            try:
                df = pd.read_csv(tsv_file, sep='\t')
                # 检查ChnSentiCorp格式
                if 'label' in df.columns and 'text_a' in df.columns and len(df) > 0:
                    return True
                # 检查其他TSV格式
                elif kaggle_config and len(df) > 0 and kaggle_config['text_column'] in df.columns and kaggle_config['label_column'] in df.columns:
                    return True
            except:
                continue
        
        return False
    
    def load_existing_dataset(self, cache_dir: str = None) -> Optional[Dataset]:
        """
        加载已存在的数据集
        参数：
            cache_dir: 缓存目录路径，默认使用项目data目录
        返回值：加载的数据集对象或None
        """
        if cache_dir is None:
            cache_dir = str(Config.DATASETS_DIR)
        
        print(f"正在加载已存在的 {self.language} 数据集...")
        
        # 首先尝试从Hugging Face缓存加载
        try:
            dataset = load_dataset(self.dataset_name, cache_dir=cache_dir, trust_remote_code=True)
            
            if self.language == "chinese":
                if 'train' in dataset:
                    dataset = dataset['train']
                else:
                    dataset = dataset[list(dataset.keys())[0]]
            else:
                # 英文数据集
                train_data = dataset['train']
                test_data = dataset['test']
                
                combined_texts = train_data['text'] + test_data['text']
                combined_labels = train_data['label'] + test_data['label']
                
                dataset = Dataset.from_dict({
                    'text': combined_texts,
                    'label': combined_labels
                })
            
            # 验证数据集是否有效
            if dataset is not None and len(dataset) > 0:
                print(f"从Hugging Face缓存加载数据集成功，共 {len(dataset)} 条记录")
                return dataset
            else:
                print("Hugging Face缓存数据集为空，尝试其他方式")
                
        except Exception as e:
            print(f"从Hugging Face缓存加载失败: {str(e)}")
        
        # 尝试从Kaggle CSV文件加载
        cache_path = Path(cache_dir)
        kaggle_config = self.kaggle_sources.get(self.language)
        
        if kaggle_config:
            print("尝试从本地CSV文件加载...")
            # 查找CSV文件
            csv_files = list(cache_path.glob(f"**/{kaggle_config['file_name']}"))
            if not csv_files:
                csv_files = list(cache_path.glob("**/*.csv"))
            
            for csv_file in csv_files:
                try:
                    print(f"尝试读取CSV文件: {csv_file}")
                    df = pd.read_csv(csv_file)
                    
                    # 检查列名是否匹配
                    if kaggle_config['text_column'] in df.columns and kaggle_config['label_column'] in df.columns:
                        print(f"找到匹配的CSV文件，包含 {len(df)} 条记录")
                        
                        # 标准化列名
                        df = df.rename(columns={
                            kaggle_config['text_column']: 'text',
                            kaggle_config['label_column']: 'label'
                        })
                        
                        # 处理标签编码
                        if self.language == "chinese":
                            df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
                        else:
                            df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
                        
                        # 过滤无效数据
                        df = df.dropna(subset=['text', 'label'])
                        
                        if len(df) > 0:
                            # 转换为Dataset格式
                            dataset = Dataset.from_pandas(df[['text', 'label']], preserve_index=False)
                            
                            print(f"从CSV文件加载数据集成功，共 {len(dataset)} 条记录")
                            return dataset
                        else:
                            print("CSV文件数据为空")
                            
                except Exception as csv_error:
                    print(f"读取CSV文件 {csv_file} 失败: {str(csv_error)}")
                    continue
        
        # 尝试从TSV文件加载（特别是ChnSentiCorp格式）
        print("尝试从TSV文件加载...")
        tsv_files = list(cache_path.glob("**/*.tsv"))
        
        for tsv_file in tsv_files:
            try:
                print(f"尝试读取TSV文件: {tsv_file}")
                df = pd.read_csv(tsv_file, sep='\t')
                
                # 检查是否是ChnSentiCorp格式 (label, text_a)
                if 'label' in df.columns and 'text_a' in df.columns:
                    print(f"找到ChnSentiCorp格式TSV文件，包含 {len(df)} 条记录")
                    
                    # 标准化列名
                    df = df.rename(columns={'text_a': 'text'})
                    
                    # 过滤无效数据
                    df = df.dropna(subset=['text', 'label'])
                    
                    # 确保标签是整数类型
                    df['label'] = df['label'].astype(int)
                    
                    if len(df) > 0:
                        # 转换为Dataset格式
                        dataset = Dataset.from_pandas(df[['text', 'label']], preserve_index=False)
                        
                        print(f"从TSV文件加载数据集成功，共 {len(dataset)} 条记录")
                        return dataset
                    else:
                        print("TSV文件数据为空")
                
                # 检查其他可能的TSV格式
                elif kaggle_config and kaggle_config['text_column'] in df.columns and kaggle_config['label_column'] in df.columns:
                    print(f"找到匹配的TSV文件，包含 {len(df)} 条记录")
                    
                    # 标准化列名
                    df = df.rename(columns={
                        kaggle_config['text_column']: 'text',
                        kaggle_config['label_column']: 'label'
                    })
                    
                    # 处理标签编码
                    if self.language == "chinese":
                        df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
                    else:
                        df['label'] = df['label'].map({'positive': 1, 'negative': 0, 1: 1, 0: 0})
                    
                    # 过滤无效数据
                    df = df.dropna(subset=['text', 'label'])
                    
                    if len(df) > 0:
                        # 转换为Dataset格式
                        dataset = Dataset.from_pandas(df[['text', 'label']], preserve_index=False)
                        
                        print(f"从TSV文件加载数据集成功，共 {len(dataset)} 条记录")
                        return dataset
                    else:
                        print("TSV文件数据为空")
                        
            except Exception as tsv_error:
                print(f"读取TSV文件 {tsv_file} 失败: {str(tsv_error)}")
                continue
        
        print("所有加载方式都失败了")
        return None
    
    def get_or_download_data(self, max_samples: int = None) -> Tuple[Dataset, Dataset, Dataset]:
        """
        智能获取数据：优先加载已存在的数据集，不存在时才下载
        参数：
            max_samples: 最大样本数量，用于快速测试
        返回值：(训练集, 验证集, 测试集)
        使用场景：训练时优先使用已下载的数据，避免重复下载
        """
        # 检查数据集是否已存在
        if self.check_dataset_exists():
            print(f"检测到已存在的 {self.language} 数据集，直接加载...")
            
            # 尝试加载已存在的数据集
            raw_dataset = self.load_existing_dataset()
            
            if raw_dataset is not None:
                # 预处理数据集
                processed_dataset = self.preprocess_dataset(raw_dataset, max_samples)
                
                # 划分数据集
                train_data, val_data, test_data = self.split_dataset(processed_dataset)
                
                return train_data, val_data, test_data
        
        # 如果数据集不存在或加载失败，则下载新数据集
        print(f"未找到已存在的数据集，开始下载...")
        return self.get_processed_data(max_samples) 