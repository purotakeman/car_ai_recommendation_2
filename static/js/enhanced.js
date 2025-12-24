/**
 * enhanced.js - AI自動車推薦システム 拡張機能用JavaScript
 * 簡単診断機能、AJAX推薦、動的UI更新など
 */

// ========================================================================
// 診断機能とモード切り替え
// ========================================================================

// トグル処理は hybrid.js に統一

/**
 *  AI診断の実行
 */

function runDiagnosis() {
    // 回答の取得
    const purpose = document.querySelector('input[name="purpose"]:checked')?.value;
    const priority = document.querySelector('input[name="priority"]:checked')?.value;
    const budget = document.querySelector('input[name="budget_range"]:checked')?.value;

    // 入力検証
    if (!purpose || !priority || !budget) {
        showNotification('すべての質問にお答えください', 'warning');
        return;
    }

    // ローディング表示
    showLoading();

    // 診断結果に基づく推薦設定
    const preferences = {
        purpose: purpose,
        priority: priority,
        budget_range: budget,
        experience_level: 'beginner'
    };

    // 追加設定(プロファイルベース)
    applyProfileBasedSettings(preferences);

    // AJAXで推薦結果を取得
    fetch('/api/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            if (data.success) {
                displayDiagnosisResults(data.cars, data.user_profile);
                showNotification('AI診断が完了しました！', 'success');
            } else {
                console.error('診断エラー:', data.error);
                showNotification('診断中にエラーが発生しました。詳細検索をお試しください。', 'error');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('通信エラー:', error);
            showNotification('通信エラーが発生しました。詳細検索をお試しください。', 'error');
        });
}


/**
 * プロファイルに基づく追加設定を適用
 */
function applyProfileBasedSettings(preferences) {
    // 予算範囲を数値に変換
    const budgetMapping = {
        'low': { max: 200, min: 50 },
        'medium': { max: 400, min: 200 },
        'high': { max: 1000, min: 400 }
    };

    const budget = budgetMapping[preferences.budget_range];
    if (budget) {
        preferences.max_price = budget.max.toString();
    }

    // 用途に基づく設定
    switch (preferences.purpose) {
        case 'family':
            preferences.min_seats = '5';
            preferences.body_types = ['ミニバン', 'SUV', 'ハッチバック'];
            break;
        case 'commute':
            preferences.min_fuel_economy = '15';
            preferences.body_types = ['ハッチバック', '軽自動車', 'セダン'];
            break;
        case 'leisure':
            preferences.body_types = ['SUV', 'オープンカー', 'ハッチバック'];
            break;
        case 'business':
            preferences.body_types = ['セダン', 'SUV'];
            break;
    }

    // 優先事項に基づく設定
    switch (preferences.priority) {
        case 'economy':
            preferences.fuel_economy_importance = '0.8';
            preferences.price_importance = '0.7';
            break;
        case 'safety':
            preferences.fuel_types = ['ハイブリッド', 'EV'];
            break;
        case 'space':
            preferences.min_seats = '5';
            preferences.preferred_size = 'large';
            break;
        case 'performance':
            preferences.body_types = ['オープンカー', 'セダン'];
            break;
    }
}

// ========================================================================
// UI更新とアニメーション
// ========================================================================

/**
 * ローディング表示
 */
