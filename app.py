from flask import Flask, render_template
from routes.composer_routes import composer_bp
from routes.library_routes import library_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(composer_bp)
    app.register_blueprint(library_bp)

    @app.route("/")
    def home():
        # Default page = combined Composer + Library
        return render_template("composer.html")

    # Helpful in dev so template changes reload automatically
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    return app


if __name__ == "__main__":
    app = create_app()
    # debug=True is fine for class projects / demo
    app.run(debug=True)
