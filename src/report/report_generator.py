import json
import os
import re
from datetime import datetime
from src.models.seo_data import db, Website, Page, Keyword, Link, TechnicalSEO

class ReportGenerator:
    """
    SEO 분석 결과를 바탕으로 종합 보고서를 생성하는 클래스
    """
    
    def __init__(self, db_instance):
        """
        보고서 생성기 초기화
        
        Args:
            db_instance: SQLAlchemy 데이터베이스 인스턴스
        """
        self.db = db_instance
        
    def generate_report(self, website_id, technical_results, ranked_pages, onpage_results, output_dir):
        """
        종합 SEO 보고서 생성
        
        Args:
            website_id (int): 웹사이트 ID
            technical_results (dict): 기술적 SEO 검사 결과
            ranked_pages (list): 순위가 매겨진 페이지 목록
            onpage_results (list): 온페이지 SEO 분석 결과
            output_dir (str): 출력 디렉토리
            
        Returns:
            dict: 생성된 보고서 파일 경로
        """
        website = Website.query.get(website_id)
        if not website:
            raise ValueError(f"ID가 {website_id}인 웹사이트를 찾을 수 없습니다.")
            
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 보고서 데이터 준비
        report_data = self._prepare_report_data(website, technical_results, ranked_pages, onpage_results)
        
        # JSON 형식으로 보고서 데이터 저장
        json_file = os.path.join(output_dir, 'seo_report_data.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        # 마크다운 형식으로 보고서 생성
        md_file = os.path.join(output_dir, 'seo_report.md')
        self._generate_markdown_report(report_data, md_file)
        
        # HTML 형식으로 보고서 생성
        html_file = os.path.join(output_dir, 'seo_report.html')
        self._generate_html_report(report_data, html_file)
        
        # 프레젠테이션 데이터 생성
        presentation_data = self._prepare_presentation_data(report_data)
        presentation_file = os.path.join(output_dir, 'presentation_data.json')
        with open(presentation_file, 'w', encoding='utf-8') as f:
            json.dump(presentation_data, f, ensure_ascii=False, indent=2)
            
        return {
            'json': json_file,
            'markdown': md_file,
            'html': html_file,
            'presentation_data': presentation_file
        }
    
    def _prepare_report_data(self, website, technical_results, ranked_pages, onpage_results):
        """
        보고서 데이터 준비
        
        Args:
            website (Website): 웹사이트 객체
            technical_results (dict): 기술적 SEO 검사 결과
            ranked_pages (list): 순위가 매겨진 페이지 목록
            onpage_results (list): 온페이지 SEO 분석 결과
            
        Returns:
            dict: 보고서 데이터
        """
        # 현재 날짜
        now = datetime.now().strftime('%Y년 %m월 %d일')
        
        # 전체 점수 계산
        technical_score = self._calculate_technical_score(technical_results)
        onpage_score = sum(result['score'] for result in onpage_results) / len(onpage_results) if onpage_results else 0
        overall_score = (technical_score + onpage_score) / 2
        
        # 주요 이슈 및 권장사항 수집
        all_issues = []
        all_recommendations = []
        
        # 기술적 SEO 이슈 및 권장사항
        for category, analysis in technical_results.items():
            if isinstance(analysis, dict) and 'issues' in analysis and 'recommendations' in analysis:
                all_issues.extend([f"[기술적 SEO - {category}] {issue}" for issue in analysis['issues']])
                all_recommendations.extend([f"[기술적 SEO - {category}] {rec}" for rec in analysis['recommendations']])
                
        # 온페이지 SEO 이슈 및 권장사항
        for result in onpage_results:
            all_issues.extend([f"[온페이지 SEO - {result['url']}] {issue}" for issue in result['issues']])
            all_recommendations.extend([f"[온페이지 SEO - {result['url']}] {rec}" for rec in result['recommendations']])
            
        # 중요도에 따라 이슈 및 권장사항 정렬 (여기서는 간단히 길이로 정렬)
        all_issues.sort(key=len, reverse=True)
        all_recommendations.sort(key=len, reverse=True)
        
        # 상위 10개 이슈 및 권장사항 선택
        top_issues = all_issues[:10]
        top_recommendations = all_recommendations[:10]
        
        # 키워드 분석
        keywords_data = self._analyze_keywords(website.id)
        
        # 보고서 데이터 구성
        report_data = {
            'website': {
                'url': website.url,
                'domain': website.url.split('://')[-1].split('/')[0]
            },
            'date': now,
            'scores': {
                'overall': round(overall_score, 1),
                'technical': round(technical_score, 1),
                'onpage': round(onpage_score, 1)
            },
            'summary': {
                'top_issues': top_issues,
                'top_recommendations': top_recommendations
            },
            'technical_seo': technical_results,
            'ranked_pages': ranked_pages,
            'onpage_seo': onpage_results,
            'keywords': keywords_data
        }
        
        return report_data
    
    def _calculate_technical_score(self, technical_results):
        """
        기술적 SEO 점수 계산
        
        Args:
            technical_results (dict): 기술적 SEO 검사 결과
            
        Returns:
            float: 기술적 SEO 점수
        """
        # 각 카테고리별 가중치 설정
        weights = {
            'robots_txt': 0.05,
            'sitemap': 0.05,
            'site_structure': 0.1,
            'core_web_vitals': 0.2,
            'redirects': 0.05,
            'canonical': 0.05,
            'meta_tags': 0.15,
            'structured_data': 0.1,
            'links': 0.1,
            'mobile_friendly': 0.1,
            'security': 0.05,
            'page_speed': 0.1
        }
        
        # 각 카테고리별 점수 계산
        scores = {}
        
        # robots.txt
        if 'robots_txt' in technical_results:
            if technical_results['robots_txt']['exists']:
                scores['robots_txt'] = 100 - (len(technical_results['robots_txt']['issues']) * 20)
            else:
                scores['robots_txt'] = 0
                
        # sitemap
        if 'sitemap' in technical_results:
            if technical_results['sitemap']['exists']:
                scores['sitemap'] = 100 - (len(technical_results['sitemap']['issues']) * 20)
            else:
                scores['sitemap'] = 0
                
        # site_structure
        if 'site_structure' in technical_results:
            scores['site_structure'] = 100 - (len(technical_results['site_structure']['issues']) * 20)
            
        # core_web_vitals
        if 'core_web_vitals' in technical_results:
            cwv = technical_results['core_web_vitals']
            cwv_score = 0
            
            if 'LCP' in cwv and 'rating' in cwv['LCP']:
                if cwv['LCP']['rating'] == 'good':
                    cwv_score += 33
                elif cwv['LCP']['rating'] == 'needs improvement':
                    cwv_score += 16
                    
            if 'FID' in cwv and 'rating' in cwv['FID']:
                if cwv['FID']['rating'] == 'good':
                    cwv_score += 33
                elif cwv['FID']['rating'] == 'needs improvement':
                    cwv_score += 16
                    
            if 'CLS' in cwv and 'rating' in cwv['CLS']:
                if cwv['CLS']['rating'] == 'good':
                    cwv_score += 34
                elif cwv['CLS']['rating'] == 'needs improvement':
                    cwv_score += 17
                    
            scores['core_web_vitals'] = cwv_score
            
        # redirects
        if 'redirects' in technical_results:
            scores['redirects'] = 100 - (len(technical_results['redirects']['issues']) * 20)
            
        # canonical
        if 'canonical' in technical_results:
            canonical = technical_results['canonical']
            if 'pages_with_canonical' in canonical and 'total_pages' in canonical and canonical['total_pages'] > 0:
                scores['canonical'] = (canonical['pages_with_canonical'] / canonical['total_pages']) * 100
            else:
                scores['canonical'] = 0
                
        # meta_tags
        if 'meta_tags' in technical_results:
            meta_tags = technical_results['meta_tags']
            if 'pages_with_issues' in meta_tags and 'total_pages' in meta_tags and meta_tags['total_pages'] > 0:
                scores['meta_tags'] = 100 - ((meta_tags['pages_with_issues'] / meta_tags['total_pages']) * 100)
            else:
                scores['meta_tags'] = 0
                
        # structured_data
        if 'structured_data' in technical_results:
            structured_data = technical_results['structured_data']
            if 'pages_with_schema' in structured_data and 'total_pages' in structured_data and structured_data['total_pages'] > 0:
                scores['structured_data'] = (structured_data['pages_with_schema'] / structured_data['total_pages']) * 100
            else:
                scores['structured_data'] = 0
                
        # links
        if 'links' in technical_results:
            scores['links'] = 100 - (len(technical_results['links']['issues']) * 20)
            
        # mobile_friendly
        if 'mobile_friendly' in technical_results:
            if technical_results['mobile_friendly']['is_mobile_friendly']:
                scores['mobile_friendly'] = 100
            else:
                scores['mobile_friendly'] = 0
                
        # security
        if 'security' in technical_results:
            security = technical_results['security']
            security_score = 0
            
            if security['is_https']:
                security_score += 50
                
            if security['has_hsts']:
                security_score += 50
                
            scores['security'] = security_score
            
        # page_speed
        if 'page_speed' in technical_results:
            page_speed = technical_results['page_speed']
            scores['page_speed'] = (page_speed['mobile_score'] + page_speed['desktop_score']) / 2
            
        # 가중 평균 계산
        weighted_score = 0
        total_weight = 0
        
        for category, score in scores.items():
            if category in weights:
                weighted_score += score * weights[category]
                total_weight += weights[category]
                
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return 0
    
    def _analyze_keywords(self, website_id):
        """
        웹사이트의 키워드 분석
        
        Args:
            website_id (int): 웹사이트 ID
            
        Returns:
            dict: 키워드 분석 결과
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
            
        # 페이지별 주요 키워드
        page_keywords = {}
        pages = Page.query.filter_by(website_id=website_id).all()
        
        for page in pages:
            keywords = Keyword.query.filter_by(page_id=page.id).order_by(Keyword.count.desc()).limit(5).all()
            if keywords:
                page_keywords[page.url] = [{'keyword': kw.keyword, 'count': kw.count, 'density': kw.density} for kw in keywords]
                
        return {
            'global_keywords': global_keywords[:20],  # 상위 20개 키워드
            'page_keywords': page_keywords
        }
    
    def _generate_markdown_report(self, report_data, output_file):
        """
        마크다운 형식으로 보고서 생성
        
        Args:
            report_data (dict): 보고서 데이터
            output_file (str): 출력 파일 경로
            
        Returns:
            str: 생성된 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            # 제목 및 개요
            f.write(f"# {report_data['website']['domain']} SEO 감사 보고서\n\n")
            f.write(f"**분석 날짜:** {report_data['date']}\n\n")
            f.write(f"**웹사이트:** {report_data['website']['url']}\n\n")
            
            # 종합 점수
            f.write("## 종합 SEO 점수\n\n")
            f.write(f"**전체 점수:** {report_data['scores']['overall']}/100\n\n")
            f.write(f"**기술적 SEO 점수:** {report_data['scores']['technical']}/100\n\n")
            f.write(f"**온페이지 SEO 점수:** {report_data['scores']['onpage']}/100\n\n")
            
            # 주요 이슈 및 권장사항
            f.write("## 주요 이슈 및 개선 권장사항\n\n")
            
            f.write("### 주요 이슈\n\n")
            for issue in report_data['summary']['top_issues']:
                f.write(f"- {issue}\n")
            f.write("\n")
            
            f.write("### 개선 권장사항\n\n")
            for recommendation in report_data['summary']['top_recommendations']:
                f.write(f"- {recommendation}\n")
            f.write("\n")
            
            # 기술적 SEO 분석
            f.write("## 기술적 SEO 분석\n\n")
            
            # robots.txt
            if 'robots_txt' in report_data['technical_seo']:
                robots = report_data['technical_seo']['robots_txt']
                f.write("### robots.txt 분석\n\n")
                f.write(f"**상태:** {'존재함' if robots['exists'] else '존재하지 않음'}\n\n")
                if robots['exists']:
                    f.write(f"**URL:** {robots['url']}\n\n")
                    f.write("**내용:**\n\n")
                    f.write("```\n")
                    f.write(robots['content'][:500] + ('...' if len(robots['content']) > 500 else ''))
                    f.write("\n```\n\n")
                
                if robots['issues']:
                    f.write("**이슈:**\n\n")
                    for issue in robots['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                if robots['recommendations']:
                    f.write("**권장사항:**\n\n")
                    for rec in robots['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            # sitemap.xml
            if 'sitemap' in report_data['technical_seo']:
                sitemap = report_data['technical_seo']['sitemap']
                f.write("### sitemap.xml 분석\n\n")
                f.write(f"**상태:** {'존재함' if sitemap['exists'] else '존재하지 않음'}\n\n")
                if sitemap['exists']:
                    f.write(f"**URL:** {sitemap['url']}\n\n")
                    f.write(f"**URL 수:** {sitemap['urls_count']}\n\n")
                
                if sitemap['issues']:
                    f.write("**이슈:**\n\n")
                    for issue in sitemap['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                if sitemap['recommendations']:
                    f.write("**권장사항:**\n\n")
                    for rec in sitemap['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            # 사이트 구조
            if 'site_structure' in report_data['technical_seo']:
                structure = report_data['technical_seo']['site_structure']
                f.write("### 사이트 구조 분석\n\n")
                f.write(f"**총 페이지 수:** {structure['total_pages']}\n\n")
                f.write(f"**최대 깊이:** {structure['max_depth']}\n\n")
                
                f.write("**깊이별 페이지 분포:**\n\n")
                for depth, count in structure['depth_distribution'].items():
                    f.write(f"- 깊이 {depth}: {count}개 페이지\n")
                f.write("\n")
                
                if structure['issues']:
                    f.write("**이슈:**\n\n")
                    for issue in structure['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                if structure['recommendations']:
                    f.write("**권장사항:**\n\n")
                    for rec in structure['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            # Core Web Vitals
            if 'core_web_vitals' in report_data['technical_seo']:
                cwv = report_data['technical_seo']['core_web_vitals']
                f.write("### Core Web Vitals 분석\n\n")
                
                if 'LCP' in cwv:
                    lcp = cwv['LCP']
                    f.write(f"**LCP (Largest Contentful Paint):** {lcp['value']}초 ({lcp['rating']})\n\n")
                    f.write(f"- 좋음: {lcp['threshold']['good']}초 이하\n")
                    f.write(f"- 개선 필요: {lcp['threshold']['good']}초 ~ {lcp['threshold']['poor']}초\n")
                    f.write(f"- 나쁨: {lcp['threshold']['poor']}초 이상\n\n")
                
                if 'FID' in cwv:
                    fid = cwv['FID']
                    f.write(f"**FID (First Input Delay):** {fid['value']}ms ({fid['rating']})\n\n")
                    f.write(f"- 좋음: {fid['threshold']['good']}ms 이하\n")
                    f.write(f"- 개선 필요: {fid['threshold']['good']}ms ~ {fid['threshold']['poor']}ms\n")
                    f.write(f"- 나쁨: {fid['threshold']['poor']}ms 이상\n\n")
                
                if 'CLS' in cwv:
                    cls = cwv['CLS']
                    f.write(f"**CLS (Cumulative Layout Shift):** {cls['value']} ({cls['rating']})\n\n")
                    f.write(f"- 좋음: {cls['threshold']['good']} 이하\n")
                    f.write(f"- 개선 필요: {cls['threshold']['good']} ~ {cls['threshold']['poor']}\n")
                    f.write(f"- 나쁨: {cls['threshold']['poor']} 이상\n\n")
                
                if 'issues' in cwv and cwv['issues']:
                    f.write("**이슈:**\n\n")
                    for issue in cwv['issues']:
                        f.write(f"- {issue}\n")
                    f.write("\n")
                
                if 'recommendations' in cwv and cwv['recommendations']:
                    f.write("**권장사항:**\n\n")
                    for rec in cwv['recommendations']:
                        f.write(f"- {rec}\n")
                    f.write("\n")
            
            # 키워드 분석
            f.write("## 키워드 분석\n\n")
            
            f.write("### 상위 키워드\n\n")
            f.write("| 키워드 | 출현 횟수 | 밀도(%) |\n")
            f.write("|--------|-----------|--------|\n")
            for kw in report_data['keywords']['global_keywords'][:10]:
                f.write(f"| {kw['keyword']} | {kw['count']} | {kw['density']} |\n")
            f.write("\n")
            
            # 상위 페이지 분석
            f.write("## 상위 페이지 분석\n\n")
            
            f.write("### 중요도 기준 상위 10개 페이지\n\n")
            f.write("| 순위 | URL | 점수 | 깊이 | 내부 링크 수 |\n")
            f.write("|------|-----|------|------|-------------|\n")
            for i, page in enumerate(report_data['ranked_pages'][:10]):
                f.write(f"| {i+1} | {page['url']} | {page['score']} | {page['depth']} | {page['inbound_links']} |\n")
            f.write("\n")
            
            # 온페이지 SEO 분석
            f.write("## 온페이지 SEO 분석\n\n")
            
            for i, page in enumerate(report_data['onpage_seo'][:5]):  # 상위 5개 페이지만 상세 분석
                f.write(f"### {i+1}. {page['url']}\n\n")
                f.write(f"**점수:** {page['score']}/100\n\n")
                f.write(f"**제목:** {page['title']}\n\n")
                f.write(f"**메타 설명:** {page['meta_description']}\n\n")
                
                f.write("**주요 키워드:**\n\n")
                for kw in page['keywords'][:5]:
                    f.write(f"- {kw['keyword']} (밀도: {kw['density']}%)\n")
                f.write("\n")
                
                f.write("**주요 이슈:**\n\n")
                for issue in page['issues'][:5]:
                    f.write(f"- {issue}\n")
                f.write("\n")
                
                f.write("**개선 권장사항:**\n\n")
                for rec in page['recommendations'][:5]:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            # 결론 및 다음 단계
            f.write("## 결론 및 다음 단계\n\n")
            
            f.write("이 SEO 감사 보고서는 웹사이트의 현재 SEO 상태에 대한 종합적인 분석을 제공합니다. ")
            f.write("위에서 언급한 이슈를 해결하고 권장사항을 구현함으로써 검색 엔진 순위와 가시성을 크게 향상시킬 수 있습니다.\n\n")
            
            f.write("### 우선순위가 높은 작업\n\n")
            
            # 우선순위가 높은 권장사항 선택 (여기서는 처음 3개)
            for i, rec in enumerate(report_data['summary']['top_recommendations'][:3]):
                f.write(f"{i+1}. {rec}\n")
            f.write("\n")
            
            f.write("### 중기 작업\n\n")
            
            # 중기 권장사항 선택 (여기서는 다음 3개)
            for i, rec in enumerate(report_data['summary']['top_recommendations'][3:6]):
                f.write(f"{i+1}. {rec}\n")
            f.write("\n")
            
            f.write("### 장기 작업\n\n")
            
            # 장기 권장사항 선택 (여기서는 나머지)
            for i, rec in enumerate(report_data['summary']['top_recommendations'][6:9]):
                f.write(f"{i+1}. {rec}\n")
            f.write("\n")
            
            # 용어 설명
            f.write("## 용어 설명\n\n")
            
            f.write("- **SEO (Search Engine Optimization, 검색 엔진 최적화)**: 웹사이트가 검색 엔진 결과 페이지에서 더 높은 순위를 차지하도록 최적화하는 과정입니다.\n")
            f.write("- **Core Web Vitals**: 사용자 경험을 측정하는 Google의 지표로, LCP, FID, CLS로 구성됩니다.\n")
            f.write("- **LCP (Largest Contentful Paint, 최대 콘텐츠풀 페인트)**: 페이지 로드 시 가장 큰 콘텐츠 요소가 표시되는 시간을 측정합니다.\n")
            f.write("- **FID (First Input Delay, 최초 입력 지연)**: 사용자가 페이지와 처음 상호 작용할 때 브라우저가 응답하는 데 걸리는 시간을 측정합니다.\n")
            f.write("- **CLS (Cumulative Layout Shift, 누적 레이아웃 이동)**: 페이지 로드 중 예기치 않은 레이아웃 이동의 양을 측정합니다.\n")
            f.write("- **robots.txt**: 검색 엔진 크롤러에게 웹사이트의 어떤 부분을 크롤링해야 하는지 알려주는 파일입니다.\n")
            f.write("- **sitemap.xml**: 웹사이트의 모든 페이지 목록을 제공하여 검색 엔진이 콘텐츠를 더 효율적으로 크롤링할 수 있도록 돕는 파일입니다.\n")
            f.write("- **canonical 태그**: 중복 콘텐츠가 있는 경우 검색 엔진에 원본 URL을 알려주는 HTML 태그입니다.\n")
            f.write("- **키워드 밀도**: 전체 콘텐츠 대비 특정 키워드의 출현 빈도를 백분율로 나타낸 것입니다.\n")
            f.write("- **메타 설명**: 검색 결과에 표시되는 페이지에 대한 간략한 설명을 제공하는 HTML 태그입니다.\n")
            
        return output_file
    
    def _generate_html_report(self, report_data, output_file):
        """
        HTML 형식으로 보고서 생성
        
        Args:
            report_data (dict): 보고서 데이터
            output_file (str): 출력 파일 경로
            
        Returns:
            str: 생성된 파일 경로
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            # HTML 헤더
            f.write("""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO 감사 보고서</title>
    <style>
        body {
            font-family: 'Noto Sans KR', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
        }
        h1 {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .score-container {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }
        .score-box {
            flex: 1;
            margin: 0 10px;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .overall-score {
            background-color: #3498db;
            color: white;
        }
        .technical-score {
            background-color: #2ecc71;
            color: white;
        }
        .onpage-score {
            background-color: #e74c3c;
            color: white;
        }
        .score-value {
            font-size: 2em;
            font-weight: bold;
        }
        .issues, .recommendations {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .issues li, .recommendations li {
            margin-bottom: 10px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .glossary-term {
            font-weight: bold;
        }
        .glossary-definition {
            margin-left: 20px;
            margin-bottom: 10px;
        }
        @media print {
            body {
                font-size: 12pt;
            }
            .score-box {
                break-inside: avoid;
            }
            h2, h3 {
                break-after: avoid;
            }
            table {
                break-inside: auto;
            }
            tr {
                break-inside: avoid;
                break-after: auto;
            }
        }
    </style>
</head>
<body>
""")
            
            # 제목 및 개요
            f.write(f"<h1>{report_data['website']['domain']} SEO 감사 보고서</h1>\n")
            f.write(f"<p><strong>분석 날짜:</strong> {report_data['date']}</p>\n")
            f.write(f"<p><strong>웹사이트:</strong> {report_data['website']['url']}</p>\n")
            
            # 종합 점수
            f.write("<h2>종합 SEO 점수</h2>\n")
            f.write("<div class='score-container'>\n")
            f.write(f"<div class='score-box overall-score'><h3>전체 점수</h3><div class='score-value'>{report_data['scores']['overall']}</div><div>/ 100</div></div>\n")
            f.write(f"<div class='score-box technical-score'><h3>기술적 SEO</h3><div class='score-value'>{report_data['scores']['technical']}</div><div>/ 100</div></div>\n")
            f.write(f"<div class='score-box onpage-score'><h3>온페이지 SEO</h3><div class='score-value'>{report_data['scores']['onpage']}</div><div>/ 100</div></div>\n")
            f.write("</div>\n")
            
            # 주요 이슈 및 권장사항
            f.write("<h2>주요 이슈 및 개선 권장사항</h2>\n")
            
            f.write("<h3>주요 이슈</h3>\n")
            f.write("<div class='issues'>\n<ul>\n")
            for issue in report_data['summary']['top_issues']:
                f.write(f"<li>{issue}</li>\n")
            f.write("</ul>\n</div>\n")
            
            f.write("<h3>개선 권장사항</h3>\n")
            f.write("<div class='recommendations'>\n<ul>\n")
            for recommendation in report_data['summary']['top_recommendations']:
                f.write(f"<li>{recommendation}</li>\n")
            f.write("</ul>\n</div>\n")
            
            # 기술적 SEO 분석
            f.write("<h2>기술적 SEO 분석</h2>\n")
            
            # robots.txt
            if 'robots_txt' in report_data['technical_seo']:
                robots = report_data['technical_seo']['robots_txt']
                f.write("<h3>robots.txt 분석</h3>\n")
                f.write(f"<p><strong>상태:</strong> {'존재함' if robots['exists'] else '존재하지 않음'}</p>\n")
                if robots['exists']:
                    f.write(f"<p><strong>URL:</strong> {robots['url']}</p>\n")
                    f.write("<p><strong>내용:</strong></p>\n")
                    f.write("<pre>\n")
                    f.write(robots['content'][:500] + ('...' if len(robots['content']) > 500 else ''))
                    f.write("\n</pre>\n")
                
                if robots['issues']:
                    f.write("<p><strong>이슈:</strong></p>\n<ul>\n")
                    for issue in robots['issues']:
                        f.write(f"<li>{issue}</li>\n")
                    f.write("</ul>\n")
                
                if robots['recommendations']:
                    f.write("<p><strong>권장사항:</strong></p>\n<ul>\n")
                    for rec in robots['recommendations']:
                        f.write(f"<li>{rec}</li>\n")
                    f.write("</ul>\n")
            
            # sitemap.xml
            if 'sitemap' in report_data['technical_seo']:
                sitemap = report_data['technical_seo']['sitemap']
                f.write("<h3>sitemap.xml 분석</h3>\n")
                f.write(f"<p><strong>상태:</strong> {'존재함' if sitemap['exists'] else '존재하지 않음'}</p>\n")
                if sitemap['exists']:
                    f.write(f"<p><strong>URL:</strong> {sitemap['url']}</p>\n")
                    f.write(f"<p><strong>URL 수:</strong> {sitemap['urls_count']}</p>\n")
                
                if sitemap['issues']:
                    f.write("<p><strong>이슈:</strong></p>\n<ul>\n")
                    for issue in sitemap['issues']:
                        f.write(f"<li>{issue}</li>\n")
                    f.write("</ul>\n")
                
                if sitemap['recommendations']:
                    f.write("<p><strong>권장사항:</strong></p>\n<ul>\n")
                    for rec in sitemap['recommendations']:
                        f.write(f"<li>{rec}</li>\n")
                    f.write("</ul>\n")
            
            # 사이트 구조
            if 'site_structure' in report_data['technical_seo']:
                structure = report_data['technical_seo']['site_structure']
                f.write("<h3>사이트 구조 분석</h3>\n")
                f.write(f"<p><strong>총 페이지 수:</strong> {structure['total_pages']}</p>\n")
                f.write(f"<p><strong>최대 깊이:</strong> {structure['max_depth']}</p>\n")
                
                f.write("<p><strong>깊이별 페이지 분포:</strong></p>\n<ul>\n")
                for depth, count in structure['depth_distribution'].items():
                    f.write(f"<li>깊이 {depth}: {count}개 페이지</li>\n")
                f.write("</ul>\n")
                
                if structure['issues']:
                    f.write("<p><strong>이슈:</strong></p>\n<ul>\n")
                    for issue in structure['issues']:
                        f.write(f"<li>{issue}</li>\n")
                    f.write("</ul>\n")
                
                if structure['recommendations']:
                    f.write("<p><strong>권장사항:</strong></p>\n<ul>\n")
                    for rec in structure['recommendations']:
                        f.write(f"<li>{rec}</li>\n")
                    f.write("</ul>\n")
            
            # Core Web Vitals
            if 'core_web_vitals' in report_data['technical_seo']:
                cwv = report_data['technical_seo']['core_web_vitals']
                f.write("<h3>Core Web Vitals 분석</h3>\n")
                
                if 'LCP' in cwv:
                    lcp = cwv['LCP']
                    f.write(f"<p><strong>LCP (Largest Contentful Paint):</strong> {lcp['value']}초 ({lcp['rating']})</p>\n")
                    f.write("<ul>\n")
                    f.write(f"<li>좋음: {lcp['threshold']['good']}초 이하</li>\n")
                    f.write(f"<li>개선 필요: {lcp['threshold']['good']}초 ~ {lcp['threshold']['poor']}초</li>\n")
                    f.write(f"<li>나쁨: {lcp['threshold']['poor']}초 이상</li>\n")
                    f.write("</ul>\n")
                
                if 'FID' in cwv:
                    fid = cwv['FID']
                    f.write(f"<p><strong>FID (First Input Delay):</strong> {fid['value']}ms ({fid['rating']})</p>\n")
                    f.write("<ul>\n")
                    f.write(f"<li>좋음: {fid['threshold']['good']}ms 이하</li>\n")
                    f.write(f"<li>개선 필요: {fid['threshold']['good']}ms ~ {fid['threshold']['poor']}ms</li>\n")
                    f.write(f"<li>나쁨: {fid['threshold']['poor']}ms 이상</li>\n")
                    f.write("</ul>\n")
                
                if 'CLS' in cwv:
                    cls = cwv['CLS']
                    f.write(f"<p><strong>CLS (Cumulative Layout Shift):</strong> {cls['value']} ({cls['rating']})</p>\n")
                    f.write("<ul>\n")
                    f.write(f"<li>좋음: {cls['threshold']['good']} 이하</li>\n")
                    f.write(f"<li>개선 필요: {cls['threshold']['good']} ~ {cls['threshold']['poor']}</li>\n")
                    f.write(f"<li>나쁨: {cls['threshold']['poor']} 이상</li>\n")
                    f.write("</ul>\n")
                
                if 'issues' in cwv and cwv['issues']:
                    f.write("<p><strong>이슈:</strong></p>\n<ul>\n")
                    for issue in cwv['issues']:
                        f.write(f"<li>{issue}</li>\n")
                    f.write("</ul>\n")
                
                if 'recommendations' in cwv and cwv['recommendations']:
                    f.write("<p><strong>권장사항:</strong></p>\n<ul>\n")
                    for rec in cwv['recommendations']:
                        f.write(f"<li>{rec}</li>\n")
                    f.write("</ul>\n")
            
            # 키워드 분석
            f.write("<h2>키워드 분석</h2>\n")
            
            f.write("<h3>상위 키워드</h3>\n")
            f.write("<table>\n")
            f.write("<tr><th>키워드</th><th>출현 횟수</th><th>밀도(%)</th></tr>\n")
            for kw in report_data['keywords']['global_keywords'][:10]:
                f.write(f"<tr><td>{kw['keyword']}</td><td>{kw['count']}</td><td>{kw['density']}</td></tr>\n")
            f.write("</table>\n")
            
            # 상위 페이지 분석
            f.write("<h2>상위 페이지 분석</h2>\n")
            
            f.write("<h3>중요도 기준 상위 10개 페이지</h3>\n")
            f.write("<table>\n")
            f.write("<tr><th>순위</th><th>URL</th><th>점수</th><th>깊이</th><th>내부 링크 수</th></tr>\n")
            for i, page in enumerate(report_data['ranked_pages'][:10]):
                f.write(f"<tr><td>{i+1}</td><td>{page['url']}</td><td>{page['score']}</td><td>{page['depth']}</td><td>{page['inbound_links']}</td></tr>\n")
            f.write("</table>\n")
            
            # 온페이지 SEO 분석
            f.write("<h2>온페이지 SEO 분석</h2>\n")
            
            for i, page in enumerate(report_data['onpage_seo'][:5]):  # 상위 5개 페이지만 상세 분석
                f.write(f"<h3>{i+1}. {page['url']}</h3>\n")
                f.write(f"<p><strong>점수:</strong> {page['score']}/100</p>\n")
                f.write(f"<p><strong>제목:</strong> {page['title']}</p>\n")
                f.write(f"<p><strong>메타 설명:</strong> {page['meta_description']}</p>\n")
                
                f.write("<p><strong>주요 키워드:</strong></p>\n<ul>\n")
                for kw in page['keywords'][:5]:
                    f.write(f"<li>{kw['keyword']} (밀도: {kw['density']}%)</li>\n")
                f.write("</ul>\n")
                
                f.write("<p><strong>주요 이슈:</strong></p>\n<ul>\n")
                for issue in page['issues'][:5]:
                    f.write(f"<li>{issue}</li>\n")
                f.write("</ul>\n")
                
                f.write("<p><strong>개선 권장사항:</strong></p>\n<ul>\n")
                for rec in page['recommendations'][:5]:
                    f.write(f"<li>{rec}</li>\n")
                f.write("</ul>\n")
            
            # 결론 및 다음 단계
            f.write("<h2>결론 및 다음 단계</h2>\n")
            
            f.write("<p>이 SEO 감사 보고서는 웹사이트의 현재 SEO 상태에 대한 종합적인 분석을 제공합니다. ")
            f.write("위에서 언급한 이슈를 해결하고 권장사항을 구현함으로써 검색 엔진 순위와 가시성을 크게 향상시킬 수 있습니다.</p>\n")
            
            f.write("<h3>우선순위가 높은 작업</h3>\n<ol>\n")
            
            # 우선순위가 높은 권장사항 선택 (여기서는 처음 3개)
            for rec in report_data['summary']['top_recommendations'][:3]:
                f.write(f"<li>{rec}</li>\n")
            f.write("</ol>\n")
            
            f.write("<h3>중기 작업</h3>\n<ol>\n")
            
            # 중기 권장사항 선택 (여기서는 다음 3개)
            for rec in report_data['summary']['top_recommendations'][3:6]:
                f.write(f"<li>{rec}</li>\n")
            f.write("</ol>\n")
            
            f.write("<h3>장기 작업</h3>\n<ol>\n")
            
            # 장기 권장사항 선택 (여기서는 나머지)
            for rec in report_data['summary']['top_recommendations'][6:9]:
                f.write(f"<li>{rec}</li>\n")
            f.write("</ol>\n")
            
            # 용어 설명
            f.write("<h2>용어 설명</h2>\n")
            
            f.write("<dl>\n")
            f.write("<dt class='glossary-term'>SEO (Search Engine Optimization, 검색 엔진 최적화)</dt>\n")
            f.write("<dd class='glossary-definition'>웹사이트가 검색 엔진 결과 페이지에서 더 높은 순위를 차지하도록 최적화하는 과정입니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>Core Web Vitals</dt>\n")
            f.write("<dd class='glossary-definition'>사용자 경험을 측정하는 Google의 지표로, LCP, FID, CLS로 구성됩니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>LCP (Largest Contentful Paint, 최대 콘텐츠풀 페인트)</dt>\n")
            f.write("<dd class='glossary-definition'>페이지 로드 시 가장 큰 콘텐츠 요소가 표시되는 시간을 측정합니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>FID (First Input Delay, 최초 입력 지연)</dt>\n")
            f.write("<dd class='glossary-definition'>사용자가 페이지와 처음 상호 작용할 때 브라우저가 응답하는 데 걸리는 시간을 측정합니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>CLS (Cumulative Layout Shift, 누적 레이아웃 이동)</dt>\n")
            f.write("<dd class='glossary-definition'>페이지 로드 중 예기치 않은 레이아웃 이동의 양을 측정합니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>robots.txt</dt>\n")
            f.write("<dd class='glossary-definition'>검색 엔진 크롤러에게 웹사이트의 어떤 부분을 크롤링해야 하는지 알려주는 파일입니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>sitemap.xml</dt>\n")
            f.write("<dd class='glossary-definition'>웹사이트의 모든 페이지 목록을 제공하여 검색 엔진이 콘텐츠를 더 효율적으로 크롤링할 수 있도록 돕는 파일입니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>canonical 태그</dt>\n")
            f.write("<dd class='glossary-definition'>중복 콘텐츠가 있는 경우 검색 엔진에 원본 URL을 알려주는 HTML 태그입니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>키워드 밀도</dt>\n")
            f.write("<dd class='glossary-definition'>전체 콘텐츠 대비 특정 키워드의 출현 빈도를 백분율로 나타낸 것입니다.</dd>\n")
            
            f.write("<dt class='glossary-term'>메타 설명</dt>\n")
            f.write("<dd class='glossary-definition'>검색 결과에 표시되는 페이지에 대한 간략한 설명을 제공하는 HTML 태그입니다.</dd>\n")
            f.write("</dl>\n")
            
            # HTML 푸터
            f.write("""
</body>
</html>
""")
            
        return output_file
    
    def _prepare_presentation_data(self, report_data):
        """
        프레젠테이션 데이터 준비
        
        Args:
            report_data (dict): 보고서 데이터
            
        Returns:
            dict: 프레젠테이션 데이터
        """
        presentation_data = {
            'title': f"{report_data['website']['domain']} SEO 감사 보고서",
            'date': report_data['date'],
            'website': report_data['website']['url'],
            'scores': report_data['scores'],
            'slides': [
                {
                    'title': '개요',
                    'content': {
                        'text': f"이 보고서는 {report_data['website']['url']}의 SEO 상태에 대한 종합적인 분석을 제공합니다.",
                        'points': [
                            "검색 엔진 최적화(SEO)는 웹사이트의 가시성과 검색 엔진 순위를 향상시키는 과정입니다.",
                            "이 감사는 기술적 SEO, 온페이지 SEO, 키워드 분석을 포함합니다.",
                            f"분석 날짜: {report_data['date']}"
                        ]
                    }
                },
                {
                    'title': 'SEO 점수',
                    'content': {
                        'scores': {
                            'overall': report_data['scores']['overall'],
                            'technical': report_data['scores']['technical'],
                            'onpage': report_data['scores']['onpage']
                        }
                    }
                },
                {
                    'title': '주요 이슈',
                    'content': {
                        'issues': report_data['summary']['top_issues'][:5]
                    }
                },
                {
                    'title': '개선 권장사항',
                    'content': {
                        'recommendations': report_data['summary']['top_recommendations'][:5]
                    }
                },
                {
                    'title': '기술적 SEO 분석',
                    'content': {
                        'text': "기술적 SEO는 검색 엔진이 웹사이트를 크롤링하고 색인화하는 방식에 영향을 미치는 요소입니다.",
                        'categories': [
                            {'name': 'robots.txt', 'status': '존재함' if report_data['technical_seo'].get('robots_txt', {}).get('exists', False) else '존재하지 않음'},
                            {'name': 'sitemap.xml', 'status': '존재함' if report_data['technical_seo'].get('sitemap', {}).get('exists', False) else '존재하지 않음'},
                            {'name': '사이트 구조', 'status': f"최대 깊이: {report_data['technical_seo'].get('site_structure', {}).get('max_depth', 'N/A')}"},
                            {'name': 'Core Web Vitals', 'status': report_data['technical_seo'].get('core_web_vitals', {}).get('LCP', {}).get('rating', 'N/A')},
                            {'name': '모바일 친화성', 'status': '좋음' if report_data['technical_seo'].get('mobile_friendly', {}).get('is_mobile_friendly', False) else '개선 필요'},
                            {'name': 'HTTPS', 'status': '사용 중' if report_data['technical_seo'].get('security', {}).get('is_https', False) else '사용하지 않음'}
                        ]
                    }
                },
                {
                    'title': '상위 키워드 분석',
                    'content': {
                        'text': "키워드 분석은 웹사이트의 콘텐츠가 사용자의 검색 의도와 얼마나 잘 일치하는지 보여줍니다.",
                        'keywords': report_data['keywords']['global_keywords'][:10]
                    }
                },
                {
                    'title': '상위 페이지',
                    'content': {
                        'text': "다음은 중요도에 따라 순위가 매겨진 상위 페이지입니다.",
                        'pages': report_data['ranked_pages'][:5]
                    }
                },
                {
                    'title': '온페이지 SEO 분석',
                    'content': {
                        'text': "온페이지 SEO는 개별 페이지의 콘텐츠와 HTML 소스 코드를 최적화하는 것을 의미합니다.",
                        'pages': [
                            {
                                'url': page['url'],
                                'score': page['score'],
                                'issues': page['issues'][:3]
                            } for page in report_data['onpage_seo'][:3]
                        ]
                    }
                },
                {
                    'title': '다음 단계',
                    'content': {
                        'text': "다음은 SEO를 개선하기 위한 권장 단계입니다.",
                        'steps': {
                            'high': report_data['summary']['top_recommendations'][:3],
                            'medium': report_data['summary']['top_recommendations'][3:6],
                            'low': report_data['summary']['top_recommendations'][6:9]
                        }
                    }
                },
                {
                    'title': '감사합니다',
                    'content': {
                        'text': "질문이 있으시면 언제든지 문의해 주세요.",
                        'contact': "example@example.com"
                    }
                }
            ]
        }
        
        return presentation_data
