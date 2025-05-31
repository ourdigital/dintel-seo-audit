import requests
import json
import re
import urllib.parse
import logging
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from src.models.seo_data import db, Website, Page, TechnicalSEO

class TechnicalSEOChecker:
    """
    웹사이트의 기술적 SEO 요소를 검사하는 클래스
    """
    
    def __init__(self, db_instance):
        """
        기술적 SEO 검사기 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        self.logger = self._setup_logger()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
    def _setup_logger(self):
        """로깅 설정"""
        logger = logging.getLogger('technical_seo_checker')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def check_website(self, website_id):
        """
        웹사이트의 기술적 SEO 요소 검사
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 검사 결과
        """
        website = Website.query.get(website_id)
        if not website:
            raise ValueError(f"ID가 {website_id}인 웹사이트를 찾을 수 없습니다.")
            
        self.logger.info(f"웹사이트 {website.url}의 기술적 SEO 요소 검사 시작")
        
        # 기존 기술적 SEO 정보 가져오기
        tech_seo = TechnicalSEO.query.filter_by(website_id=website_id).first()
        
        # 기술적 SEO 정보가 없으면 새로 생성
        if not tech_seo:
            tech_seo = TechnicalSEO(website_id=website_id)
            self.db.session.add(tech_seo)
            self.db.session.commit()
            
        # 검사 결과 초기화
        results = {
            'website_url': website.url,
            'robots_txt': self._check_robots_txt(website.url, tech_seo),
            'sitemap': self._check_sitemap(website.url, tech_seo),
            'site_structure': self._analyze_site_structure(website_id),
            'core_web_vitals': self._check_core_web_vitals(website.url),
            'redirects': self._check_redirects(website_id),
            'canonical': self._check_canonical_settings(website_id),
            'meta_tags': self._check_meta_tags(website_id),
            'structured_data': self._check_structured_data(website_id),
            'links': self._analyze_links(website_id),
            'mobile_friendly': self._check_mobile_friendly(website.url),
            'security': self._check_security(website.url),
            'page_speed': self._check_page_speed(website.url)
        }
        
        # 기술적 SEO 정보 업데이트
        tech_seo.core_web_vitals = json.dumps(results['core_web_vitals'])
        self.db.session.commit()
        
        self.logger.info(f"웹사이트 {website.url}의 기술적 SEO 요소 검사 완료")
        return results
    
    def _check_robots_txt(self, website_url, tech_seo):
        """
        robots.txt 검사
        
        Args:
            website_url (str): 웹사이트 URL
            tech_seo (TechnicalSEO): 기술적 SEO 정보
            
        Returns:
            dict: robots.txt 검사 결과
        """
        robots_url = urllib.parse.urljoin(website_url, 'robots.txt')
        result = {
            'exists': tech_seo.has_robots_txt,
            'url': robots_url,
            'content': tech_seo.robots_txt_content,
            'issues': [],
            'recommendations': []
        }
        
        if not tech_seo.has_robots_txt:
            result['issues'].append('robots.txt 파일이 없습니다.')
            result['recommendations'].append('웹사이트에 robots.txt 파일을 추가하여 검색 엔진 크롤링을 제어하세요.')
            return result
            
        # robots.txt 내용 분석
        rp = RobotFileParser()
        rp.parse(tech_seo.robots_txt_content.splitlines())
        
        # Sitemap 지시문 확인
        if 'Sitemap:' not in tech_seo.robots_txt_content:
            result['issues'].append('robots.txt에 Sitemap 지시문이 없습니다.')
            result['recommendations'].append('robots.txt에 Sitemap 지시문을 추가하여 검색 엔진이 사이트맵을 찾을 수 있도록 하세요.')
            
        # 중요 페이지 차단 확인
        important_paths = ['/about', '/contact', '/products', '/services', '/blog']
        blocked_paths = []
        
        for path in important_paths:
            full_url = urllib.parse.urljoin(website_url, path)
            if not rp.can_fetch('*', full_url):
                blocked_paths.append(path)
                
        if blocked_paths:
            result['issues'].append(f"다음 중요 경로가 robots.txt에 의해 차단되었습니다: {', '.join(blocked_paths)}")
            result['recommendations'].append('중요한 페이지가 검색 엔진에 의해 색인되도록 robots.txt를 수정하세요.')
            
        return result
    
    def _check_sitemap(self, website_url, tech_seo):
        """
        sitemap.xml 검사
        
        Args:
            website_url (str): 웹사이트 URL
            tech_seo (TechnicalSEO): 기술적 SEO 정보
            
        Returns:
            dict: sitemap.xml 검사 결과
        """
        default_sitemap_url = urllib.parse.urljoin(website_url, 'sitemap.xml')
        sitemap_url = tech_seo.sitemap_url or default_sitemap_url
        
        result = {
            'exists': tech_seo.has_sitemap,
            'url': sitemap_url,
            'content': tech_seo.sitemap_content,
            'urls_count': 0,
            'issues': [],
            'recommendations': []
        }
        
        if not tech_seo.has_sitemap:
            result['issues'].append('sitemap.xml 파일이 없습니다.')
            result['recommendations'].append('웹사이트에 sitemap.xml 파일을 추가하여 검색 엔진 크롤링을 개선하세요.')
            return result
            
        # sitemap.xml 내용 분석
        try:
            soup = BeautifulSoup(tech_seo.sitemap_content, 'xml')
            urls = soup.find_all('url')
            result['urls_count'] = len(urls)
            
            # URL 수 확인
            if result['urls_count'] == 0:
                result['issues'].append('sitemap.xml에 URL이 없습니다.')
                result['recommendations'].append('sitemap.xml에 웹사이트의 모든 중요한 URL을 포함하세요.')
                
            # lastmod 태그 확인
            urls_with_lastmod = soup.find_all('lastmod')
            if len(urls_with_lastmod) < result['urls_count'] * 0.5:  # 50% 미만의 URL에 lastmod 태그가 있는 경우
                result['issues'].append('많은 URL에 lastmod 태그가 없습니다.')
                result['recommendations'].append('모든 URL에 lastmod 태그를 추가하여 검색 엔진이 콘텐츠 업데이트를 인식할 수 있도록 하세요.')
                
        except Exception as e:
            result['issues'].append(f"sitemap.xml 분석 중 오류 발생: {str(e)}")
            result['recommendations'].append('유효한 XML 형식으로 sitemap.xml을 수정하세요.')
            
        return result
    
    def _analyze_site_structure(self, website_id):
        """
        사이트 구조 분석
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 사이트 구조 분석 결과
        """
        # 페이지 깊이 분석
        depth_counts = db.session.query(Page.depth, db.func.count(Page.id)) \
                        .filter(Page.website_id == website_id) \
                        .group_by(Page.depth) \
                        .all()
                        
        max_depth = max([d[0] for d in depth_counts]) if depth_counts else 0
        total_pages = sum([d[1] for d in depth_counts])
        
        depth_distribution = {d[0]: d[1] for d in depth_counts}
        
        result = {
            'total_pages': total_pages,
            'max_depth': max_depth,
            'depth_distribution': depth_distribution,
            'issues': [],
            'recommendations': []
        }
        
        # 깊이 문제 확인
        if max_depth > 4:
            result['issues'].append(f"최대 페이지 깊이({max_depth})가 권장 깊이(3-4)보다 깊습니다.")
            result['recommendations'].append('사이트 구조를 평평하게 만들어 중요한 페이지가 홈페이지에서 3-4번의 클릭 내에 접근 가능하도록 하세요.')
            
        # 깊은 페이지 비율 확인
        deep_pages = sum([depth_distribution.get(d, 0) for d in range(4, max_depth + 1)])
        deep_pages_ratio = deep_pages / total_pages if total_pages > 0 else 0
        
        if deep_pages_ratio > 0.3:  # 30% 이상의 페이지가 깊은 경우
            result['issues'].append(f"전체 페이지의 {round(deep_pages_ratio * 100, 2)}%가 깊은 수준(4 이상)에 있습니다.")
            result['recommendations'].append('내부 링크 구조를 개선하여 깊은 페이지의 접근성을 높이세요.')
            
        return result
    
    def _check_core_web_vitals(self, website_url):
        """
        Core Web Vitals 검사 (실제로는 Lighthouse API 또는 유사한 서비스 사용 필요)
        
        Args:
            website_url (str): 웹사이트 URL
            
        Returns:
            dict: Core Web Vitals 검사 결과
        """
        # 실제 구현에서는 Lighthouse API 또는 유사한 서비스를 사용하여 측정
        # 여기서는 예시 데이터 반환
        result = {
            'LCP': {  # Largest Contentful Paint
                'value': 2.5,  # 초 단위
                'rating': 'good',  # good, needs improvement, poor
                'threshold': {'good': 2.5, 'poor': 4.0}
            },
            'FID': {  # First Input Delay
                'value': 80,  # 밀리초 단위
                'rating': 'needs improvement',
                'threshold': {'good': 100, 'poor': 300}
            },
            'CLS': {  # Cumulative Layout Shift
                'value': 0.15,
                'rating': 'needs improvement',
                'threshold': {'good': 0.1, 'poor': 0.25}
            },
            'issues': [],
            'recommendations': []
        }
        
        # 문제 및 권장사항 추가
        if result['LCP']['rating'] != 'good':
            result['issues'].append(f"LCP({result['LCP']['value']}초)가 좋지 않습니다.")
            result['recommendations'].append('서버 응답 시간 개선, 렌더링 차단 리소스 제거, 이미지 최적화 등을 통해 LCP를 개선하세요.')
            
        if result['FID']['rating'] != 'good':
            result['issues'].append(f"FID({result['FID']['value']}ms)가 좋지 않습니다.")
            result['recommendations'].append('긴 작업 분할, 자바스크립트 실행 최적화, 타사 코드 영향 최소화 등을 통해 FID를 개선하세요.')
            
        if result['CLS']['rating'] != 'good':
            result['issues'].append(f"CLS({result['CLS']['value']})가 좋지 않습니다.")
            result['recommendations'].append('이미지 및 비디오 요소에 크기 속성 지정, 동적 콘텐츠 공간 예약 등을 통해 CLS를 개선하세요.')
            
        return result
    
    def _check_redirects(self, website_id):
        """
        리다이렉트 검사
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 리다이렉트 검사 결과
        """
        # 리다이렉트가 있는 페이지 찾기 (상태 코드 301, 302)
        redirect_pages = Page.query.filter(
            Page.website_id == website_id,
            Page.status_code.in_([301, 302])
        ).all()
        
        result = {
            'redirect_count': len(redirect_pages),
            'redirects': [{'url': page.url, 'status_code': page.status_code} for page in redirect_pages],
            'issues': [],
            'recommendations': []
        }
        
        # 리다이렉트 체인 확인 (실제 구현에서는 더 복잡한 로직 필요)
        if result['redirect_count'] > 10:
            result['issues'].append(f"리다이렉트가 많습니다({result['redirect_count']}개).")
            result['recommendations'].append('불필요한 리다이렉트를 제거하고 직접 링크를 사용하세요.')
            
        return result
    
    def _check_canonical_settings(self, website_id):
        """
        표준 링크(canonical) 설정 검사
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 표준 링크 설정 검사 결과
        """
        pages = Page.query.filter_by(website_id=website_id).all()
        
        canonical_issues = []
        for page in pages:
            # 실제 구현에서는 페이지 콘텐츠에서 canonical 태그 추출 필요
            # 여기서는 예시로 canonical 태그가 없다고 가정
            canonical_issues.append({
                'url': page.url,
                'has_canonical': False,  # 예시 데이터
                'canonical_url': None
            })
            
        pages_without_canonical = [issue for issue in canonical_issues if not issue['has_canonical']]
        
        result = {
            'total_pages': len(pages),
            'pages_with_canonical': len(canonical_issues) - len(pages_without_canonical),
            'pages_without_canonical': len(pages_without_canonical),
            'issues': [],
            'recommendations': []
        }
        
        if result['pages_without_canonical'] > 0:
            result['issues'].append(f"{result['pages_without_canonical']}개 페이지에 canonical 태그가 없습니다.")
            result['recommendations'].append('모든 페이지에 canonical 태그를 추가하여 중복 콘텐츠 문제를 방지하세요.')
            
        return result
    
    def _check_meta_tags(self, website_id):
        """
        SEO 관련 메타 태그 검사
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 메타 태그 검사 결과
        """
        pages = Page.query.filter_by(website_id=website_id).all()
        
        meta_issues = []
        for page in pages:
            # 제목 길이 확인
            title_length = len(page.title) if page.title else 0
            
            # 메타 설명 길이 확인
            meta_desc_length = len(page.meta_description) if page.meta_description else 0
            
            issues = []
            if title_length == 0:
                issues.append('제목 태그 없음')
            elif title_length < 30:
                issues.append('제목이 너무 짧음')
            elif title_length > 60:
                issues.append('제목이 너무 김')
                
            if meta_desc_length == 0:
                issues.append('메타 설명 태그 없음')
            elif meta_desc_length < 70:
                issues.append('메타 설명이 너무 짧음')
            elif meta_desc_length > 160:
                issues.append('메타 설명이 너무 김')
                
            if issues:
                meta_issues.append({
                    'url': page.url,
                    'title_length': title_length,
                    'meta_desc_length': meta_desc_length,
                    'issues': issues
                })
                
        result = {
            'total_pages': len(pages),
            'pages_with_issues': len(meta_issues),
            'issues_detail': meta_issues[:10],  # 처음 10개 이슈만 포함
            'common_issues': [],
            'recommendations': []
        }
        
        # 공통 이슈 분석
        issue_counts = {}
        for page_issue in meta_issues:
            for issue in page_issue['issues']:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
        for issue, count in issue_counts.items():
            percentage = (count / len(pages)) * 100 if len(pages) > 0 else 0
            if percentage > 10:  # 10% 이상의 페이지에 영향을 미치는 이슈
                result['common_issues'].append(f"{issue}: {count}개 페이지({round(percentage, 2)}%)")
                
        # 권장사항 추가
        if '제목 태그 없음' in issue_counts or '제목이 너무 짧음' in issue_counts or '제목이 너무 김' in issue_counts:
            result['recommendations'].append('모든 페이지에 30-60자 길이의 고유하고 설명적인 제목 태그를 추가하세요.')
            
        if '메타 설명 태그 없음' in issue_counts or '메타 설명이 너무 짧음' in issue_counts or '메타 설명이 너무 김' in issue_counts:
            result['recommendations'].append('모든 페이지에 70-160자 길이의 설명적인 메타 설명 태그를 추가하세요.')
            
        return result
    
    def _check_structured_data(self, website_id):
        """
        구조화된 데이터 스키마 검사
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 구조화된 데이터 검사 결과
        """
        pages = Page.query.filter_by(website_id=website_id).all()
        
        # 실제 구현에서는 페이지 콘텐츠에서 구조화된 데이터 추출 필요
        # 여기서는 예시 데이터 반환
        result = {
            'total_pages': len(pages),
            'pages_with_schema': 0,  # 예시 데이터
            'schema_types': {},  # 예시 데이터
            'issues': [],
            'recommendations': []
        }
        
        if result['pages_with_schema'] == 0:
            result['issues'].append('구조화된 데이터(Schema.org)가 없습니다.')
            result['recommendations'].append('주요 페이지에 적절한 Schema.org 마크업을 추가하여 검색 결과에서 리치 스니펫을 활성화하세요.')
            
        return result
    
    def _analyze_links(self, website_id):
        """
        내부 및 외부 링크 분석
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 링크 분석 결과
        """
        # 내부 링크 수
        internal_links_count = db.session.query(db.func.count(Link.id)) \
                                .join(Page) \
                                .filter(Page.website_id == website_id, Link.is_internal == True) \
                                .scalar() or 0
                                
        # 외부 링크 수
        external_links_count = db.session.query(db.func.count(Link.id)) \
                                .join(Page) \
                                .filter(Page.website_id == website_id, Link.is_internal == False) \
                                .scalar() or 0
                                
        # nofollow 링크 수
        nofollow_links_count = db.session.query(db.func.count(Link.id)) \
                                .join(Page) \
                                .filter(Page.website_id == website_id, Link.is_followed == False) \
                                .scalar() or 0
                                
        # 페이지당 평균 내부 링크 수
        pages_count = db.session.query(db.func.count(Page.id)) \
                        .filter(Page.website_id == website_id) \
                        .scalar() or 1  # 0으로 나누기 방지
                        
        avg_internal_links_per_page = internal_links_count / pages_count
        
        result = {
            'internal_links_count': internal_links_count,
            'external_links_count': external_links_count,
            'nofollow_links_count': nofollow_links_count,
            'avg_internal_links_per_page': round(avg_internal_links_per_page, 2),
            'issues': [],
            'recommendations': []
        }
        
        # 내부 링크 문제 확인
        if avg_internal_links_per_page < 5:
            result['issues'].append(f"페이지당 평균 내부 링크 수({avg_internal_links_per_page})가 적습니다.")
            result['recommendations'].append('콘텐츠에 더 많은 내부 링크를 추가하여 사이트 탐색과 SEO를 개선하세요.')
            
        # 외부 링크 비율 확인
        total_links = internal_links_count + external_links_count
        external_links_ratio = external_links_count / total_links if total_links > 0 else 0
        
        if external_links_ratio > 0.5:  # 외부 링크가 50% 이상인 경우
            result['issues'].append(f"외부 링크 비율({round(external_links_ratio * 100, 2)}%)이 높습니다.")
            result['recommendations'].append('외부 링크 비율을 줄이고 내부 링크를 더 많이 사용하여 사이트 권위를 유지하세요.')
            
        return result
    
    def _check_mobile_friendly(self, website_url):
        """
        모바일 친화성 검사 (실제로는 Google Mobile-Friendly Test API 또는 유사한 서비스 사용 필요)
        
        Args:
            website_url (str): 웹사이트 URL
            
        Returns:
            dict: 모바일 친화성 검사 결과
        """
        # 실제 구현에서는 Google Mobile-Friendly Test API 또는 유사한 서비스 사용
        # 여기서는 예시 데이터 반환
        result = {
            'is_mobile_friendly': True,  # 예시 데이터
            'issues': [],
            'recommendations': []
        }
        
        if not result['is_mobile_friendly']:
            result['issues'].append('웹사이트가 모바일 친화적이지 않습니다.')
            result['recommendations'].append('반응형 디자인을 구현하고, 모바일 화면에 맞게 콘텐츠를 최적화하세요.')
            
        return result
    
    def _check_security(self, website_url):
        """
        보안 검사 (HTTPS, HSTS 등)
        
        Args:
            website_url (str): 웹사이트 URL
            
        Returns:
            dict: 보안 검사 결과
        """
        is_https = website_url.startswith('https://')
        
        result = {
            'is_https': is_https,
            'has_hsts': False,  # 예시 데이터
            'issues': [],
            'recommendations': []
        }
        
        if not is_https:
            result['issues'].append('웹사이트가 HTTPS를 사용하지 않습니다.')
            result['recommendations'].append('HTTPS를 구현하여 보안을 강화하고 SEO 순위를 개선하세요.')
            
        if not result['has_hsts']:
            result['issues'].append('HSTS(HTTP Strict Transport Security)가 구현되지 않았습니다.')
            result['recommendations'].append('HSTS를 구현하여 보안을 강화하세요.')
            
        return result
    
    def _check_page_speed(self, website_url):
        """
        페이지 속도 검사 (실제로는 Google PageSpeed Insights API 또는 유사한 서비스 사용 필요)
        
        Args:
            website_url (str): 웹사이트 URL
            
        Returns:
            dict: 페이지 속도 검사 결과
        """
        # 실제 구현에서는 Google PageSpeed Insights API 또는 유사한 서비스 사용
        # 여기서는 예시 데이터 반환
        result = {
            'mobile_score': 75,  # 예시 데이터
            'desktop_score': 85,  # 예시 데이터
            'issues': [],
            'recommendations': []
        }
        
        if result['mobile_score'] < 80:
            result['issues'].append(f"모바일 페이지 속도 점수({result['mobile_score']})가 낮습니다.")
            result['recommendations'].append('이미지 최적화, 자바스크립트 및 CSS 최소화, 브라우저 캐싱 활성화 등을 통해 모바일 페이지 속도를 개선하세요.')
            
        if result['desktop_score'] < 90:
            result['issues'].append(f"데스크톱 페이지 속도 점수({result['desktop_score']})가 낮습니다.")
            result['recommendations'].append('서버 응답 시간 개선, 리소스 최적화, 렌더링 차단 리소스 제거 등을 통해 데스크톱 페이지 속도를 개선하세요.')
            
        return result
    
    def save_results(self, results, output_file):
        """
        검사 결과를 JSON 파일로 저장
        
        Args:
            results (dict): 검사 결과
            output_file (str): 출력 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"기술적 SEO 검사 결과가 {output_file}에 저장되었습니다.")
        return output_file
