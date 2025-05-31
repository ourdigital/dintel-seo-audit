from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pages = db.relationship('Page', backref='website', lazy=True, cascade="all, delete-orphan")
    technical_seo = db.relationship('TechnicalSEO', backref='website', lazy=True, uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Website {self.url}>'

class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.Text)
    meta_description = db.Column(db.Text)
    h1 = db.Column(db.Text)
    content = db.Column(db.Text)
    status_code = db.Column(db.Integer)
    content_type = db.Column(db.String(100))
    depth = db.Column(db.Integer, default=0)
    is_homepage = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    keywords = db.relationship('Keyword', backref='page', lazy=True, cascade="all, delete-orphan")
    links = db.relationship('Link', backref='page', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Page {self.url}>'

class Keyword(db.Model):
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)
    density = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Keyword {self.keyword}>'

class Link(db.Model):
    __tablename__ = 'links'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    is_internal = db.Column(db.Boolean, default=True)
    is_followed = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Link {self.url}>'

class TechnicalSEO(db.Model):
    __tablename__ = 'technical_seo'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False, unique=True)
    has_robots_txt = db.Column(db.Boolean, default=False)
    robots_txt_content = db.Column(db.Text)
    has_sitemap = db.Column(db.Boolean, default=False)
    sitemap_url = db.Column(db.String(255))
    sitemap_content = db.Column(db.Text)
    core_web_vitals = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TechnicalSEO for website_id {self.website_id}>'
