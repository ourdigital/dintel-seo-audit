import json
import os
from collections import defaultdict
from src.models.seo_data import db, Website, Page, Link

class PageRanker:
    """
    웹사이트의 페이지를 중요도에 따라 순위를 매기는 클래스
    """
    
    def __init__(self, db_instance):
        """
        페이지 랭커 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        
    def rank_pages(self, website_id, top_n=20):
        """
        웹사이트의 페이지를 중요도에 따라 순위를 매기고 상위 N개 페이지 반환
        
        Args:
            website_id (int): 웹사이트 ID
            top_n (int): 반환할 상위 페이지 수
            
        Returns:
            list: 상위 N개 페이지 정보
        """
        # 모든 페이지 가져오기
        pages = Page.query.filter_by(website_id=website_id).all()
        
        if not pages:
            return []
            
        # 페이지 점수 계산
        page_scores = self._calculate_page_scores(website_id)
        
        # 페이지 정보와 점수 결합
        ranked_pages = []
        for page in pages:
            score = page_scores.get(page.id, 0)
            ranked_pages.append({
                'id': page.id,
                'url': page.url,
                'title': page.title,
                'is_homepage': page.is_homepage,
                'depth': page.depth,
                'score': score,
                'inbound_links': page_scores.get(f'inbound_links_{page.id}', 0),
                'outbound_links': page_scores.get(f'outbound_links_{page.id}', 0)
            })
            
        # 점수에 따라 정렬
        ranked_pages.sort(key=lambda x: x['score'], reverse=True)
        
        # 상위 N개 페이지 반환
        return ranked_pages[:top_n]
    
    def _calculate_page_scores(self, website_id):
        """
        페이지 점수 계산
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 페이지 ID를 키로 하고 점수를 값으로 하는 딕셔너리
        """
        # 페이지 정보 가져오기
        pages = Page.query.filter_by(website_id=website_id).all()
        
        # 페이지 ID를 키로 하는 딕셔너리 초기화
        page_scores = {}
        
        # 내부 링크 분석
        inbound_links = defaultdict(int)  # 페이지로 들어오는 링크 수
        outbound_links = defaultdict(int)  # 페이지에서 나가는 링크 수
        
        # 모든 내부 링크 가져오기
        internal_links = db.session.query(Link) \
                        .join(Page, Link.page_id == Page.id) \
                        .filter(Page.website_id == website_id, Link.is_internal == True) \
                        .all()
                        
        # 페이지 URL을 ID로 매핑
        page_url_to_id = {page.url: page.id for page in pages}
        
        # 내부 링크 분석
        for link in internal_links:
            source_page_id = link.page_id
            target_url = link.url
            
            # 대상 페이지 ID 찾기
            target_page_id = None
            for page in pages:
                if target_url == page.url or target_url.rstrip('/') == page.url.rstrip('/'):
                    target_page_id = page.id
                    break
                    
            if target_page_id:
                inbound_links[target_page_id] += 1
                outbound_links[source_page_id] += 1
                
        # 각 페이지의 점수 계산
        for page in pages:
            # 기본 점수 초기화
            score = 0
            
            # 1. 홈페이지 가중치
            if page.is_homepage:
                score += 100
                
            # 2. 깊이 가중치 (낮을수록 높은 점수)
            depth_score = max(0, 10 - page.depth * 2)  # 깊이가 0이면 10점, 1이면 8점, ...
            score += depth_score
            
            # 3. 내부 링크 가중치
            inbound_link_count = inbound_links[page.id]
            inbound_link_score = min(50, inbound_link_count * 2)  # 최대 50점
            score += inbound_link_score
            
            # 4. 제목 및 메타 설명 가중치
            if page.title and len(page.title) > 10:
                score += 5
                
            if page.meta_description and len(page.meta_description) > 50:
                score += 5
                
            # 5. H1 태그 가중치
            if page.h1 and len(page.h1) > 5:
                score += 5
                
            # 6. 콘텐츠 길이 가중치
            if page.content:
                content_length = len(page.content)
                if content_length > 1000:
                    score += 10
                elif content_length > 500:
                    score += 5
                    
            # 점수 저장
            page_scores[page.id] = score
            page_scores[f'inbound_links_{page.id}'] = inbound_links[page.id]
            page_scores[f'outbound_links_{page.id}'] = outbound_links[page.id]
            
        return page_scores
    
    def save_ranked_pages(self, ranked_pages, output_file):
        """
        순위가 매겨진 페이지를 JSON 파일로 저장
        
        Args:
            ranked_pages (list): 순위가 매겨진 페이지 목록
            output_file (str): 출력 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ranked_pages, f, ensure_ascii=False, indent=2)
            
        return output_file