function showLoading() {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    if (loading) {
        loading.classList.add('active');
    }
    if (results) {
        results.style.display = 'none';
    }

    // ローディング位置にスクロール
    setTimeout(() => {
        loading?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

/**
 * ローディング非表示
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');

    if (loading) {
        loading.classList.remove('active');
    }
    if (results) {
        results.style.display = 'block';
    }
}

/**
 * 診断結果の表示
 */
function displayDiagnosisResults(cars, userProfile) {
    // 結果コンテナの取得
    const resultsContainer = document.getElementById('results');
    if (!resultsContainer) return;

    // 車両カードの更新
    updateCarResults(cars);

    // 推薦洞察の表示
    showRecommendationInsights(cars, userProfile);

    // 結果セクションにスクロール
    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 300);
}

/**
 * 車両カードの動的更新
 */
function updateCarResults(cars) {
    const carCardsContainer = document.getElementById('car-results');
    if (!carCardsContainer) return;

    // 既存カードをクリア
    carCardsContainer.innerHTML = '';

    // 新しいカードを生成
    cars.forEach((car, index) => {
        const carCard = createCarCard(car);
        carCard.style.opacity = '0';
        carCard.style.transform = 'translateY(20px)';
        carCardsContainer.appendChild(carCard);

        // アニメーション付きで表示
        setTimeout(() => {
            carCard.style.opacity = '1';
            carCard.style.transform = 'translateY(0)';
            carCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        }, index * 100);
    });

    // 結果数の更新
    updateResultCount(cars.length);

    // お気に入り機能の再設定
    setupFavoriteButtons();
}

/**
 * 車両カードの動的生成
 */
function createCarCard(car) {
    const cardElement = document.createElement('div');
    cardElement.className = 'car-card';
    cardElement.setAttribute('data-price', car['価格(万円)'] || 0);
    cardElement.setAttribute('data-fuel', car['燃費(km/L)'] || 0);
    cardElement.setAttribute('data-score', car['推薦スコア'] || 0);

    // 安全な値の取得
    const maker = car['メーカー'] || '';
    const model = car['車種'] || '';
    const price = car['価格(万円)'] || 0;
    const fuel = car['燃費(km/L)'] || '';
    const bodyType = car['ボディタイプ'] || '';
    const driveType = car['駆動方式'] || '';
    const fuelType = car['燃料の種類'] || '';
    const seats = car['乗車定員'] || '';
    const size = car['サイズ(mm)'] || '';
    const usedPrice = car['中古相場(万円)'] || '';
    const tax = car['自動車税(円)'] || '';
    const score = car['推薦スコア'] || '';
    const reason = car['推薦理由'] || '';
    const id = car['id'] || '';

    cardElement.innerHTML = `
        <div class="car-header">
            <h3>${maker} ${model}</h3>
            ${score ? `<div class="score-badge">
                <span class="score-value">${score}</span>
                <span class="score-label">点</span>
            </div>` : ''}
        </div>
        <div class="car-body">
            <div class="car-info">
                <div class="info-row">
                    <div class="info-item">
                        <span class="label"><i class="fas fa-car-side"></i> タイプ:</span>
                        <span class="value">${bodyType}</span>
                    </div>
                    <div class="info-item">
                        <span class="label"><i class="fas fa-cog"></i> 駆動:</span>
                        <span class="value">${driveType}</span>
                    </div>
                </div>
                <div class="info-row">
                    <div class="info-item">
                        <span class="label"><i class="fas fa-yen-sign"></i> 価格:</span>
                        <span class="value highlight">${(() => {
            let p = parseFloat(price.toString().replace(/,/g, ''));
            if (isNaN(p)) return price;
            if (p >= 100000) p = p / 10000;
            return p.toLocaleString();
        })()}万円</span>
                    </div>
                    ${fuel ? `<div class="info-item">
                        <span class="label"><i class="fas fa-gas-pump"></i> 燃費:</span>
                        <span class="value">${fuel}km/L</span>
                    </div>` : ''}
                </div>
                <div class="info-row">
                    ${fuelType ? `<div class="info-item">
                        <span class="label"><i class="fas fa-battery-half"></i> 燃料:</span>
                        <span class="value fuel-type-${fuelType}">${fuelType}</span>
                    </div>` : ''}
                    ${seats ? `<div class="info-item">
                        <span class="label"><i class="fas fa-users"></i> 定員:</span>
                        <span class="value">${seats}人</span>
                    </div>` : ''}
                </div>
                ${size ? `<div class="info-row">
                    <div class="info-item full-width">
                        <span class="label"><i class="fas fa-ruler-combined"></i> サイズ:</span>
                        <span class="value">${size}</span>
                    </div>
                </div>` : ''}
                ${usedPrice || tax ? `<div class="info-row">
                    ${usedPrice ? `<div class="info-item">
                        <span class="label"><i class="fas fa-recycle"></i> 中古相場:</span>
                        <span class="value">${usedPrice}万円</span>
                    </div>` : ''}
                    ${tax ? `<div class="info-item">
                        <span class="label"><i class="fas fa-receipt"></i> 税金:</span>
                        <span class="value">${formatCurrency(tax)}円/年</span>
                    </div>` : ''}
                </div>` : ''}
                ${reason ? `<div class="recommendation-reason">
                    <i class="fas fa-star"></i> ${reason}
                </div>` : ''}
            </div>
            <div class="car-actions">
                <a href="/car/${id}" class="action-button">
                    <i class="fas fa-info-circle"></i> 詳細
                </a>
                <button class="action-button secondary favorite-button" data-car-id="${id}">
                    <i class="far fa-heart"></i> お気に入り
                </button>
            </div>
        </div>
    `;

    return cardElement;
}

/**
 * 推薦洞察の表示
 */
function showRecommendationInsights(cars, userProfile) {
    // 既存の洞察セクションを削除
    const existingInsights = document.querySelector('.recommendation-insights');
    if (existingInsights) {
        existingInsights.remove();
    }

    // 新しい洞察セクションを作成
    const insightsHtml = `
        <div class="recommendation-insights">
            <h3><i class="fas fa-lightbulb"></i> AI分析結果</h3>
            <div class="insights-grid">
                <div class="insight-card">
                    <h4>あなたのタイプ</h4>
                    <p class="profile-type">${getProfileDisplayName(userProfile)}</p>
                    <small>選択された条件から判定</small>
                </div>
                <div class="insight-card">
                    <h4>検索結果</h4>
                    <p class="profile-type">${cars.length}台</p>
                    <small>条件に合致した車両数</small>
                </div>
                <div class="insight-card">
                    <h4>平均予算</h4>
                    <p class="budget-info">${calculateAveragePrice(cars)}万円</p>
                    <small>上位3台の平均価格</small>
                </div>
                ${cars.length > 0 && cars[0]['推薦理由'] ? `<div class="insight-card" style="grid-column: 1 / -1;">
                    <h4>1位の推薦理由</h4>
                    <p style="font-size: 0.9rem; text-align: left;">${cars[0]['推薦理由']}</p>
                </div>` : ''}
            </div>
        </div>
    `;

    // 結果セクションの前に挿入
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.insertAdjacentHTML('beforebegin', insightsHtml);

        // アニメーション効果
        const newInsights = document.querySelector('.recommendation-insights');
        if (newInsights) {
            newInsights.style.opacity = '0';
            newInsights.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                newInsights.style.opacity = '1';
                newInsights.style.transform = 'translateY(0)';
                newInsights.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            }, 100);
        }
    }
}

