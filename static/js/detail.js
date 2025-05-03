// 詳細ページ用JavaScript
/**
 * 車両詳細ページ用JavaScript
 * AI自動車診断システム
 */

document.addEventListener('DOMContentLoaded', function() {
    // タブ機能の設定
    setupTabs();
    
    // お気に入りボタンの設定
    setupFavoriteButton();
    
    // 共有機能の設定
    setupShareButton();
    
    // 推薦スコアのアニメーション
    animateRecommendationScore();
    
    // レビュー関連の機能設定
    setupReviews();
});

/**
 * タブ切り替え機能の設定
 */
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // クリックされたタブをアクティブにする
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // 対応するコンテンツを表示する
            const tabId = button.getAttribute('data-tab');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId + '-tab') {
                    content.classList.add('active');
                }
            });
        });
    });
}

/**
 * お気に入りボタンの設定
 */
function setupFavoriteButton() {
    const favoriteButton = document.querySelector('.favorite-button');
    if (!favoriteButton) return;
    
    const carId = favoriteButton.getAttribute('data-car-id');
    
    // ローカルストレージからお気に入りリストを取得
    let favorites = JSON.parse(localStorage.getItem('carFavorites')) || [];
    
    // 初期状態の設定
    if (favorites.includes(carId)) {
        favoriteButton.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
        favoriteButton.classList.add('favorited');
    }
    
    // クリックイベント
    favoriteButton.addEventListener('click', function() {
        if (favorites.includes(carId)) {
            // お気に入りから削除
            favorites = favorites.filter(id => id !== carId);
            favoriteButton.innerHTML = '<i class="far fa-heart"></i> お気に入りに追加';
            favoriteButton.classList.remove('favorited');
        } else {
            // お気に入りに追加
            favorites.push(carId);
            favoriteButton.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
            favoriteButton.classList.add('favorited');
            
            // 追加時のアニメーション
            favoriteButton.classList.add('pulse');
            setTimeout(() => favoriteButton.classList.remove('pulse'), 300);
        }
        
        // ローカルストレージに保存
        localStorage.setItem('carFavorites', JSON.stringify(favorites));
    });
}

/**
 * 共有機能の設定
 */
function setupShareButton() {
    const shareButton = document.querySelector('.share-button');
    if (!shareButton) return;
    
    shareButton.addEventListener('click', function() {
        const url = window.location.href;
        const title = document.title;
        
        // Web Share APIが利用可能かチェック
        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            })
            .then(() => console.log('共有に成功しました'))
            .catch(error => console.log('共有に失敗しました', error));
        } else {
            // Web Share APIが利用できない場合はURLをクリップボードにコピー
            navigator.clipboard.writeText(url)
                .then(() => {
                    // 成功通知
                    const notification = document.createElement('div');
                    notification.textContent = 'URLをクリップボードにコピーしました';
                    notification.className = 'copy-notification';
                    document.body.appendChild(notification);
                    
                    // 2秒後に通知を消す
                    setTimeout(() => {
                        document.body.removeChild(notification);
                    }, 2000);
                })
                .catch(err => {
                    console.error('クリップボードへのコピーに失敗しました', err);
                });
        }
    });
}

/**
 * 推薦スコアのアニメーション
 */
function animateRecommendationScore() {
    const scoreElement = document.querySelector('.score-value');
    if (!scoreElement) return;
    
    // スコア値を取得
    const scoreValue = parseFloat(scoreElement.style.width) || 0;
    
    // 一旦0にしてからアニメーション
    scoreElement.style.width = '0%';
    
    setTimeout(() => {
        scoreElement.style.width = scoreValue + '%';
    }, 500);
}

/**
 * レビュー関連の機能設定
 */
function setupReviews() {
    const moreReviewsButton = document.querySelector('.more-reviews-button');
    if (!moreReviewsButton) return;
    
    // 現在表示しているレビュー数を追跡
    let displayedReviews = 3;
    const reviewsPerPage = 3;
    
    moreReviewsButton.addEventListener('click', function() {
        // 追加のレビューを読み込む処理
        // 実際の実装では、サーバーからAJAXで追加レビューを取得する
        loadMoreReviews(displayedReviews, reviewsPerPage);
        displayedReviews += reviewsPerPage;
    });
}

/**
 * 追加のレビューを読み込む
 * 注: 実際のアプリでは、サーバーからデータを取得する実装に置き換える
 */
function loadMoreReviews(start, count) {
    // このデモデータは実際の実装では使用しない
    const demoReviews = [
        {
            name: '鈴木さん',
            date: '2025年1月5日',
            rating: 4,
            content: '家族での使用に非常に適しています。特に広い室内空間が気に入っています。燃費も想定内で、満足しています。'
        },
        {
            name: '伊藤さん',
            date: '2024年12月20日',
            rating: 5,
            content: 'デザインに一目惚れして購入しましたが、機能性も抜群です。特に運転支援システムが充実していて、長距離ドライブでも疲れにくいです。'
        },
        {
            name: '高橋さん',
            date: '2024年11月15日',
            rating: 3,
            content: '全体的には満足していますが、後部座席の乗り心地がやや硬く感じます。都市部での運転は快適ですが、長距離では少し疲れます。'
        }
    ];
    
    // レビューリストの要素を取得
    const reviewList = document.querySelector('.review-list');
    
    // 追加のレビューが無い場合はボタンを非表示にする
    if (start >= demoReviews.length) {
        const moreReviewsButton = document.querySelector('.more-reviews-button');
        moreReviewsButton.style.display = 'none';
        return;
    }
    
    // 指定された数だけレビューを追加
    for (let i = start; i < start + count && i < demoReviews.length; i++) {
        const review = demoReviews[i];
        
        // レビュー要素を作成
        const reviewItem = document.createElement('div');
        reviewItem.className = 'review-item';
        
        // 星評価を生成
        let starsHTML = '';
        for (let s = 1; s <= 5; s++) {
            if (s <= review.rating) {
                starsHTML += '<i class="fas fa-star"></i>';
            } else {
                starsHTML += '<i class="far fa-star"></i>';
            }
        }
        
        // レビュー内容をHTMLとして設定
        reviewItem.innerHTML = `
            <div class="review-header">
                <div class="reviewer">
                    <i class="fas fa-user-circle"></i>
                    <span class="reviewer-name">${review.name}</span>
                </div>
                <div class="review-rating">
                    <div class="stars">
                        ${starsHTML}
                    </div>
                    <span class="review-date">${review.date}</span>
                </div>
            </div>
            <div class="review-content">
                <p>${review.content}</p>
            </div>
        `;
        
        // レビューリストに追加
        reviewList.appendChild(reviewItem);
        
        // フェードインアニメーション
        reviewItem.style.opacity = '0';
        reviewItem.style.transform = 'translateY(10px)';
        reviewItem.style.transition = 'opacity 0.5s, transform 0.5s';
        
        setTimeout(() => {
            reviewItem.style.opacity = '1';
            reviewItem.style.transform = 'translateY(0)';
        }, 50 * (i - start));
    }
}

/**
 * CSS用のスタイルを動的に追加
 */
(function addStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .copy-notification {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(44, 62, 80, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            z-index: 1000;
            animation: fadeInOut 2s forwards;
        }
        
        .pulse {
            animation: pulse 0.3s ease-in-out;
        }
        
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translate(-50%, 20px); }
            20% { opacity: 1; transform: translate(-50%, 0); }
            80% { opacity: 1; transform: translate(-50%, 0); }
            100% { opacity: 0; transform: translate(-50%, -20px); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
})();