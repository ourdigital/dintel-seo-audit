import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    데이터베이스 초기화 함수
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    with app.app_context():
        db.create_all()
        print("데이터베이스가 초기화되었습니다.")

if __name__ == "__main__":
    from src.main import app
    init_db(app)
