import nltk
import networkx as nx
import json
import os
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from src.models.seo_data import db, Website, Page, Keyword, Link, TechnicalSEO

class TextAnalyzer:
    """
    저장된 SEO 데이터에서 텍스트 분석을 수행하는 클래스
    """
    
    def __init__(self, db_instance):
        """
        텍스트 분석기 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        self._ensure_nltk_data()
        
    def _ensure_nltk_data(self):
        """NLTK 데이터 다운로드 확인"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def analyze_website(self, website_id):
        """
        웹사이트의 모든 페이지에 대한 텍스트 분석 수행
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 분석 결과 요약
        """
        website = Website.query.get(website_id)
        if not website:
            raise ValueError(f"ID가 {website_id}인 웹사이트를 찾을 수 없습니다.")
            
        pages = Page.query.filter_by(website_id=website_id).all()
        
        results = {
            'website_url': website.url,
            'pages_analyzed': len(pages),
            'global_keywords': self.analyze_global_keywords(website_id),
            'knowledge_graph': self.build_global_knowledge_graph(website_id),
            'page_analyses': []
        }
        
        for page in pages:
            page_result = self.analyze_page(page.id)
            results['page_analyses'].append(page_result)
            
        return results
    
    def analyze_page(self, page_id):
        """
        단일 페이지에 대한 텍스트 분석 수행
        
        Args:
            page_id (int): 페이지 ID
            
        Returns:
            dict: 페이지 분석 결과
        """
        page = Page.query.get(page_id)
        if not page:
            raise ValueError(f"ID가 {page_id}인 페이지를 찾을 수 없습니다.")
            
        # 기존 키워드 분석 결과 가져오기
        keywords = Keyword.query.filter_by(page_id=page_id).all()
        
        # 키워드가 없으면 새로 분석
        if not keywords:
            keywords = self._analyze_keywords(page.content, page_id)
            
        # 지식 그래프 구축
        knowledge_graph = self._build_knowledge_graph([kw.keyword for kw in keywords[:15]])
        
        # 결과 반환
        return {
            'page_id': page.id,
            'url': page.url,
            'title': page.title,
            'keywords': [{'keyword': kw.keyword, 'count': kw.count, 'density': kw.density} for kw in keywords],
            'knowledge_graph': knowledge_graph,
            'word_count': len(page.content.split()) if page.content else 0,
            'readability': self._calculate_readability(page.content)
        }
    
    def analyze_global_keywords(self, website_id):
        """
        웹사이트 전체의 글로벌 키워드 분석
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            list: 글로벌 키워드 목록
        """
        # 모든 페이지의 키워드 가져오기
        all_keywords = db.session.query(Keyword.keyword, db.func.sum(Keyword.count).label('total_count')) \
                        .join(Page) \
                        .filter(Page.website_id == website_id) \
                        .group_by(Keyword.keyword) \
                        .order_by(db.desc('total_count')) \
                        .limit(50) \
                        .all()
                        
        # 총 단어 수 계산
        total_words = db.session.query(db.func.sum(Keyword.count)).join(Page).filter(Page.website_id == website_id).scalar() or 0
        
        # 글로벌 키워드 밀도 계산
        global_keywords = []
        for keyword, count in all_keywords:
            density = (count / total_words) * 100 if total_words > 0 else 0
            global_keywords.append({
                'keyword': keyword,
                'count': count,
                'density': round(density, 2)
            })
            
        return global_keywords
    
    def build_global_knowledge_graph(self, website_id, max_keywords=30):
        """
        웹사이트 전체의 글로벌 지식 그래프 구축
        
        Args:
            website_id (int): 웹사이트 ID
            max_keywords (int): 최대 키워드 수
            
        Returns:
            dict: 지식 그래프 데이터
        """
        # 상위 키워드 가져오기
        top_keywords = [kw['keyword'] for kw in self.analyze_global_keywords(website_id)[:max_keywords]]
        
        # 지식 그래프 구축
        return self._build_knowledge_graph(top_keywords)
    
    def _analyze_keywords(self, text, page_id=None, lang='ko'):
        """
        텍스트에서 키워드 추출 및 밀도 계산
        
        Args:
            text (str): 분석할 텍스트
            page_id (int, optional): 페이지 ID
            lang (str): 언어 코드
            
        Returns:
            list: Keyword 객체 목록
        """
        if not text:
            return []
            
        # 언어에 따른 불용어 설정
        try:
            stop_words = set(stopwords.words('korean' if lang == 'ko' else 'english'))
        except:
            stop_words = set()
            
        # 토큰화
        tokens = word_tokenize(text.lower())
        
        # 불용어 및 특수문자 제거
        words = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 1]
        
        # 단어 빈도수 계산
        word_count = Counter(words)
        total_words = len(words)
        
        # 키워드 및 밀도 계산
        keywords = []
        for word, count in word_count.most_common(30):  # 상위 30개 키워드
            density = count / total_words if total_words > 0 else 0
            
            if page_id:
                # 데이터베이스에 저장
                keyword = Keyword(
                    page_id=page_id,
                    keyword=word,
                    count=count,
                    density=round(density * 100, 2)  # 백분율로 변환
                )
                keywords.append(keyword)
                
                if len(keywords) % 10 == 0:
                    self.db.session.add_all(keywords[-10:])
                    self.db.session.commit()
            else:
                # 임시 객체 생성
                keyword = Keyword(
                    page_id=0,
                    keyword=word,
                    count=count,
                    density=round(density * 100, 2)
                )
                keywords.append(keyword)
                
        # 남은 키워드 저장
        if page_id and keywords and len(keywords) % 10 != 0:
            self.db.session.add_all(keywords[-(len(keywords) % 10):])
            self.db.session.commit()
            
        return keywords
    
    def _build_knowledge_graph(self, keywords, threshold=0.5):
        """
        키워드 간의 관계를 나타내는 지식 그래프 구축
        
        Args:
            keywords (list): 키워드 목록
            threshold (float): 관계 임계값
            
        Returns:
            dict: 지식 그래프 데이터
        """
        G = nx.Graph()
        
        # 노드 추가
        for keyword in keywords:
            G.add_node(keyword)
            
        # 엣지 추가 (단순화된 관계 - 동시 출현 기반)
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i+1:]:
                # 여기서는 단순히 모든 키워드 간에 관계를 설정
                # 실제로는 동시 출현 빈도나 의미적 유사성을 계산해야 함
                G.add_edge(kw1, kw2, weight=0.5)
                
        # 그래프를 JSON으로 변환
        graph_data = {
            'nodes': [{'id': node, 'label': node, 'value': G.degree(node)} for node in G.nodes()],
            'edges': [{'source': u, 'target': v, 'weight': G[u][v]['weight']} for u, v in G.edges()]
        }
        
        return graph_data
    
    def _calculate_readability(self, text, lang='ko'):
        """
        텍스트의 가독성 점수 계산
        
        Args:
            text (str): 분석할 텍스트
            lang (str): 언어 코드
            
        Returns:
            dict: 가독성 점수
        """
        if not text:
            return {'score': 0, 'level': '알 수 없음', 'description': '텍스트가 없습니다.'}
            
        # 문장 및 단어 수 계산
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        words = text.split()
        word_count = len(words)
        
        # 평균 문장 길이
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # 한국어의 경우 간단한 가독성 점수 계산
        # (실제로는 더 복잡한 알고리즘 사용 필요)
        if lang == 'ko':
            if avg_sentence_length < 10:
                score = 90
                level = '매우 쉬움'
                description = '짧은 문장으로 구성되어 읽기 매우 쉽습니다.'
            elif avg_sentence_length < 15:
                score = 80
                level = '쉬움'
                description = '적절한 문장 길이로 읽기 쉽습니다.'
            elif avg_sentence_length < 20:
                score = 70
                level = '보통'
                description = '일반적인 문장 길이로 가독성이 보통입니다.'
            elif avg_sentence_length < 25:
                score = 60
                level = '약간 어려움'
                description = '문장이 다소 길어 가독성이 떨어집니다.'
            else:
                score = 50
                level = '어려움'
                description = '문장이 매우 길어 가독성이 낮습니다.'
        else:
            # 영어의 경우 Flesch Reading Ease 점수 계산
            # (간소화된 버전)
            score = 206.835 - (1.015 * avg_sentence_length)
            
            if score > 90:
                level = '매우 쉬움'
                description = '초등학교 저학년 수준의 텍스트입니다.'
            elif score > 80:
                level = '쉬움'
                description = '초등학교 고학년 수준의 텍스트입니다.'
            elif score > 70:
                level = '약간 쉬움'
                description = '중학교 수준의 텍스트입니다.'
            elif score > 60:
                level = '보통'
                description = '고등학교 저학년 수준의 텍스트입니다.'
            elif score > 50:
                level = '약간 어려움'
                description = '고등학교 고학년 수준의 텍스트입니다.'
            elif score > 30:
                level = '어려움'
                description = '대학교 수준의 텍스트입니다.'
            else:
                level = '매우 어려움'
                description = '대학원 수준의 텍스트입니다.'
                
        return {
            'score': round(score, 2),
            'level': level,
            'description': description,
            'stats': {
                'sentence_count': sentence_count,
                'word_count': word_count,
                'avg_sentence_length': round(avg_sentence_length, 2)
            }
        }
    
    def save_analysis_results(self, results, output_dir):
        """
        분석 결과를 JSON 파일로 저장
        
        Args:
            results (dict): 분석 결과
            output_dir (str): 출력 디렉토리
            
        Returns:
            dict: 저장된 파일 경로
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 글로벌 분석 결과 저장
        global_file = os.path.join(output_dir, 'global_analysis.json')
        with open(global_file, 'w', encoding='utf-8') as f:
            json.dump({
                'website_url': results['website_url'],
                'global_keywords': results['global_keywords'],
                'knowledge_graph': results['knowledge_graph']
            }, f, ensure_ascii=False, indent=2)
            
        # 페이지별 분석 결과 저장
        pages_dir = os.path.join(output_dir, 'pages')
        os.makedirs(pages_dir, exist_ok=True)
        
        page_files = []
        for page_analysis in results['page_analyses']:
            page_file = os.path.join(pages_dir, f"page_{page_analysis['page_id']}.json")
            with open(page_file, 'w', encoding='utf-8') as f:
                json.dump(page_analysis, f, ensure_ascii=False, indent=2)
                
            page_files.append(page_file)
            
        return {
            'global_analysis': global_file,
            'page_analyses': page_files
        }
