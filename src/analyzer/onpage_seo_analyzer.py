import json
import os
import re
from src.models.seo_data import db, Website, Page, Keyword, Link

class OnPageSEOAnalyzer:
    """
    선택된 페이지의 온페이지 SEO 요소를 분석하는 클래스
    """
    
    def __init__(self, db_instance):
        """
        온페이지 SEO 분석기 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        
    def analyze_pages(self, page_ids):
        """
        선택된 페이지의 온페이지 SEO 요소 분석
        
        Args:
            page_ids (list): 분석할 페이지 ID 목록
            
        Returns:
            list: 페이지별 분석 결과
        """
        results = []
        
        for page_id in page_ids:
            page_result = self.analyze_page(page_id)
            if page_result:
                results.append(page_result)
                
        return results
    
    def analyze_page(self, page_id):
        """
        단일 페이지의 온페이지 SEO 요소 분석
        
        Args:
            page_id (int): 분석할 페이지 ID
            
        Returns:
            dict: 페이지 분석 결과
        """
        page = Page.query.get(page_id)
        if not page:
            return None
            
        # 키워드 정보 가져오기
        keywords = Keyword.query.filter_by(page_id=page_id).order_by(Keyword.count.desc()).all()
        
        # 링크 정보 가져오기
        links = Link.query.filter_by(page_id=page_id).all()
        internal_links = [link for link in links if link.is_internal]
        external_links = [link for link in links if not link.is_internal]
        
        # 분석 결과 초기화
        result = {
            'page_id': page.id,
            'url': page.url,
            'title': page.title,
            'meta_description': page.meta_description,
            'h1': page.h1,
            'content_length': len(page.content) if page.content else 0,
            'keywords': [{'keyword': kw.keyword, 'count': kw.count, 'density': kw.density} for kw in keywords[:10]],
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'analysis': {
                'title': self._analyze_title(page),
                'meta_description': self._analyze_meta_description(page),
                'url': self._analyze_url(page),
                'headings': self._analyze_headings(page),
                'content': self._analyze_content(page, keywords),
                'images': self._analyze_images(page),
                'links': self._analyze_links(page, internal_links, external_links),
                'mobile_friendly': self._analyze_mobile_friendly(page),
                'social_tags': self._analyze_social_tags(page)
            },
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 종합 점수 계산 및 이슈/권장사항 수집
        score = 0
        issues = []
        recommendations = []
        
        for category, analysis in result['analysis'].items():
            score += analysis['score']
            issues.extend(analysis['issues'])
            recommendations.extend(analysis['recommendations'])
            
        # 최대 점수는 100점
        result['score'] = min(100, score)
        result['issues'] = issues
        result['recommendations'] = recommendations
        
        return result
    
    def _analyze_title(self, page):
        """
        페이지 제목 분석
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 제목 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 제목이 없는 경우
        if not page.title:
            result['issues'].append('페이지에 제목 태그가 없습니다.')
            result['recommendations'].append('페이지에 설명적이고 키워드가 포함된 제목 태그를 추가하세요.')
            return result
            
        # 제목 길이 확인
        title_length = len(page.title)
        
        if title_length < 30:
            result['issues'].append(f'제목이 너무 짧습니다({title_length}자).')
            result['recommendations'].append('제목을 30-60자로 늘려 더 설명적으로 만드세요.')
            result['score'] += 5
        elif title_length > 60:
            result['issues'].append(f'제목이 너무 깁니다({title_length}자).')
            result['recommendations'].append('제목을 60자 이하로 줄여 검색 결과에서 잘리지 않도록 하세요.')
            result['score'] += 5
        else:
            result['score'] += 10
            
        # 키워드 포함 여부 확인
        keywords = Keyword.query.filter_by(page_id=page.id).order_by(Keyword.count.desc()).limit(3).all()
        
        if keywords:
            primary_keyword = keywords[0].keyword
            if primary_keyword.lower() in page.title.lower():
                result['score'] += 5
            else:
                result['issues'].append(f'제목에 주요 키워드("{primary_keyword}")가 포함되어 있지 않습니다.')
                result['recommendations'].append('제목에 주요 키워드를 포함하여 검색 엔진 최적화를 개선하세요.')
                
        return result
    
    def _analyze_meta_description(self, page):
        """
        메타 설명 분석
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 메타 설명 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 메타 설명이 없는 경우
        if not page.meta_description:
            result['issues'].append('페이지에 메타 설명 태그가 없습니다.')
            result['recommendations'].append('페이지에 설명적이고 키워드가 포함된 메타 설명 태그를 추가하세요.')
            return result
            
        # 메타 설명 길이 확인
        desc_length = len(page.meta_description)
        
        if desc_length < 70:
            result['issues'].append(f'메타 설명이 너무 짧습니다({desc_length}자).')
            result['recommendations'].append('메타 설명을 70-160자로 늘려 더 설명적으로 만드세요.')
            result['score'] += 5
        elif desc_length > 160:
            result['issues'].append(f'메타 설명이 너무 깁니다({desc_length}자).')
            result['recommendations'].append('메타 설명을 160자 이하로 줄여 검색 결과에서 잘리지 않도록 하세요.')
            result['score'] += 5
        else:
            result['score'] += 10
            
        # 키워드 포함 여부 확인
        keywords = Keyword.query.filter_by(page_id=page.id).order_by(Keyword.count.desc()).limit(3).all()
        
        if keywords:
            primary_keyword = keywords[0].keyword
            if primary_keyword.lower() in page.meta_description.lower():
                result['score'] += 5
            else:
                result['issues'].append(f'메타 설명에 주요 키워드("{primary_keyword}")가 포함되어 있지 않습니다.')
                result['recommendations'].append('메타 설명에 주요 키워드를 포함하여 검색 엔진 최적화를 개선하세요.')
                
        return result
    
    def _analyze_url(self, page):
        """
        URL 분석
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: URL 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # URL 길이 확인
        url_path = page.url.split('://')[-1].split('/', 1)[-1] if '/' in page.url.split('://')[-1] else ''
        url_length = len(url_path)
        
        if url_length > 100:
            result['issues'].append(f'URL이 너무 깁니다({url_length}자).')
            result['recommendations'].append('URL을 더 짧고 간결하게 만드세요.')
        else:
            result['score'] += 5
            
        # URL에 특수문자 확인
        if re.search(r'[^a-zA-Z0-9/-]', url_path):
            result['issues'].append('URL에 특수문자가 포함되어 있습니다.')
            result['recommendations'].append('URL에서 특수문자를 제거하고 하이픈(-)을 사용하여 단어를 구분하세요.')
        else:
            result['score'] += 5
            
        # URL에 키워드 포함 여부 확인
        keywords = Keyword.query.filter_by(page_id=page.id).order_by(Keyword.count.desc()).limit(3).all()
        
        if keywords:
            primary_keyword = keywords[0].keyword
            if primary_keyword.lower() in url_path.lower():
                result['score'] += 5
            else:
                result['issues'].append(f'URL에 주요 키워드("{primary_keyword}")가 포함되어 있지 않습니다.')
                result['recommendations'].append('URL에 주요 키워드를 포함하여 검색 엔진 최적화를 개선하세요.')
                
        return result
    
    def _analyze_headings(self, page):
        """
        제목 태그(H1, H2, H3 등) 분석
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 제목 태그 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # H1 태그 확인
        if not page.h1:
            result['issues'].append('페이지에 H1 태그가 없습니다.')
            result['recommendations'].append('페이지에 주요 키워드가 포함된 H1 태그를 추가하세요.')
        else:
            result['score'] += 5
            
            # H1 태그 길이 확인
            h1_length = len(page.h1)
            
            if h1_length < 20:
                result['issues'].append(f'H1 태그가 너무 짧습니다({h1_length}자).')
                result['recommendations'].append('H1 태그를 더 설명적으로 만들고 주요 키워드를 포함하세요.')
            elif h1_length > 70:
                result['issues'].append(f'H1 태그가 너무 깁니다({h1_length}자).')
                result['recommendations'].append('H1 태그를 더 간결하게 만들되 주요 키워드는 유지하세요.')
            else:
                result['score'] += 5
                
            # H1 태그에 키워드 포함 여부 확인
            keywords = Keyword.query.filter_by(page_id=page.id).order_by(Keyword.count.desc()).limit(3).all()
            
            if keywords:
                primary_keyword = keywords[0].keyword
                if primary_keyword.lower() in page.h1.lower():
                    result['score'] += 5
                else:
                    result['issues'].append(f'H1 태그에 주요 키워드("{primary_keyword}")가 포함되어 있지 않습니다.')
                    result['recommendations'].append('H1 태그에 주요 키워드를 포함하여 검색 엔진 최적화를 개선하세요.')
                    
        # 콘텐츠에서 H2, H3 태그 확인 (실제 구현에서는 HTML 파싱 필요)
        # 여기서는 예시 데이터 반환
        result['score'] += 5
        
        return result
    
    def _analyze_content(self, page, keywords):
        """
        콘텐츠 분석
        
        Args:
            page (Page): 페이지 객체
            keywords (list): 키워드 객체 목록
            
        Returns:
            dict: 콘텐츠 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 콘텐츠가 없는 경우
        if not page.content:
            result['issues'].append('페이지에 콘텐츠가 없습니다.')
            result['recommendations'].append('페이지에 유용하고 관련성 있는 콘텐츠를 추가하세요.')
            return result
            
        # 콘텐츠 길이 확인
        content_length = len(page.content)
        word_count = len(page.content.split())
        
        if word_count < 300:
            result['issues'].append(f'콘텐츠가 너무 짧습니다({word_count}단어).')
            result['recommendations'].append('콘텐츠를 최소 300단어 이상으로 늘려 더 많은 가치를 제공하세요.')
            result['score'] += 2
        elif word_count < 600:
            result['score'] += 5
        else:
            result['score'] += 10
            
        # 키워드 밀도 확인
        if keywords:
            primary_keyword = keywords[0]
            
            if primary_keyword.density < 0.5:
                result['issues'].append(f'주요 키워드("{primary_keyword.keyword}")의 밀도가 너무 낮습니다({primary_keyword.density}%).')
                result['recommendations'].append('주요 키워드의 밀도를 0.5-2.5% 사이로 유지하세요.')
            elif primary_keyword.density > 2.5:
                result['issues'].append(f'주요 키워드("{primary_keyword.keyword}")의 밀도가 너무 높습니다({primary_keyword.density}%).')
                result['recommendations'].append('키워드 스터핑을 피하고 주요 키워드의 밀도를 0.5-2.5% 사이로 유지하세요.')
            else:
                result['score'] += 5
                
        # 문단 및 문장 구조 확인 (간단한 분석)
        paragraphs = re.split(r'\n\s*\n', page.content)
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        if avg_paragraph_length > 150:
            result['issues'].append(f'문단이 너무 깁니다(평균 {avg_paragraph_length:.1f}단어).')
            result['recommendations'].append('문단을 더 짧게 나누어 가독성을 높이세요.')
        else:
            result['score'] += 5
            
        return result
    
    def _analyze_images(self, page):
        """
        이미지 분석 (실제 구현에서는 HTML 파싱 필요)
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 이미지 분석 결과
        """
        # 실제 구현에서는 HTML 파싱을 통해 이미지 태그 추출 필요
        # 여기서는 예시 데이터 반환
        result = {
            'score': 5,
            'issues': ['이미지 alt 속성이 누락되었습니다.'],
            'recommendations': ['모든 이미지에 설명적인 alt 속성을 추가하세요.']
        }
        
        return result
    
    def _analyze_links(self, page, internal_links, external_links):
        """
        링크 분석
        
        Args:
            page (Page): 페이지 객체
            internal_links (list): 내부 링크 목록
            external_links (list): 외부 링크 목록
            
        Returns:
            dict: 링크 분석 결과
        """
        result = {
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # 내부 링크 수 확인
        internal_links_count = len(internal_links)
        
        if internal_links_count < 3:
            result['issues'].append(f'내부 링크가 너무 적습니다({internal_links_count}개).')
            result['recommendations'].append('페이지에 더 많은 내부 링크를 추가하여 사이트 탐색과 SEO를 개선하세요.')
        else:
            result['score'] += 5
            
        # 외부 링크 수 확인
        external_links_count = len(external_links)
        
        if external_links_count > internal_links_count * 2:
            result['issues'].append(f'외부 링크가 내부 링크보다 훨씬 많습니다(외부: {external_links_count}개, 내부: {internal_links_count}개).')
            result['recommendations'].append('외부 링크 비율을 줄이고 내부 링크를 더 많이 사용하세요.')
        else:
            result['score'] += 5
            
        # 앵커 텍스트 확인
        empty_anchor_count = sum(1 for link in internal_links + external_links if not link.text)
        
        if empty_anchor_count > 0:
            result['issues'].append(f'앵커 텍스트가 없는 링크가 있습니다({empty_anchor_count}개).')
            result['recommendations'].append('모든 링크에 설명적인 앵커 텍스트를 사용하세요.')
        else:
            result['score'] += 5
            
        return result
    
    def _analyze_mobile_friendly(self, page):
        """
        모바일 친화성 분석 (실제 구현에서는 추가 API 필요)
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 모바일 친화성 분석 결과
        """
        # 실제 구현에서는 Google Mobile-Friendly Test API 또는 유사한 서비스 사용 필요
        # 여기서는 예시 데이터 반환
        result = {
            'score': 10,
            'issues': [],
            'recommendations': []
        }
        
        return result
    
    def _analyze_social_tags(self, page):
        """
        소셜 미디어 태그 분석 (실제 구현에서는 HTML 파싱 필요)
        
        Args:
            page (Page): 페이지 객체
            
        Returns:
            dict: 소셜 미디어 태그 분석 결과
        """
        # 실제 구현에서는 HTML 파싱을 통해 Open Graph 및 Twitter Card 태그 추출 필요
        # 여기서는 예시 데이터 반환
        result = {
            'score': 0,
            'issues': ['Open Graph 태그가 없습니다.', 'Twitter Card 태그가 없습니다.'],
            'recommendations': ['소셜 미디어 공유를 최적화하기 위해 Open Graph 및 Twitter Card 태그를 추가하세요.']
        }
        
        return result
    
    def save_analysis_results(self, results, output_file):
        """
        분석 결과를 JSON 파일로 저장
        
        Args:
            results (list): 분석 결과 목록
            output_file (str): 출력 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return output_file
