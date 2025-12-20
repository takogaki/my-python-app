function showReplyForm(commentId) {
    // すべての返信フォームを閉じる
    const allForms = document.querySelectorAll('.reply-form');
    allForms.forEach(form => form.style.display = 'none');

    // 指定された返信フォームを開く
    const form = document.getElementById('reply-form-' + commentId);
    if (form) {
        form.style.display = 'block';
    }
}