/**
 * 結果数の更新
 */
function updateResultCount(count) {
    const resultCount = document.querySelector('.result-count');
    if (resultCount) {
        resultCount.textContent = `(${count}台)`;

        // アニメーション効果
        resultCount.style.transform = 'scale(1.2)';
        setTimeout(() => {
            resultCount.style.transform = 'scale(1)';
            resultCount.style.transition = 'transform 0.3s ease';
        }, 200);
    }
}

// ========================================================================
// ユーティリティ関数
// ========================================================================

/**
 * プロファイル表示名の取得
 */
function getProfileDisplayName(profile) {
    const profileNames = {
        'family': 'ファミリー向け',
        'commuter': '通勤・実用重視',
        'luxury': '高級志向',
        'eco': 'エコ志向',
        'sporty': 'スポーツ志向',
        'general': 'バランス重視'
    };
    return profileNames[profile] || 'バランス重視';
}

/**
 * 平均価格の計算
 */
function calculateAveragePrice(cars) {
    if (!cars || cars.length === 0) return 0;

    const topThree = cars.slice(0, Math.min(3, cars.length));
    const total = topThree.reduce((sum, car) => {
        const price = parseFloat(car['価格(万円)'] || 0);
        return sum + price;
    }, 0);

    return Math.round(total / topThree.length);
}

/**
 * 通貨フォーマット
 */
function formatCurrency(value) {
    try {
        return parseInt(value).toLocaleString();
    } catch {
        return value;
    }
}

/**
 * 通知表示
 */
function showNotification(message, type = 'info') {
    // 既存の通知を削除
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // 新しい通知を作成
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    // スタイル設定
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: '10000',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        color: 'white',
        fontWeight: '500',
        maxWidth: '400px',
        opacity: '0',
        transform: 'translateX(100%)',
        transition: 'all 0.3s ease'
    });

    // タイプ別の色設定
    const colors = {
        'success': '#4CAF50',
        'error': '#f44336',
        'warning': '#ff9800',
        'info': '#2196F3'
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    // 通知スタイル
    const style = document.createElement('style');
    style.textContent = `
        .notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .notification-close {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 4px;
            padding: 5px;
            margin-left: auto;
        }
        .notification-close:hover {
            background: rgba(255,255,255,0.3);
        }
    `;
    document.head.appendChild(style);

    // DOMに追加
    document.body.appendChild(notification);

    // アニメーション
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);

    // 自動削除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

