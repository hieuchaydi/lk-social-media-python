// Module quản lý bài viết
const PostModule = {
    init: function() {
        this.setupLikeHandlers();
        this.setupPostForms();
    },
    
    setupLikeHandlers: function() {
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.btn-like')) {
                const button = e.target.closest('.btn-like');
                const postId = button.dataset.postId;
                await this.handleLikePost(postId, button);
            }
        });
    },
    
    handleLikePost: async function(postId, button) {
        try {
            const response = await fetch(`/like_post/${postId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                button.classList.toggle('liked', data.action === 'liked');
                const likeCount = button.querySelector('.like-count') || 
                                 button.closest('.post-actions').querySelector('.like-count');
                if (likeCount) likeCount.textContent = data.likes_count;
                
                // Hiệu ứng visual
                if (data.action === 'liked') {
                    this.createLikeAnimation(button);
                }
            }
        } catch (error) {
            console.error('Like error:', error);
            Toast.show('Có lỗi khi thực hiện thao tác', 'error');
        }
    },
    
    createLikeAnimation: function(element) {
        const heart = document.createElement('div');
        heart.className = 'heart-animation';
        heart.innerHTML = '<i class="fas fa-heart"></i>';
        
        const container = element.closest('.post-actions') || element;
        container.appendChild(heart);
        
        setTimeout(() => heart.remove(), 1000);
    }
};

// Module quản lý bình luận
const CommentModule = {
    init: function() {
        this.setupCommentHandlers();
        this.setupReplyHandlers();
    },
    
    setupCommentHandlers: function() {
        // Xử lý like comment
        document.addEventListener('submit', async (e) => {
            if (e.target.classList.contains('like-comment-form')) {
                e.preventDefault();
                await this.handleLikeComment(e.target);
            }
        });
        
        // Xử lý gửi comment
        document.addEventListener('submit', async (e) => {
            if (e.target.classList.contains('comment-form')) {
                e.preventDefault();
                await this.handleNewComment(e.target);
            }
        });
    },
    
    handleLikeComment: async function(form) {
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new FormData(form)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                const likeBtn = form.querySelector('.btn-like-comment');
                const likeCount = form.querySelector('.like-count');
                
                if (likeBtn) likeBtn.classList.toggle('liked', data.action === 'liked');
                if (likeCount) likeCount.textContent = data.likes_count;
            }
        } catch (error) {
            console.error('Comment like error:', error);
        }
    },
    
    handleNewComment: async function(form) {
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: new FormData(form)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                form.reset();
                // Cập nhật UI với comment mới
                const commentsContainer = document.querySelector(data.comments_container || '.comments-list');
                if (commentsContainer && data.comment_html) {
                    commentsContainer.insertAdjacentHTML('beforeend', data.comment_html);
                }
            }
        } catch (error) {
            console.error('Comment error:', error);
        }
    }
};