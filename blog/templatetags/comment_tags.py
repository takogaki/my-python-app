from django import template

register = template.Library()

@register.inclusion_tag('blog/render_comments.html')
def render_comment_tree(comment):
    """
    再帰的にコメントツリーを描画するテンプレートタグ
    """
    return {'comment': comment}