/**
 * 通知アイコンの取得
 */
function getNotificationIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * お気に入りボタンの再設定
 */
function setupFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.favorite-button');
    const favorites = JSON.parse(localStorage.getItem('carFavorites')) || [];

    favoriteButtons.forEach(button => {
        const carId = button.getAttribute('data-car-id');

        // 初期状態の設定
        if (favorites.includes(carId)) {
            button.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
            button.classList.add('favorited');
        } else {
            button.innerHTML = '<i class="far fa-heart"></i> お気に入り';
            button.classList.remove('favorited');
        }

        // 既存のイベントリスナーを削除（重複防止）
        button.replaceWith(button.cloneNode(true));

        // 新しいイベントリスナーを追加
        const newButton = document.querySelector(`[data-car-id="${carId}"]`);
        if (newButton) {
            newButton.addEventListener('click', function (event) {
                event.stopPropagation();
                toggleFavorite(carId, this);
            });
        }
    });
}

/**
 * お気に入りのトグル
 */
function toggleFavorite(carId, button) {
    let favorites = JSON.parse(localStorage.getItem('carFavorites')) || [];

    if (favorites.includes(carId)) {
        // お気に入りから削除
        favorites = favorites.filter(id => id !== carId);
        button.innerHTML = '<i class="far fa-heart"></i> お気に入り';
        button.classList.remove('favorited');
        showNotification('お気に入りから削除しました', 'info');
    } else {
        // お気に入りに追加
        favorites.push(carId);
        button.innerHTML = '<i class="fas fa-heart"></i> お気に入り済み';
        button.classList.add('favorited');
        showNotification('お気に入りに追加しました', 'success');

        // 追加時のアニメーション
        button.style.transform = 'scale(1.1)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
            button.style.transition = 'transform 0.3s ease';
        }, 200);
    }

    // ローカルストレージに保存
    localStorage.setItem('carFavorites', JSON.stringify(favorites));
}

// ========================================================================
// 初期化とイベントリスナー
// ========================================================================

/**
 * ページ読み込み時の初期化
 */
document.addEventListener('DOMContentLoaded', function () {
    // 初期表示の制御は hybrid.js に統一

    // 簡単診断モードを初期表示にする場合
    // toggleSearchMode();

    // お気に入り機能の初期設定
    setupFavoriteButtons();

    // ラジオボタンの選択時のアニメーション
    setupRadioAnimations();

    // 診断結果がある場合の自動スクロール
    if (document.querySelector('.recommendation-insights')) {
        setTimeout(() => {
            document.querySelector('.recommendation-insights')?.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 500);
    }
});

/**
 * ラジオボタンのアニメーション設定
 */
function setupRadioAnimations() {
    const radioLabels = document.querySelectorAll('.radio-group label');

    radioLabels.forEach(label => {
        label.addEventListener('click', function () {
            // 同じグループの他のラベルからselectedクラスを削除
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                const groupName = radio.name;
                document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                    r.closest('label')?.classList.remove('selected');
                });

                // クリックされたラベルにselectedクラスを追加
                this.classList.add('selected');

                // アニメーション効果
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                    this.style.transition = 'transform 0.2s ease';
                }, 100);
            }
        });
    });
}

// ========================================================================
// エラーハンドリング
// ========================================================================

/**
 * グローバルエラーハンドラー
 */
window.addEventListener('error', function (event) {
    console.error('JavaScript Error:', event.error);
    showNotification('予期しないエラーが発生しました', 'error');
});

/**
 * 未処理のPromise拒否のハンドラー
 */
window.addEventListener('unhandledrejection', function (event) {
    console.error('Unhandled Promise Rejection:', event.reason);
    showNotification('通信エラーが発生しました', 'error');
    event.preventDefault();
});

// グローバル関数として公開（HTMLから呼び出し可能にする）
// toggleSearchMode は hybrid.js が公開
window.runDiagnosis = runDiagnosis;