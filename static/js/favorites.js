/**
 * お気に入りページ専用のJavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    loadFavorites();
});

/**
 * お気に入り車両を読み込んで表示する
 */
async function loadFavorites() {
    const container = document.getElementById('favorites-container');
    const noResults = document.getElementById('no-favorites-message');
    const countDisplay = document.getElementById('result-count-display');

    if (!container) return;

    // ローカルストレージからお気に入りIDを取得
    let favorites = JSON.parse(localStorage.getItem('carFavorites')) || [];

    if (favorites.length === 0) {
        container.innerHTML = '';
        if (noResults) noResults.style.display = 'block';
        if (countDisplay) countDisplay.textContent = '(0台)';
        return;
    }

    // 最大9件に制限
    const topFavorites = favorites.slice(0, 9);
    if (countDisplay) countDisplay.textContent = `(${topFavorites.length}台)`;

    try {
        // APIでお気に入り車両の詳細を一括取得
        const response = await fetch('/api/cars/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: topFavorites })
        });

        if (!response.ok) throw new Error('Failed to fetch favorites');

        const cars = await response.json();

        // ローディング表示を消去
        container.innerHTML = '';

        if (cars.length === 0) {
            if (noResults) noResults.style.display = 'block';
            return;
        }

        // 車両カードを生成して追加
        cars.forEach(car => {
            const card = createFavoriteCarCard(car);
            container.appendChild(card);
        });

        // script.jsのお気に入りボタン等の再設定
        if (typeof setupFavorites === 'function') {
            setupFavorites();
        }

        // お気に入りページで解除された場合に画面から消すためのイベントリスナー追加
        setupFavoritesRemovalListener();

    } catch (error) {
        console.error('Error loading favorites:', error);
        container.innerHTML = '<p class="error-message">データの読み込みに失敗しました。</p>';
    }
}

/**
 * お気に入りページ用の車両カード生成
 * script.js / hybrid.js のロジックを統合し、詳細な情報を表示
 */
function createFavoriteCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    card.setAttribute('data-car-id', car.id);

    // 価格整形
    const priceRange = typeof formatCurrency === 'function' ? formatCurrency(car['価格帯(万円)']) : car['価格帯(万円)'];
    const fuelEconomy = car['燃費(km/L)'] || '未定';

    card.innerHTML = `
        <div class="car-header">
            <h3>${car['メーカー']} ${car['車種']}</h3>
        </div>
        <div class="car-body">
            <div class="car-info">
                <div class="info-row">
                    <div class="info-item">
                        <span class="label"><i class="fas fa-car-side"></i> タイプ:</span>
                        <span class="value">${car['ボディタイプ'] || '未定'}</span>
                    </div>
                    <div class="info-item">
                        <span class="label"><i class="fas fa-cog"></i> 駆動:</span>
                        <span class="value">${car['駆動方式'] || '未定'}</span>
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-item">
                        <span class="label"><i class="fas fa-yen-sign"></i> 価格帯:</span>
                        <span class="value highlight">${priceRange}万円</span>
                    </div>
                    <div class="info-item">
                        <span class="label"><i class="fas fa-gas-pump"></i> 燃費:</span>
                        <span class="value">${fuelEconomy}km/L</span>
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-item">
                        <span class="label"><i class="fas fa-shield-alt"></i> 安全装備:</span>
                        <span class="value">${car['先進安全装備'] || '未定'}</span>
                    </div>
                    ${car['乗車定員'] ? `
                    <div class="info-item">
                        <span class="label"><i class="fas fa-users"></i> 定員:</span>
                        <span class="value">${car['乗車定員']}人</span>
                    </div>
                    ` : ''}
                </div>
                ${car.youtube_thumbnail ? `
                <a href="/car/${car.id}?tab=reviews" class="card-video-thumbnail">
                    <img src="${car.youtube_thumbnail}" alt="${car['メーカー']} ${car['車種']} レビュー動画">
                    <div class="video-play-badge"><i class="fab fa-youtube"></i> 動画</div>
                </a>
                ` : ''}
                ${!car.youtube_thumbnail ? `
                <div class="car-overview">
                    <img src="/static/images/car_placeholder.png" alt="${car['メーカー']} ${car['車種']}" style="width:100%; height:auto; border-radius:4px; margin-top:10px;">
                </div>
                ` : ''}
            </div>
            <div class="car-actions">
                <a href="/car/${car.id}" class="action-button"><i class="fas fa-info-circle"></i> 詳細</a>
                <button class="action-button secondary favorite-button favorited" data-car-id="${car.id}">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
        </div>
    `;

    return card;
}

/**
 * お気に入りページで「お気に入り済み」ボタンを押したときにカードを消す処理
 */
function setupFavoritesRemovalListener() {
    const container = document.getElementById('favorites-container');
    if (!container) return;

    container.addEventListener('click', function (e) {
        const btn = e.target.closest('.favorite-button');
        if (btn && btn.classList.contains('favorited')) {
            // script.jsのsetupFavoritesが先に動いてクラスが外れるのを待つか、
            // ここで独自にチェックする。script.jsは toggle なので、
            // favorited クラスがあれば解除（削除）の意味になる。
            const card = btn.closest('.car-card');
            if (card) {
                card.style.opacity = '0.5';
                card.style.pointerEvents = 'none';
                setTimeout(() => {
                    card.remove();
                    // 0件になったらメッセージ表示
                    if (container.children.length === 0) {
                        const noResults = document.getElementById('no-favorites-message');
                        if (noResults) noResults.style.display = 'block';
                        const countDisplay = document.getElementById('result-count-display');
                        if (countDisplay) countDisplay.textContent = '(0台)';
                    } else {
                        const countDisplay = document.getElementById('result-count-display');
                        if (countDisplay) countDisplay.textContent = `(${container.children.length}台)`;
                    }
                }, 300);
            }
        }
    });
}
