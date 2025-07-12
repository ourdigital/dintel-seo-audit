try:
    from src.presentation.presentation_designer import PresentationDesigner
except ImportError as e:
    print(f"Warning: PresentationDesigner import failed: {e}")
    # Create a mock PresentationDesigner for graceful degradation
    class PresentationDesigner:
        def __init__(self, report_data):
            self.report_data = report_data
            print("Using mock PresentationDesigner - PDF generation will be limited")
        
        def generate_charts(self, output_dir):
            print("Charts generation not available")
            return {}
        
        def generate_presentation_html(self, charts, output_file):
            # Create a basic HTML file
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><title>SEO Report</title></head>
            <body>
                <h1>{self.report_data.get('title', 'SEO Report')}</h1>
                <p>Presentation generation is limited due to missing dependencies.</p>
                <p>Please install required system libraries for full functionality.</p>
            </body>
            </html>
            """
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return output_file
        
        def generate_pptx(self, charts, output_file):
            print("PPTX generation not available")
            return None
        
        def generate_pdf(self, html_file, output_file):
            print("PDF generation not available")
            return None
