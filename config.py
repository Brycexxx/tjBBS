import os

class Config:
    SECRET_KEY = 'GrpopNaV2RPExg3SIPSdQtj1EFoR7sbQ'
    UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/")
    FC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/users/")
    POST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/posts/")
    IMAGE_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    PER_PAGE = 5
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    TJ_MAIL_SUBJECT_PREFIX = '同济生活小助手'
    TJ_MAIL_SENDER = os.getenv('TJ_MAIL_SENDER')
    TJ_ADMIN = os.getenv('TJ_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    FLASK_DB_QUERY_TIMEOUT = 0.5
    SSL_DISABLE = True
    APP_ID = "11377112"
    API_KEY = 'AlBNp0uGpHhut87Am7O3QtAi'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    URL = "localhost:5000"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/depAssistant"

class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/testAssistant"

class ProductionConfig(Config):
    DEBUG = True
    URL = "120.79.239.130:2048"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@120.79.239.130:3306/proAssistant"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr=cls.TJ_MAIL_SENDER,
                toaddrs=[cls.TJ_ADMIN],
                subject=cls.TJ_MAIL_SUBJECT_PREFIX + ' Application Error',
                credentials=credentials,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

class AliyunConfig(ProductionConfig):
    SSL_DISABLE = bool(os.getenv('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'aliyun': AliyunConfig,

    'default': DevelopmentConfig
}