/**
 * AI自動車診断システム用JavaScriptファイル
 * フォーム操作、カードの並び替え、UIインタラクションなどを実装
 */

document.addEventListener('DOMContentLoaded', function () {
    // 検索フォームの処理
    setupSearchForm();

    // 車カードのイベント処理
    setupCarCards();

    // 並び替え機能の設定
    setupSorting();

    // お気に入り機能の設定
    setupFavorites();

    // レンジスライダーの設定
    setupRangeSliders();

    // 初期表示時のモード設定
    initializeDisplayMode();
});

function initializeDisplayMode() {
    // セッションストレージからモードを判定
    const mode = sessionStorage.getItem('searchMode');

    if (mode === 'detailed') {
        // 詳細検索モードを表示
        showDetailedSearch();
    } else if (mode === 'hybrid') {
        // スマート診断モードを表示
        showHybridDiagnosis();
    } else {
        // デフォルトは詳細検索モードを表示
        showDetailedSearch();
    }
}

/**
 * 検索フォームの設定
 */
function setupSearchForm() {
    const form = document.getElementById('car-filter-form');
    if (!form) return;

    // フォーム送信時の処理
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        console.log('詳細検索を実行しています...');

        // 検索実行(1ページ目)
        executeSearch(1);
    });

    // フォームリセットボタンの処理
    const resetButton = form.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            // エラー表示をクリア
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => clearValidationError(input));

            console.log('フォームをリセットしました');
        });
    }
}

/**
 * バリデーションエラーを表示する
 */
function showValidationError(inputElement, message) {
    // 既存のエラーメッセージを削除
    clearValidationError(inputElement);

    // エラーメッセージ要素を作成
    const errorElement = document.createElement('div');
    errorElement.className = 'validation-error';
    errorElement.textContent = message;
    errorElement.style.color = '#e74c3c';
    errorElement.style.fontSize = '0.8rem';
    errorElement.style.marginTop = '5px';

    // 入力要素の後に挿入
    inputElement.parentNode.appendChild(errorElement);

    // 入力要素にエラースタイルを適用
    inputElement.style.borderColor = '#e74c3c';
}

/**
 * バリデーションエラーをクリアする
 */
function clearValidationError(inputElement) {
    // 兄弟要素のエラーメッセージを削除
    const parent = inputElement.parentNode;
    const errorElement = parent.querySelector('.validation-error');
    if (errorElement) {
        parent.removeChild(errorElement);
    }

    // 入力要素のエラースタイルをリセット
    inputElement.style.borderColor = '';
}

/**
 * 車カードの設定
 */
function setupCarCards() {
    const carCards = document.querySelectorAll('.car-card');

    carCards.forEach(card => {
        // カードクリック時のイベント
        card.addEventListener('click', function (event) {
            // お気に入りボタンや詳細ボタンのクリックはカード全体のクリックとして処理しない
            if (event.target.closest('.car-actions')) {
                return;
            }

            // カードの詳細情報ページへのリンク
            const detailsLink = card.querySelector('.action-button');
            if (detailsLink) {
                window.location.href = detailsLink.getAttribute('href');
            }
        });
    });
}

/**
 * 並び替え機能の設定
 */
function setupSorting() {
    const sortSelect = document.getElementById('sort-select');
    if (!sortSelect) return;

    sortSelect.addEventListener('change', function () {
        const selectedValue = this.value;
        const carContainer = document.getElementById('car-results');
        if (!carContainer) return;
        const cards = Array.from(carContainer.querySelectorAll('.car-card'));

        // 選択された条件に基づいてカードを並び替え
        cards.sort((a, b) => {
            // ヘルパー関数: 価格帯文字列から最小値・最大値を取得
            const getValue = (str, type) => {
                if (!str) return 0;
                const parts = str.toString().split(/[~～]/);
                const minVal = parseFloat(parts[0]) || 0;
                if (type === 'max' && parts.length > 1) {
                    return parseFloat(parts[1]) || minVal;
                }
                return minVal;
            };
            switch (selectedValue) {
                case 'recommended':
                    const scoreA = parseInt(a.dataset.score) || 0;
                    const scoreB = parseInt(b.dataset.score) || 0;
                    return scoreB - scoreA;
                case 'price-asc':
                    return getValue(a.dataset.price, 'min') - getValue(b.dataset.price, 'min');
                case 'price-desc':
                    return getValue(b.dataset.price, 'max') - getValue(a.dataset.price, 'max');
                case 'fuel-desc':
                    return getValue(b.dataset.fuel, 'max') - getValue(a.dataset.fuel, 'max');
                default:
                    return 0;
            }
        });

        cards.forEach(card => carContainer.appendChild(card));
        animateCards();
    });
}

