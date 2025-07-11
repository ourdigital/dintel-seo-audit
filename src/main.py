import sys
import os
import nltk

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure NLTK data path to use ~/Utilities/nltk_data
nltk_data_path = os.path.expanduser("~/Utilities/nltk_data")
if os.path.exists(nltk_data_path):
    nltk.data.path.insert(0, nltk_data_path)
    print(f"Using NLTK data from: {nltk_data_path}")
else:
    print(f"NLTK data path not found: {nltk_data_path}")
    print("NLTK will use default data locations")

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
import json
import tempfile
from werkzeug.utils import secure_filename
from urllib.parse import quote
from src.models.seo_data import db, Website, Page, Keyword, Link, TechnicalSEO
from src.crawler.seo_crawler import SEOCrawler
from src.crawler.data_importer import SEODataImporter
from src.analyzer.text_analyzer import TextAnalyzer
from src.analyzer.technical_seo_checker import TechnicalSEOChecker
from src.analyzer.page_ranker import PageRanker
from src.analyzer.onpage_seo_analyzer import OnPageSEOAnalyzer
from src.report.report_generator import ReportGenerator
from src.presentation.presentation_designer import PresentationDesigner

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seo_audit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'reports')
app.config['CHARTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'charts')
app.config['PRESENTATIONS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'presentations')

# Create required directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHARTS_FOLDER'], exist_ok=True)
os.makedirs(app.config['PRESENTATIONS_FOLDER'], exist_ok=True)

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def audit():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required.'}), 400
        
    # Generate session ID
    session_id = secure_filename(url.replace('://', '_').replace('/', '_'))
    
    # Create working directory
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Start crawling and analysis process
    return jsonify({
        'session_id': session_id,
        'message': f'Crawling and analysis process started for {url}.',
        'redirect': url_for('audit_status', session_id=session_id) + f'?url={quote(url)}'
    })

@app.route('/audit/<session_id>/status')
def audit_status(session_id):
    return render_template('audit_status.html', session_id=session_id)

@app.route('/api/audit/<session_id>/start', methods=['POST'])
def start_audit(session_id):
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required.'}), 400
        
    # Create working directory
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    try:
        # 1. Crawling
        crawler = SEOCrawler(url, max_pages=50, max_depth=3)
        crawl_result = crawler.crawl()
        
        # Save crawling results
        crawl_file = os.path.join(session_dir, 'crawl_result.json')
        with open(crawl_file, 'w', encoding='utf-8') as f:
            json.dump(crawl_result, f, ensure_ascii=False, indent=2)
            
        # 2. Database initialization
        with app.app_context():
            db.create_all()
            
            # 3. Import crawling data
            importer = SEODataImporter(db)
            import_summary = importer.import_from_json(crawl_file)
            
            # Get website ID
            website = Website.query.filter_by(url=url).first()
            if not website:
                return jsonify({'error': 'Website information not found.'}), 500
                
            website_id = website.id
            
            # 4. Text analysis
            analyzer = TextAnalyzer(db)
            text_analysis = analyzer.analyze_website(website_id)
            
            # Save text analysis results
            text_analysis_dir = os.path.join(session_dir, 'text_analysis')
            analysis_files = analyzer.save_analysis_results(text_analysis, text_analysis_dir)
            
            # 5. Technical SEO check
            tech_checker = TechnicalSEOChecker(db)
            tech_results = tech_checker.check_website(website_id)
            
            # Save technical SEO check results
            tech_file = os.path.join(session_dir, 'technical_seo.json')
            tech_checker.save_results(tech_results, tech_file)
            
            # 6. Page ranking
            ranker = PageRanker(db)
            ranked_pages = ranker.rank_pages(website_id, top_n=20)
            
            # Save page ranking results
            ranking_file = os.path.join(session_dir, 'ranked_pages.json')
            ranker.save_ranked_pages(ranked_pages, ranking_file)
            
            # 7. On-page SEO analysis
            page_ids = [page['id'] for page in ranked_pages]
            onpage_analyzer = OnPageSEOAnalyzer(db)
            onpage_results = onpage_analyzer.analyze_pages(page_ids)
            
            # Save on-page SEO analysis results
            onpage_file = os.path.join(session_dir, 'onpage_seo.json')
            onpage_analyzer.save_analysis_results(onpage_results, onpage_file)
            
            # 8. Report generation
            report_dir = os.path.join(app.config['REPORTS_FOLDER'], session_id)
            os.makedirs(report_dir, exist_ok=True)
            
            report_generator = ReportGenerator(db)
            report_files = report_generator.generate_report(
                website_id,
                tech_results,
                ranked_pages,
                onpage_results,
                report_dir
            )
            
            # 9. Presentation design
            with open(report_files['json'], 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                
            charts_dir = os.path.join(app.config['CHARTS_FOLDER'], session_id)
            os.makedirs(charts_dir, exist_ok=True)
            
            presentation_dir = os.path.join(app.config['PRESENTATIONS_FOLDER'], session_id)
            os.makedirs(presentation_dir, exist_ok=True)
            
            designer = PresentationDesigner(report_data)
            charts = designer.generate_charts(charts_dir)
            
            # Generate HTML presentation
            html_file = os.path.join(presentation_dir, 'presentation.html')
            designer.generate_presentation_html(charts, html_file)
            
            # Generate PPTX
            pptx_file = os.path.join(presentation_dir, 'presentation.pptx')
            designer.generate_pptx(charts, pptx_file)
            
            # Generate PDF
            pdf_file = os.path.join(presentation_dir, 'presentation.pdf')
            designer.generate_pdf(html_file, pdf_file)
            
            # Save results
            result = {
                'session_id': session_id,
                'website_url': url,
                'website_id': website_id,
                'crawl_file': crawl_file,
                'import_summary': import_summary,
                'text_analysis': analysis_files,
                'technical_seo': tech_file,
                'ranked_pages': ranking_file,
                'onpage_seo': onpage_file,
                'report': report_files,
                'charts': charts,
                'presentation': {
                    'html': html_file,
                    'pptx': pptx_file,
                    'pdf': pdf_file
                }
            }
            
            # Save result file
            result_file = os.path.join(session_dir, 'result.json')
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            return jsonify({
                'status': 'success',
                'message': 'Audit completed successfully.',
                'result': {
                    'session_id': session_id,
                    'presentation_url': url_for('view_presentation', session_id=session_id),
                    'download': {
                        'pptx': url_for('download_pptx', session_id=session_id),
                        'pdf': url_for('download_pdf', session_id=session_id)
                    }
                }
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred during audit: {str(e)}'
        }), 500

@app.route('/api/audit/<session_id>/status', methods=['GET'])
def check_audit_status(session_id):
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    result_file = os.path.join(session_dir, 'result.json')
    
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
            
        return jsonify({
            'status': 'completed',
            'result': {
                'session_id': session_id,
                'presentation_url': url_for('view_presentation', session_id=session_id),
                'download': {
                    'pptx': url_for('download_pptx', session_id=session_id),
                    'pdf': url_for('download_pdf', session_id=session_id)
                }
            }
        })
    else:
        return jsonify({
            'status': 'in_progress',
            'message': '감사가 진행 중입니다.'
        })

@app.route('/presentation/<session_id>')
def view_presentation(session_id):
    presentation_file = os.path.join(app.config['PRESENTATIONS_FOLDER'], session_id, 'presentation.html')
    
    if not os.path.exists(presentation_file):
        return render_template('error.html', message='프레젠테이션을 찾을 수 없습니다.')
        
    with open(presentation_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return content

@app.route('/download/<session_id>/pptx')
def download_pptx(session_id):
    pptx_file = os.path.join(app.config['PRESENTATIONS_FOLDER'], session_id, 'presentation.pptx')
    
    if not os.path.exists(pptx_file):
        return render_template('error.html', message='PPTX 파일을 찾을 수 없습니다.')
        
    return send_file(pptx_file, as_attachment=True, download_name='seo_audit_report.pptx')

@app.route('/download/<session_id>/pdf')
def download_pdf(session_id):
    pdf_file = os.path.join(app.config['PRESENTATIONS_FOLDER'], session_id, 'presentation.pdf')
    
    if not os.path.exists(pdf_file):
        return render_template('error.html', message='PDF 파일을 찾을 수 없습니다.')
        
    return send_file(pdf_file, as_attachment=True, download_name='seo_audit_report.pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
