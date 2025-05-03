/**
 * AI自動車診断システム用JavaScriptファイル
 * フォーム操作、カードの並び替え、UIインタラクションなどを実装
 */

document.addEventListener('DOMContentLoaded', function() {
    // 検索フォームの処理
    setupSearchForm();
    
    // 車カードのイベント処理
    setupCarCards();
    
    // 並び替え機能の設定
    setupSorting();
    
    // お気に入り機能の設定
    setupFavorites();
});

/**
 * 検索フォームの設定
 */
function setupSearchForm() {
    const form = document.getElementById('car-filter-form');
    if (!form) return;
    
    // フォーム送信時の処理
    form.addEventListener('submit', function(event) {
        // ローディング表示などを追加できます
        console.log('フォームを送信しています...');
        
        // 入力の簡易バリデーション
        const maxPrice = document.getElementById('max-price');
        const minFuelEconomy = document.getElementById('min-fuel-economy');
        const minSeats = document.getElementById('min-seats');
        
        // すべての入力が有効かチェック
        let isValid = true;
        
        if (maxPrice && maxPrice.value !== "" && (isNaN(maxPrice.value) || maxPrice.value < 50 || maxPrice.value > 1000)) {
            showValidationError(maxPrice, '価格は50〜1000万円の範囲で入力してください');
            isValid = false;
        } else if (maxPrice) {
            clearValidationError(maxPrice);
        }
        
        if (minFuelEconomy && minFuelEconomy.value !== "" && (isNaN(minFuelEconomy.value) || minFuelEconomy.value < 5 || minFuelEconomy.value > 40)) {
            showValidationError(minFuelEconomy, '燃費は5〜40km/Lの範囲で入力してください');
            isValid = false;
        } else if (minFuelEconomy) {
            clearValidationError(minFuelEconomy);
        }
        
        if (minSeats && minSeats.value !== "" && (isNaN(minSeats.value) || minSeats.value < 2 || minSeats.value > 10)) {
            showValidationError(minSeats, '乗車定員は2〜10人の範囲で入力してください');
            isValid = false;
        } else if (minSeats) {
            clearValidationError(minSeats);
        }
        
        if (!isValid) {
            event.preventDefault(); // フォーム送信を中止
        }
    });
    
    // フォームリセットボタンの処理
    const resetButton = form.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
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
        card.addEventListener('click', function(event) {
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
    
    sortSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        const carContainer = document.getElementById('car-results');
        const cards = Array.from(carContainer.querySelectorAll('.car-card'));
        
        // 選択された条件に基づいてカードを並び替え
        cards.sort((a, b) => {
            switch (selectedValue) {
                case 'price-asc':
                    return parseFloat(a.dataset.price || 0) - parseFloat(b.dataset.price || 0);
                case 'price-desc':
                    return parseFloat(b.dataset.price || 0) - parseFloat(a.dataset.price || 0);
                case 'fuel-desc':
                    return parseFloat(b.dataset.fuel || 0) - parseFloat(a.dataset.fuel || 0);
                case 'recommended':
                default:
                    return parseFloat(b.dataset.score || 0) - parseFloat(a.dataset.score || 0);
            }
        });
        
        // DOMから一旦削除して、並び替え後に再追加
        cards.forEach(card => carContainer.removeChild(card));
        cards.forEach(card => carContainer.appendChild(card));
        
        // 並び替え後のアニメーション
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
        button.addEventListener('click', function(event) {
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
 * ページネーション機能 (将来的に実装予定)
 */
function setupPagination() {
    // TODO: ページネーション機能の実装
}

/**
 * レンジスライダーの値表示 (将来的に実装予定)
 */
function setupRangeSliders() {
    const priceSlider = document.getElementById('price-importance');
    const fuelSlider = document.getElementById('fuel-economy-importance');
    const sizeSlider = document.getElementById('size-importance');
    
    if (priceSlider) {
        priceSlider.addEventListener('input', function() {
            updateSliderValue(this, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
        });
        updateSliderValue(priceSlider, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
    }
    
    if (fuelSlider) {
        fuelSlider.addEventListener('input', function() {
            updateSliderValue(this, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
        });
        updateSliderValue(fuelSlider, ['とても低い', '低い', 'やや低め', '普通', 'やや高め', '高い', 'とても高い']);
    }
    
    if (sizeSlider) {
        sizeSlider.addEventListener('input', function() {
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