/**
 * カードのアニメーション処理
 */
function animateCards() {
    const cards = document.querySelectorAll('.car-card');

    cards.forEach((card, index) => {
        // アニメーションをリセットして再適用
        card.style.animation = 'none';
        card.offsetHeight; // リフロー
        card.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s forwards`;
    });
}

/**
 * お気に入り機能の設定
 */
function setupFavorites() {
    const favoriteButtons = document.querySelectorAll('.favorite-button');

    // ローカルストレージからお気に入りリストを取得
    let favorites = JSON.parse(localStorage.getItem('carFavorites')) || [];

    favoriteButtons.forEach(button => {
        const carId = button.getAttribute('data-car-id');

        // 初期状態の設定
        if (favorites.includes(carId)) {
            button.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
            button.classList.add('favorited');
        }

        // クリックイベント
        button.addEventListener('click', function (event) {
            event.stopPropagation(); // カード全体のクリックイベントを停止

            if (favorites.includes(carId)) {
                // お気に入りから削除
                favorites = favorites.filter(id => id !== carId);
                button.innerHTML = '<i class="far fa-heart"></i> お気に入り';
                button.classList.remove('favorited');
            } else {
                // お気に入りに追加
                favorites.push(carId);
                button.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
                button.classList.add('favorited');

                // 追加時のアニメーション
                button.classList.add('pulse');
                setTimeout(() => button.classList.remove('pulse'), 300);
            }

            // ローカルストレージに保存
            localStorage.setItem('carFavorites', JSON.stringify(favorites));
        });
    });
}

/**
 * 検索の実行 (JSON APIを使用)
 */
function executeSearch(page = 1) {
    const form = document.getElementById('car-filter-form');
    if (!form) return;

    showLoading();

    // フォームデータからオブジェクト作成
    const formData = new FormData(form);
    const searchParams = {
        is_detailed_search: true,
        page: page,
        per_page: 12
    };

    // FormDataをプレーンオブジェクトに変換
    formData.forEach((value, key) => {
        if (!value) return; // 空の値はスキップ
        if (!searchParams[key]) {
            searchParams[key] = value;
        } else {
            if (!Array.isArray(searchParams[key])) {
                searchParams[key] = [searchParams[key]];
            }
            searchParams[key].push(value);
        }
    });

    console.log('APIリクエスト:', searchParams);

    fetch('/api/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySearchResults(data);
            } else {
                showNotification('検索エラー: ' + data.error, 'error');
            }
            hideLoading();
        })
        .catch(error => {
            console.error('API Error:', error);
            hideLoading();
            showNotification('通信エラーが発生しました', 'error');
        });
}

/**
 * 検索結果の表示
 */
function displaySearchResults(data) {
    const resultsArea = document.getElementById('results');
    const carContainer = document.getElementById('car-results');
    if (!resultsArea || !carContainer) return;

    // 結果エリアを表示
    resultsArea.style.display = 'block';

    // タイトルとカウント表示
    const titleDisplay = document.getElementById('result-title');
    if (titleDisplay) titleDisplay.textContent = '検索結果';

    const countDisplay = document.getElementById('result-count-display');
    if (countDisplay) {
        countDisplay.textContent = `(${data.total}台)`;
    }

    const noResults = document.getElementById('no-results-message');
    carContainer.innerHTML = '';

    if (data.cars.length === 0) {
        if (noResults) noResults.style.display = 'flex';
        updatePagination(1, 1);
        const countDisplay = document.getElementById('result-count-display');
        if (countDisplay) countDisplay.textContent = '(0台)';
        return;
    }

    if (noResults) noResults.style.display = 'none';

    data.cars.forEach(car => {
        const card = createCarCardElement(car, false); // 詳細検索なのでスコアは非表示
        carContainer.appendChild(card);
    });

    // 並び替え設定の調整 (詳細検索では推薦順オプションがないことを確認)
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        const optRecommended = sortSelect.querySelector('option[value="recommended"]');
        if (optRecommended) optRecommended.remove();
    }

    // ページネーション更新
    updatePagination(data.page, data.total_pages);

    // イベント再設定
    setupCarCards();
    setupFavorites();

    // スクロール
    resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // アニメーション
    animateCards();
}

/**
 * ページネーションUIの更新
 */
function updatePagination(currentPage, totalPages) {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    const container = document.getElementById('pagination-container');

    if (pageInfo) {
        pageInfo.textContent = `${currentPage} / ${totalPages}`;
    }

    if (prevBtn) {
        prevBtn.disabled = (currentPage <= 1);
        prevBtn.onclick = () => executeSearch(currentPage - 1);
    }

    if (nextBtn) {
        nextBtn.disabled = (currentPage >= totalPages);
        nextBtn.onclick = () => executeSearch(currentPage + 1);
    }

    if (container) {
        container.style.display = totalPages > 1 ? 'flex' : 'none';
    }
}

/**
 * 車両カード要素の作成
 */
function createCarCardElement(car, showScore = true) {
    const card = document.createElement('div');
    card.className = 'car-card';
    card.dataset.id = car.id;
    card.dataset.price = car['価格帯(万円)'] || '';
    card.dataset.fuel = car['燃費(km/L)'] || '';
    card.dataset.score = car['推薦スコア'] || 0;

    const formatPrice = (priceVal) => {
        if (!priceVal) return '未定';
        const parts = priceVal.toString().split(/[~～]/);
        const formattedParts = parts.map(part => {
            let v = parseFloat(part.replace(/,/g, '').replace('万円', '').replace('円', '').strip?.() || part);
            if (isNaN(v)) return part;
            if (v >= 100000) v = v / 10000;
            return v.toLocaleString();
        });
        return formattedParts.join('～') + '万円';
    };

    const priceDisplay = formatPrice(car['価格帯(万円)']);

    card.innerHTML = `
        <div class="car-header">
            <h3>${car['メーカー']} ${car['車種']}</h3>
            ${showScore && car['推薦スコア'] ? `
            <div class="score-badge">
                <span class="score-value">${car['推薦スコア']}</span>
                <span class="score-label">点</span>
            </div>
            ` : ''}
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
                        <span class="value highlight">${priceDisplay}</span>
                    </div>
                    <div class="info-item">
                        <span class="label"><i class="fas fa-gas-pump"></i> 燃費:</span>
                        <span class="value">${car['燃費(km/L)'] || '未定'}km/L</span>
                    </div>
                </div>
                ${car.youtube_thumbnail ? `
                <a href="/car/${car.id}?tab=reviews" class="card-video-thumbnail">
                    <img src="${car.youtube_thumbnail}" alt="${car['メーカー']} ${car['車種']} レビュー動画">
                    <div class="video-play-badge"><i class="fab fa-youtube"></i> 動画</div>
                </a>
                ` : ''}
            </div>
            <div class="car-actions">
                <a href="/car/${car.id}" class="action-button"><i class="fas fa-info-circle"></i>詳細</a>
                ${car.youtube_url ? `
                <a href="/car/${car.id}?tab=reviews" class="action-button youtube-button">
                    <i class="fab fa-youtube"></i> 動画
                </a>
                ` : ''}
                <button class="action-button secondary favorite-button" data-car-id="${car.id}">
                    <i class="far fa-heart"></i>
                </button>
            </div>
        </div>
    `;
    return card;
}

/**
 * レンジスライダーの値表示
 */
function setupRangeSliders() {
    const priceSlider = document.getElementById('price-importance');
    const fuelSlider = document.getElementById('fuel-economy-importance');
    const sizeSlider = document.getElementById('size-importance');

    if (priceSlider) {
        priceSlider.addEventListener('input', function () {
            updateSliderValue(this, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
        });
        updateSliderValue(priceSlider, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
    }

    if (fuelSlider) {
        fuelSlider.addEventListener('input', function () {
            updateSliderValue(this, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
        });
        updateSliderValue(fuelSlider, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
    }

    if (sizeSlider) {
        sizeSlider.addEventListener('input', function () {
            updateSliderValue(this, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
        });
        updateSliderValue(sizeSlider, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
    }
}

/**
 * スライダーの値を表示用テキストに変換する
 */
function updateSliderValue(slider, labels) {
    const value = parseFloat(slider.value);
    const index = Math.floor((value / (1 / (labels.length - 1))) + 0.5);
    const displayElement = slider.nextElementSibling;

    if (displayElement && displayElement.classList.contains('value-display')) {
        displayElement.textContent = labels[index];
    }
}

// ========================================================================
// ローディング表示と通知
// ========================================================================

function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'flex';
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

function showNotification(message, type = 'info') {
    // 簡易通知実装
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}
