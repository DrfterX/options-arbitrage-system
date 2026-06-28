"""Blog 路由 Blueprint。"""

from flask import Blueprint, render_template

blog_bp = Blueprint("blog", __name__, url_prefix="/blog")


@blog_bp.route("")
def blog_index():
    return render_template("blog_index.html")


@blog_bp.route("/n-structure-practical")
def article_n_structure():
    return render_template("blog_post.html")


@blog_bp.route("/options-iv-analysis")
def article_iv():
    return render_template("blog_post_iv.html")


@blog_bp.route("/multi-timeframe-signals")
def article_mtf():
    return render_template("blog_post_mtf.html")


@blog_bp.route("/iv-n-structure-combined")
def article_iv_nstructure():
    return render_template("blog_post_iv_nstructure.html")


@blog_bp.route("/options-strategies")
def article_options_strategies():
    return render_template("blog_post_options_strategies.html")


@blog_bp.route("/product-intro")
def article_intro():
    return render_template("blog_post_intro.html")


@blog_bp.route("/n-structure-engine-deepdive")
def article_engine_deepdive():
    return render_template("blog_post_engine_deepdive.html")


@blog_bp.route("/ru2609-case-study")
def article_ru2609():
    return render_template("blog_post_ru2609.html")
