import os
import json
import sqlite3
from src.models.seo_data import db, Website, Page, Keyword, Link, TechnicalSEO

class SEODataImporter:
    """
    크롤링된 SEO 데이터를 SQLite 데이터베이스에 저장하는 클래스
    """
    
    def __init__(self, db_instance):
        """
        SEO 데이터 임포터 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        
    def import_from_json(self, json_file):
        """
        JSON 파일에서 SEO 데이터를 가져와 데이터베이스에 저장
        
        Args:
            json_file (str): JSON 파일 경로
            
        Returns:
            dict: 가져온 데이터 요약
        """
        try:
            # JSON 파일 읽기
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 웹사이트 정보 저장
            website_url = data['website']['url']
            website = Website.query.filter_by(url=website_url).first()
            
            if not website:
                website = Website(url=website_url)
                self.db.session.add(website)
                self.db.session.commit()
                
            # 기술적 SEO 정보 저장
            tech_data = data['technical_seo']
            tech_seo = TechnicalSEO.query.filter_by(website_id=website.id).first()
            
            if not tech_seo:
                tech_seo = TechnicalSEO(
                    website_id=website.id,
                    has_robots_txt=tech_data['has_robots_txt'],
                    robots_txt_content=tech_data['robots_txt_content'],
                    has_sitemap=tech_data['has_sitemap'],
                    sitemap_url=tech_data['sitemap_url'],
                    sitemap_content=tech_data['sitemap_content'],
                    core_web_vitals=tech_data['core_web_vitals']
                )
                self.db.session.add(tech_seo)
            else:
                tech_seo.has_robots_txt = tech_data['has_robots_txt']
                tech_seo.robots_txt_content = tech_data['robots_txt_content']
                tech_seo.has_sitemap = tech_data['has_sitemap']
                tech_seo.sitemap_url = tech_data['sitemap_url']
                tech_seo.sitemap_content = tech_data['sitemap_content']
                tech_seo.core_web_vitals = tech_data['core_web_vitals']
                
            self.db.session.commit()
            
            # 페이지 정보 저장
            pages_count = 0
            keywords_count = 0
            links_count = 0
            
            for page_data in data['pages']:
                # 이미 존재하는 페이지인지 확인
                page = Page.query.filter_by(website_id=website.id, url=page_data['url']).first()
                
                if not page:
                    page = Page(
                        website_id=website.id,
                        url=page_data['url'],
                        title=page_data['title'],
                        meta_description=page_data['meta_description'],
                        h1=page_data['h1'],
                        content=page_data['content'],
                        status_code=page_data['status_code'],
                        content_type=page_data['content_type'],
                        depth=page_data['depth'],
                        is_homepage=page_data['is_homepage']
                    )
                    self.db.session.add(page)
                else:
                    page.title = page_data['title']
                    page.meta_description = page_data['meta_description']
                    page.h1 = page_data['h1']
                    page.content = page_data['content']
                    page.status_code = page_data['status_code']
                    page.content_type = page_data['content_type']
                    page.depth = page_data['depth']
                    page.is_homepage = page_data['is_homepage']
                    
                self.db.session.commit()
                pages_count += 1
                
                # 기존 키워드 및 링크 삭제 (새로운 데이터로 대체)
                Keyword.query.filter_by(page_id=page.id).delete()
                Link.query.filter_by(page_id=page.id).delete()
                
                # 키워드 정보 저장
                for kw_data in page_data['keywords']:
                    keyword = Keyword(
                        page_id=page.id,
                        keyword=kw_data['keyword'],
                        count=kw_data['count'],
                        density=kw_data['density']
                    )
                    self.db.session.add(keyword)
                    keywords_count += 1
                    
                # 링크 정보 저장
                for link_data in page_data['links']:
                    link = Link(
                        page_id=page.id,
                        url=link_data['url'],
                        text=link_data['text'],
                        is_internal=link_data['is_internal'],
                        is_followed=link_data['is_followed']
                    )
                    self.db.session.add(link)
                    links_count += 1
                    
                # 주기적으로 커밋하여 메모리 사용량 관리
                if pages_count % 10 == 0:
                    self.db.session.commit()
                    
            # 최종 커밋
            self.db.session.commit()
            
            # 지식 그래프 데이터는 별도의 JSON 파일로 저장
            knowledge_graphs_dir = os.path.join(os.path.dirname(json_file), 'knowledge_graphs')
            os.makedirs(knowledge_graphs_dir, exist_ok=True)
            
            for i, page_data in enumerate(data['pages']):
                if 'knowledge_graph' in page_data:
                    graph_file = os.path.join(knowledge_graphs_dir, f'graph_{i}.json')
                    with open(graph_file, 'w', encoding='utf-8') as f:
                        json.dump(page_data['knowledge_graph'], f, ensure_ascii=False, indent=2)
            
            # 결과 요약
            summary = {
                'website': website.url,
                'pages_imported': pages_count,
                'keywords_imported': keywords_count,
                'links_imported': links_count,
                'knowledge_graphs_saved': len(data['pages'])
            }
            
            return summary
            
        except Exception as e:
            # 오류 발생 시 롤백
            self.db.session.rollback()
            raise Exception(f"데이터 가져오기 중 오류 발생: {str(e)}")
            
    def export_to_sqlite(self, output_file):
        """
        SQLAlchemy 데이터베이스를 독립적인 SQLite 파일로 내보내기
        
        Args:
            output_file (str): 출력 SQLite 파일 경로
            
        Returns:
            str: 내보낸 파일 경로
        """
        try:
            # 현재 데이터베이스 URI 가져오기
            db_uri = str(self.db.engine.url)
            
            # 새 SQLite 연결 생성
            conn = sqlite3.connect(output_file)
            
            # 테이블 생성
            conn.execute('''
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TIMESTAMP
            )
            ''')
            
            conn.execute('''
            CREATE TABLE IF NOT EXISTS technical_seo (
                id INTEGER PRIMARY KEY,
                website_id INTEGER NOT NULL,
                has_robots_txt BOOLEAN,
                robots_txt_content TEXT,
                has_sitemap BOOLEAN,
                sitemap_url TEXT,
                sitemap_content TEXT,
                core_web_vitals TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites (id)
            )
            ''')
            
            conn.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                website_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                meta_description TEXT,
                h1 TEXT,
                content TEXT,
                status_code INTEGER,
                content_type TEXT,
                depth INTEGER,
                is_homepage BOOLEAN,
                created_at TIMESTAMP,
                FOREIGN KEY (website_id) REFERENCES websites (id)
            )
            ''')
            
            conn.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY,
                page_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                count INTEGER,
                density REAL,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
            ''')
            
            conn.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY,
                page_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                text TEXT,
                is_internal BOOLEAN,
                is_followed BOOLEAN,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
            ''')
            
            # 데이터 복사
            # 웹사이트
            websites = Website.query.all()
            for website in websites:
                conn.execute(
                    "INSERT INTO websites (id, url, created_at) VALUES (?, ?, ?)",
                    (website.id, website.url, website.created_at)
                )
                
            # 기술적 SEO
            tech_seos = TechnicalSEO.query.all()
            for tech in tech_seos:
                conn.execute(
                    "INSERT INTO technical_seo (id, website_id, has_robots_txt, robots_txt_content, has_sitemap, sitemap_url, sitemap_content, core_web_vitals, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (tech.id, tech.website_id, tech.has_robots_txt, tech.robots_txt_content, tech.has_sitemap, tech.sitemap_url, tech.sitemap_content, tech.core_web_vitals, tech.created_at)
                )
                
            # 페이지
            pages = Page.query.all()
            for page in pages:
                conn.execute(
                    "INSERT INTO pages (id, website_id, url, title, meta_description, h1, content, status_code, content_type, depth, is_homepage, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (page.id, page.website_id, page.url, page.title, page.meta_description, page.h1, page.content, page.status_code, page.content_type, page.depth, page.is_homepage, page.created_at)
                )
                
            # 키워드
            keywords = Keyword.query.all()
            for kw in keywords:
                conn.execute(
                    "INSERT INTO keywords (id, page_id, keyword, count, density) VALUES (?, ?, ?, ?, ?)",
                    (kw.id, kw.page_id, kw.keyword, kw.count, kw.density)
                )
                
            # 링크
            links = Link.query.all()
            for link in links:
                conn.execute(
                    "INSERT INTO links (id, page_id, url, text, is_internal, is_followed) VALUES (?, ?, ?, ?, ?, ?)",
                    (link.id, link.page_id, link.url, link.text, link.is_internal, link.is_followed)
                )
                
            # 변경사항 커밋 및 연결 종료
            conn.commit()
            conn.close()
            
            return output_file
            
        except Exception as e:
            raise Exception(f"SQLite 내보내기 중 오류 발생: {str(e)}")
