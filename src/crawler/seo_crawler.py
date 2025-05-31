import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
import time
from collections import Counter
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import networkx as nx

# NLTK 데이터 다운로드
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SEOCrawler:
    def __init__(self, base_url, max_pages=100, max_depth=3):
        """
        SEO 크롤러 초기화
        
        Args:
            base_url (str): 크롤링할 웹사이트의 기본 URL
            max_pages (int): 크롤링할 최대 페이지 수
            max_depth (int): 크롤링할 최대 깊이
        """
        self.base_url = self._normalize_url(base_url)
        self.base_domain = self._get_domain(base_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls = set()
        self.pages_data = []
        self.technical_data = {
            'has_robots_txt': False,
            'robots_txt_content': '',
            'has_sitemap': False,
            'sitemap_url': '',
            'sitemap_content': '',
            'core_web_vitals': json.dumps({
                'LCP': None,  # Largest Contentful Paint
                'FID': None,  # First Input Delay
                'CLS': None,  # Cumulative Layout Shift
            })
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """로깅 설정"""
        logger = logging.getLogger('seo_crawler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _normalize_url(self, url):
        """URL 정규화"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # 후행 슬래시 추가
        if not url.endswith('/'):
            url = url + '/'
            
        return url
    
    def _get_domain(self, url):
        """URL에서 도메인 추출"""
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc
    
    def _is_internal_url(self, url):
        """내부 URL인지 확인"""
        if not url.startswith(('http://', 'https://')):
            return True
            
        return self.base_domain in url
    
    def _clean_url(self, url, base_url=None):
        """URL 정리 및 정규화"""
        if not url:
            return None
            
        # 프래그먼트 제거
        url = url.split('#')[0]
        
        # 쿼리 파라미터 제거 (선택적)
        # url = url.split('?')[0]
        
        # 상대 URL 처리
        if not url.startswith(('http://', 'https://')):
            if base_url:
                url = urllib.parse.urljoin(base_url, url)
            else:
                url = urllib.parse.urljoin(self.base_url, url)
                
        return url
    
    def _extract_text_content(self, soup):
        """페이지에서 텍스트 콘텐츠 추출"""
        # 불필요한 요소 제거
        for script in soup(['script', 'style', 'meta', 'noscript']):
            script.extract()
            
        # 텍스트 추출 및 정리
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_keywords(self, text, lang='ko'):
        """텍스트에서 키워드 추출 및 밀도 계산"""
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
            keywords.append({
                'keyword': word,
                'count': count,
                'density': round(density * 100, 2)  # 백분율로 변환
            })
            
        return keywords
    
    def _build_knowledge_graph(self, keywords, threshold=0.5):
        """키워드 간의 관계를 나타내는 지식 그래프 구축"""
        G = nx.Graph()
        
        # 상위 키워드만 사용
        top_keywords = [k['keyword'] for k in keywords[:15]]
        
        # 노드 추가
        for keyword in top_keywords:
            G.add_node(keyword)
            
        # 엣지 추가 (단순화된 관계 - 동시 출현 기반)
        for i, kw1 in enumerate(top_keywords):
            for kw2 in top_keywords[i+1:]:
                # 여기서는 단순히 모든 키워드 간에 관계를 설정
                # 실제로는 동시 출현 빈도나 의미적 유사성을 계산해야 함
                G.add_edge(kw1, kw2, weight=0.5)
                
        # 그래프를 JSON으로 변환
        graph_data = {
            'nodes': [{'id': node, 'label': node, 'value': G.degree(node)} for node in G.nodes()],
            'edges': [{'source': u, 'target': v, 'weight': G[u][v]['weight']} for u, v in G.edges()]
        }
        
        return graph_data
    
    def _extract_links(self, soup, current_url):
        """페이지에서 링크 추출"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            
            # URL 정리
            url = self._clean_url(href, current_url)
            if not url:
                continue
                
            # 내부/외부 링크 구분
            is_internal = self._is_internal_url(url)
            
            # nofollow 속성 확인
            is_followed = 'nofollow' not in a_tag.get('rel', [])
            
            links.append({
                'url': url,
                'text': text,
                'is_internal': is_internal,
                'is_followed': is_followed
            })
            
        return links
    
    def _check_robots_txt(self):
        """robots.txt 확인"""
        robots_url = urllib.parse.urljoin(self.base_url, 'robots.txt')
        try:
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.technical_data['has_robots_txt'] = True
                self.technical_data['robots_txt_content'] = response.text
                
                # sitemap.xml 확인
                sitemap_matches = re.findall(r'Sitemap:\s*(.*)', response.text, re.IGNORECASE)
                if sitemap_matches:
                    self.technical_data['has_sitemap'] = True
                    self.technical_data['sitemap_url'] = sitemap_matches[0].strip()
                    self._check_sitemap(self.technical_data['sitemap_url'])
                else:
                    # 기본 위치에서 sitemap 확인
                    self._check_sitemap(urllib.parse.urljoin(self.base_url, 'sitemap.xml'))
        except Exception as e:
            self.logger.error(f"robots.txt 확인 중 오류 발생: {e}")
            # 기본 위치에서 sitemap 확인
            self._check_sitemap(urllib.parse.urljoin(self.base_url, 'sitemap.xml'))
    
    def _check_sitemap(self, sitemap_url):
        """sitemap.xml 확인"""
        try:
            response = requests.get(sitemap_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.technical_data['has_sitemap'] = True
                self.technical_data['sitemap_url'] = sitemap_url
                self.technical_data['sitemap_content'] = response.text
        except Exception as e:
            self.logger.error(f"sitemap.xml 확인 중 오류 발생: {e}")
    
    def crawl(self):
        """웹사이트 크롤링 시작"""
        self.logger.info(f"크롤링 시작: {self.base_url}")
        
        # robots.txt 및 sitemap.xml 확인
        self._check_robots_txt()
        
        # 홈페이지부터 크롤링 시작
        self._crawl_page(self.base_url, depth=0, is_homepage=True)
        
        # 결과 반환
        result = {
            'website': {
                'url': self.base_url,
                'domain': self.base_domain
            },
            'technical_seo': self.technical_data,
            'pages': self.pages_data
        }
        
        self.logger.info(f"크롤링 완료: {len(self.pages_data)} 페이지")
        return result
    
    def _crawl_page(self, url, depth=0, is_homepage=False):
        """개별 페이지 크롤링"""
        # 최대 깊이 또는 최대 페이지 수 확인
        if depth > self.max_depth or len(self.pages_data) >= self.max_pages:
            return
            
        # URL 정규화
        url = self._clean_url(url)
        if not url or url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        self.logger.info(f"페이지 크롤링 중: {url} (깊이: {depth})")
        
        try:
            # 페이지 요청
            response = requests.get(url, headers=self.headers, timeout=10)
            status_code = response.status_code
            content_type = response.headers.get('Content-Type', '')
            
            # HTML 페이지만 처리
            if status_code != 200 or 'text/html' not in content_type.lower():
                self.logger.warning(f"HTML이 아닌 페이지 건너뜀: {url} (상태 코드: {status_code}, 콘텐츠 타입: {content_type})")
                return
                
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 메타데이터 추출
            title = soup.title.string.strip() if soup.title else ''
            meta_description = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and 'content' in meta_tag.attrs:
                meta_description = meta_tag['content'].strip()
                
            # H1 태그 추출
            h1_tag = soup.find('h1')
            h1_text = h1_tag.get_text(strip=True) if h1_tag else ''
            
            # 텍스트 콘텐츠 추출
            content = self._extract_text_content(soup)
            
            # 키워드 추출
            keywords = self._extract_keywords(content)
            
            # 지식 그래프 구축
            knowledge_graph = self._build_knowledge_graph(keywords)
            
            # 링크 추출
            links = self._extract_links(soup, url)
            
            # 페이지 데이터 저장
            page_data = {
                'url': url,
                'title': title,
                'meta_description': meta_description,
                'h1': h1_text,
                'content': content,
                'status_code': status_code,
                'content_type': content_type,
                'depth': depth,
                'is_homepage': is_homepage,
                'keywords': keywords,
                'knowledge_graph': knowledge_graph,
                'links': links
            }
            
            self.pages_data.append(page_data)
            
            # 내부 링크 재귀적 크롤링
            if depth < self.max_depth:
                for link in links:
                    if link['is_internal'] and link['is_followed']:
                        # 크롤링 간격 조절 (서버 부하 방지)
                        time.sleep(1)
                        self._crawl_page(link['url'], depth + 1)
                        
        except Exception as e:
            self.logger.error(f"페이지 크롤링 중 오류 발생: {url}, {str(e)}")
    
    def save_to_json(self, filename):
        """크롤링 결과를 JSON 파일로 저장"""
        result = {
            'website': {
                'url': self.base_url,
                'domain': self.base_domain
            },
            'technical_seo': self.technical_data,
            'pages': self.pages_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"크롤링 결과가 {filename}에 저장되었습니다.")
        return filename
