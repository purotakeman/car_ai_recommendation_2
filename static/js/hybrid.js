/**
 * hybrid.js - ハイブリッド診断システム用JavaScript
 * 事実情報（選択肢）+ 嗜好情報（5段階評価）の制御
 */

// ========================================================================
// グローバル変数とデータ管理
// ========================================================================

let hybridDiagnosis = {
    currentStep: 1,
    totalSteps: 3,
    userData: {},
    stepValidation: {
        1: ['hybrid_purpose', 'hybrid_budget', 'hybrid_passengers'], // 事実情報
        2: ['hybrid_fuel_importance', 'hybrid_safety_importance', 'hybrid_design_importance',
            'hybrid_space_importance', 'hybrid_maintenance_importance'], // 嗜好情報
        3: [] // 結果表示（バリデーション不要）
    }
};

// ユーザープロファイル定義
const userProfiles = {
    family: {
        name: 'ファミリー重視タイプ',
        description: '家族での利用を最優先に考える方です。安全性と実用性、そして経済性のバランスを重視します。',
        recommendations: [
            '乗車定員が多く、荷物もたくさん積める車がおすすめ',
            '安全装備が充実したミニバンやSUVが最適',
            '燃費も考慮した経済的な選択を重視'
        ]
    },
    commuter: {
        name: '通勤・実用重視タイプ',
        description: '毎日の通勤や日常使いでの経済性を最重視する方です。燃費と維持費の安さを重要視します。',
        recommendations: [
            '燃費の良いハイブリッド車やコンパクトカーがおすすめ',
            '維持費が安い軽自動車も選択肢として有力',
            '駐車のしやすさも重要なポイント'
        ]
    },
    luxury: {
        name: '高級・品質重視タイプ',
        description: '品質の高さとブランド価値を重視する方です。デザインと快適性にこだわりがあります。',
        recommendations: [
            'プレミアムブランドのセダンやSUVがおすすめ',
            '上質な内装と先進的な装備を重視',
            '所有する喜びを感じられる車選び'
        ]
    },
    eco: {
        name: 'エコ・環境重視タイプ',
        description: '環境への配慮を最優先に考える方です。燃費性能と環境負荷の少なさを重要視します。',
        recommendations: [
            'ハイブリッド車や電気自動車がおすすめ',
            'CO2排出量の少ない車種を選択',
            '将来性を考えた環境に優しい車選び'
        ]
    },
    balance: {
        name: 'バランス重視タイプ',
        description: 'すべての要素をバランス良く考慮する方です。極端に偏らない安定した選択を好みます。',
        recommendations: [
            '価格・燃費・安全性がバランス良く揃った車がおすすめ',
            '主要メーカーの人気車種が安心',
            '長く愛用できる定番モデルを選択'
        ]
    }
};

// ========================================================================
// 初期化とイベントリスナー
// ========================================================================

document.addEventListener('DOMContentLoaded', function () {
    // ハイブリッド診断機能の初期化
    initializeHybridDiagnosis();
});

function initializeHybridDiagnosis() {
    // イベントリスナーの設定
    setupHybridEventListeners();

    // 初期状態の設定
    updateHybridProgress();
    updateHybridNavigation();

    // 初期モード設定（ハイブリッド診断を表示）
    showHybridDiagnosis();
}

function setupHybridEventListeners() {
    // 選択肢カード（事実情報）のイベント
    setupChoiceCardEvents();

    // 5段階評価（嗜好情報）のイベント
    setupRatingEvents();

    // ナビゲーションボタンのイベント
    setupHybridNavigationEvents();
}

// ========================================================================
// 選択肢カード（事実情報）のイベント処理
// ========================================================================

function setupChoiceCardEvents() {
    const choiceCards = document.querySelectorAll('.choice-card');

    choiceCards.forEach(card => {
        card.addEventListener('click', function () {
            const radio = this.querySelector('input[type="radio"]');
            if (!radio) return;

            const name = radio.name;
            const value = radio.value;

            // 同じグループの他の選択肢をクリア
            document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                input.closest('.choice-card').classList.remove('selected');
            });

            // 現在の選択肢を選択状態にする
            this.classList.add('selected');
            radio.checked = true;

            // アニメーション効果
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
                this.style.transition = 'transform 0.2s ease';
            }, 150);

            // データを保存
            hybridDiagnosis.userData[name] = value;

            // ナビゲーション状態を更新
            updateHybridNavigation();

            console.log(`選択更新: ${name} = ${value}`);
        });
    });
}

// ========================================================================
// 5段階評価（嗜好情報）のイベント処理
// ========================================================================

function setupRatingEvents() {
    const ratingOptions = document.querySelectorAll('.rating-option');

    ratingOptions.forEach(option => {
        option.addEventListener('click', function () {
            const radio = this.querySelector('input[type="radio"]');
            if (!radio) return;

            const name = radio.name;
            const value = parseInt(radio.value);

            // 同じグループの他の選択肢をクリア
            document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                input.closest('.rating-option').classList.remove('selected');
            });

            // 現在の選択肢を選択状態にする
            this.classList.add('selected');
            radio.checked = true;

            // アニメーション効果
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = '';
                this.style.transition = 'transform 0.2s ease';
            }, 150);

            // データを保存
            hybridDiagnosis.userData[name] = value;

            // ナビゲーション状態を更新
            updateHybridNavigation();

            console.log(`評価更新: ${name} = ${value}`);
        });
    });
}

// ========================================================================
// ナビゲーション処理
// ========================================================================

function setupHybridNavigationEvents() {
    // 次へボタンのイベントは関数で直接処理
    // 前へボタンのイベントは関数で直接処理
}

function nextHybridStep() {
    if (hybridDiagnosis.currentStep < hybridDiagnosis.totalSteps) {
        // 現在のステップのバリデーション
        if (!validateCurrentHybridStep()) {
            showHybridNotification('すべての質問にお答えください', 'warning');
            return;
        }

        // ステップ2から3に進む場合は診断結果を生成
        if (hybridDiagnosis.currentStep === 2) {
            generateHybridDiagnosisResult();
        }

        // ステップを進める
        moveToHybridStep(hybridDiagnosis.currentStep + 1);
    }
}

function previousHybridStep() {
    if (hybridDiagnosis.currentStep > 1) {
        moveToHybridStep(hybridDiagnosis.currentStep - 1);
    }
}

function moveToHybridStep(targetStep) {
    // 現在のステップを非表示
    const currentStepElement = document.getElementById(`diagnosis-step-${hybridDiagnosis.currentStep}`);
    if (currentStepElement) {
        currentStepElement.classList.remove('active');
    }

    // 新しいステップを表示
    hybridDiagnosis.currentStep = targetStep;
    const newStepElement = document.getElementById(`diagnosis-step-${hybridDiagnosis.currentStep}`);
    if (newStepElement) {
        newStepElement.classList.add('active');
    }

    // UI状態を更新
    updateHybridProgress();
    updateHybridNavigation();
    updateStepText();

    // スクロール位置を調整
    setTimeout(() => {
        document.getElementById('hybrid-diagnosis-mode').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }, 100);
}

// ========================================================================
// バリデーション
// ========================================================================

function validateCurrentHybridStep() {
    const requiredFields = hybridDiagnosis.stepValidation[hybridDiagnosis.currentStep];
    if (!requiredFields) return true;

    return requiredFields.every(fieldName => {
        const isAnswered = hybridDiagnosis.userData[fieldName] !== undefined;
        if (!isAnswered) {
            console.log(`未回答: ${fieldName}`);
        }
        return isAnswered;
    });
}

// ========================================================================
// UI状態更新
// ========================================================================

function updateHybridProgress() {
    const progressFill = document.getElementById('diagnosisProgressFill');
    const progress = (hybridDiagnosis.currentStep / hybridDiagnosis.totalSteps) * 100;

    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
}

function updateHybridNavigation() {
    const prevBtn = document.getElementById('hybridPrevBtn');
    const nextBtn = document.getElementById('hybridNextBtn');

    if (!prevBtn || !nextBtn) return;

    // 前へボタンの状態
    prevBtn.disabled = hybridDiagnosis.currentStep === 1;

    // 次へボタンの状態
    if (hybridDiagnosis.currentStep === hybridDiagnosis.totalSteps) {
        nextBtn.style.display = 'none';
    } else {
        nextBtn.style.display = 'flex';

        // 現在のステップの回答状況をチェック
        const isStepComplete = validateCurrentHybridStep();
        nextBtn.disabled = !isStepComplete;

        // ボタンテキストの更新
        if (hybridDiagnosis.currentStep === 2) {
            nextBtn.innerHTML = '<i class="fas fa-chart-line"></i> 診断結果を見る';
        } else {
            nextBtn.innerHTML = '次へ <i class="fas fa-chevron-right"></i>';
        }
    }
}

function updateStepText() {
    const currentStepText = document.getElementById('currentStepText');
    const stepCounter = document.getElementById('stepCounter');
    const totalSteps = document.getElementById('totalSteps');

    if (currentStepText) {
        const stepTexts = {
            1: '基本情報',
            2: '重視ポイント',
            3: '診断結果'
        };
        currentStepText.textContent = stepTexts[hybridDiagnosis.currentStep] || '診断中';
    }

    if (stepCounter) {
        stepCounter.textContent = hybridDiagnosis.currentStep;
    }

    if (totalSteps) {
        totalSteps.textContent = hybridDiagnosis.totalSteps;
    }
}

// ========================================================================
// 診断結果生成
// ========================================================================

function generateHybridDiagnosisResult() {
    console.log('診断結果生成開始:', hybridDiagnosis.userData);

    // ユーザープロファイルの分析
    const profileAnalysis = analyzeHybridUserProfile(hybridDiagnosis.userData);

    // 結果をUIに表示
    displayHybridDiagnosisResult(profileAnalysis);

    // グローバルに結果を保存（推薦実行時に使用）
    window.hybridDiagnosisResult = profileAnalysis;

    console.log('生成されたプロファイル:', profileAnalysis);
}

function analyzeHybridUserProfile(userData) {
    let profileScores = {
        family: 0,
        commuter: 0,
        luxury: 0,
        eco: 0,
        balance: 0
    };

    // ===== 事実情報による分析 =====

    // 用途による分析
    switch (userData.hybrid_purpose) {
        case 'family':
            profileScores.family += 40;
            profileScores.balance += 20;
            break;
        case 'commute':
            profileScores.commuter += 40;
            profileScores.eco += 20;
            break;
        case 'leisure':
            profileScores.luxury += 25;
            profileScores.balance += 15;
            break;
        case 'business':
            profileScores.luxury += 30;
            profileScores.balance += 20;
            break;
    }

    // 予算による分析
    switch (userData.hybrid_budget) {
        case 'low':
            profileScores.commuter += 30;
            profileScores.eco += 20;
            break;
        case 'medium':
            profileScores.balance += 30;
            profileScores.family += 20;
            break;
        case 'high':
            profileScores.luxury += 40;
            break;
    }

    // 乗車人数による分析
    switch (userData.hybrid_passengers) {
        case '1-2':
            profileScores.commuter += 20;
            profileScores.luxury += 15;
            break;
        case '3-4':
            profileScores.balance += 25;
            profileScores.family += 20;
            break;
        case '5+':
            profileScores.family += 40;
            break;
    }

    // ===== 嗜好情報による分析（5段階評価） =====

    // 燃費重要度
    const fuelImportance = userData.hybrid_fuel_importance || 3;
    if (fuelImportance >= 4) {
        profileScores.eco += 25;
        profileScores.commuter += 20;
    } else if (fuelImportance <= 2) {
        profileScores.luxury += 10;
    }

    // 安全性重要度
    const safetyImportance = userData.hybrid_safety_importance || 3;
    if (safetyImportance >= 4) {
        profileScores.family += 25;
        profileScores.balance += 15;
    }

    // デザイン重要度
    const designImportance = userData.hybrid_design_importance || 3;
    if (designImportance >= 4) {
        profileScores.luxury += 30;
    } else if (designImportance <= 2) {
        profileScores.commuter += 15;
    }

    // 室内空間重要度
    const spaceImportance = userData.hybrid_space_importance || 3;
    if (spaceImportance >= 4) {
        profileScores.family += 25;
    } else if (spaceImportance <= 2) {
        profileScores.commuter += 15;
        profileScores.luxury += 10;
    }

    // 維持費重要度
    const maintenanceImportance = userData.hybrid_maintenance_importance || 3;
    if (maintenanceImportance >= 4) {
        profileScores.commuter += 25;
        profileScores.eco += 15;
    } else if (maintenanceImportance <= 2) {
        profileScores.luxury += 15;
    }

    // 最も高いスコアのプロファイルを選択
    const topProfile = Object.keys(profileScores).reduce((a, b) =>
        profileScores[a] > profileScores[b] ? a : b
    );

    // 最低しきい値チェック（40点以上で確定）
    const finalProfile = profileScores[topProfile] >= 40 ? topProfile : 'balance';

    return {
        type: finalProfile,
        score: profileScores[finalProfile],
        allScores: profileScores,
        userData: userData
    };
}

function displayHybridDiagnosisResult(profileAnalysis) {
    const profile = userProfiles[profileAnalysis.type];

    // プロファイルタイプを表示
    const profileTypeText = document.getElementById('profileTypeText');
    if (profileTypeText) {
        profileTypeText.textContent = profile.name;
    }

    // プロファイル説明を表示
    const profileDescriptionText = document.getElementById('profileDescriptionText');
    if (profileDescriptionText) {
        profileDescriptionText.textContent = profile.description;
    }

    // 推薦理由を表示
    const profileRecommendations = document.getElementById('profileRecommendations');
    if (profileRecommendations) {
        const recommendationHTML = profile.recommendations
            .map(rec => `<div class="recommendation-item"><i class="fas fa-check-circle"></i> ${rec}</div>`)
            .join('');
        profileRecommendations.innerHTML = recommendationHTML;
    }

    // グローバルに結果を保存（推薦実行時に使用）
    window.hybridDiagnosisResult = profileAnalysis;
}

// ========================================================================
// 推薦実行
// ========================================================================

function executeHybridDiagnosis() {
    console.log('executeHybridDiagnosis 開始');
    console.log('hybridDiagnosisResult:', window.hybridDiagnosisResult);
    console.log('hybridDiagnosis.userData:', hybridDiagnosis.userData);

    // 診断結果が存在しない場合は再生成
    if (!window.hybridDiagnosisResult) {
        console.log('診断結果を再生成します');
        generateHybridDiagnosisResult();
    }

    if (!window.hybridDiagnosisResult) {
        console.error('診断データが見つかりません');
        showHybridNotification('診断データが見つかりません。最初からやり直してください。', 'error');
        return;
    }

    // ローディング表示
    showLoading();

    try {
        // ハイブリッド診断データを従来のAPIに合わせて変換
        console.log('API変換開始');
        console.log('hybridDiagnosisResult:', window.hybridDiagnosisResult);

        if (!window.hybridDiagnosisResult || !window.hybridDiagnosisResult.userData) {
            throw new Error('診断データが不完全です');
        }

        const apiPreferences = convertHybridDataToAPI(window.hybridDiagnosisResult);
        console.log('API変換結果:', apiPreferences);

        // 既存の推薦APIを呼び出し
        fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiPreferences)
        })
            .then(response => {
                console.log('API応答:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API結果:', data);
                hideLoading();
                if (data.success) {
                    displayDiagnosisResults(data.cars, data.user_profile);
                    showHybridNotification('ハイブリッド診断が完了しました！', 'success');

                    // 診断モードを非表示にして結果を表示
                    const hybridMode = document.getElementById('hybrid-diagnosis-mode');
                    if (hybridMode) {
                        hybridMode.style.display = 'none';
                    }
                } else {
                    console.error('診断エラー:', data.error);
                    showHybridNotification(`診断中にエラーが発生しました: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('通信エラー:', error);
                showHybridNotification(`通信エラーが発生しました: ${error.message}`, 'error');
            });
    } catch (error) {
        hideLoading();
        console.error('診断実行エラー:', error);
        showHybridNotification('エラーが発生しました。', 'error');
    }
}

function convertHybridDataToAPI(hybridResult) {
    try {
        console.log('convertHybridDataToAPI 開始:', hybridResult);

        if (!hybridResult || !hybridResult.userData || !hybridResult.type) {
            throw new Error('診断データが不完全です');
        }

        const userData = hybridResult.userData;
        const profileType = hybridResult.type;

        // 基本設定
        let apiData = {
            // ユーザープロファイル情報
            user_profile: profileType,
            purpose: userData.hybrid_purpose,
            experience_level: 'beginner', // ハイブリッド診断は初心者向け

            // 重要度設定（5段階評価を0-1の範囲に変換）
            fuel_economy_importance: (userData.hybrid_fuel_importance || 3) / 5,
            safety_importance: (userData.hybrid_safety_importance || 3) / 5,
            design_importance: (userData.hybrid_design_importance || 3) / 5,
            space_importance: (userData.hybrid_space_importance || 3) / 5,
            maintenance_importance: (userData.hybrid_maintenance_importance || 3) / 5,

            // 基本設定をプロファイル別に調整
            price_importance: 0.3, // デフォルト値
        };

        // 予算設定
        switch (userData.hybrid_budget) {
            case 'low':
                apiData.max_price = '200';
                apiData.price_importance = 0.8;
                break;
            case 'medium':
                apiData.max_price = '500';
                apiData.price_importance = 0.5;
                break;
            case 'high':
                apiData.max_price = '1000';
                apiData.price_importance = 0.2;
                break;
        }

        // 乗車人数設定
        switch (userData.hybrid_passengers) {
            case '1-2':
                apiData.min_seats = '2';
                apiData.preferred_size = 'small';
                break;
            case '3-4':
                apiData.min_seats = '4';
                apiData.preferred_size = 'medium';
                break;
            case '5+':
                apiData.min_seats = '5';
                apiData.preferred_size = 'large';
                break;
        }

        // プロファイル別の追加設定
        switch (profileType) {
            case 'family':
                apiData.body_types = ['ミニバン', 'SUV', 'ハッチバック'];
                apiData.fuel_types = ['(HEV)', 'レギュラー', 'ハイオク'];
                break;
            case 'commuter':
                apiData.body_types = ['ハッチバック', '軽自動車', 'セダン'];
                apiData.fuel_types = ['(HEV)', '電気(BEV)', 'レギュラー'];
                apiData.min_fuel_economy = '15';
                break;
            case 'luxury':
                apiData.body_types = ['セダン', 'SUV', 'オープンカー'];
                apiData.fuel_types = ['ハイオク', '(HEV)', '(PHEV)', 'ディーゼル'];
                break;
            case 'eco':
                apiData.fuel_types = ['(HEV)', '電気(BEV)', '(PHEV)', '水素'];
                apiData.min_fuel_economy = '20';
                break;
            case 'balance':
                // バランス型は特に制限を設けない
                break;
        }

        console.log('API変換結果:', apiData);
        return apiData;

    } catch (error) {
        console.error('convertHybridDataToAPI エラー:', error);
        throw error;
    }
}

// ========================================================================
// モード切り替え
// ========================================================================

function toggleSearchMode() {
    const mode = sessionStorage.getItem('searchMode');

    if (mode === 'detailed') {
        // 現在詳細検索なら、ハイブリッド診断を表示
        showHybridDiagnosis();
    } else {
        // 現在ハイブリッド（または初期）なら、詳細検索を表示
        showDetailedSearch();
    }
}

function showHybridDiagnosis() {
    const hybridMode = document.getElementById('hybrid-diagnosis-mode');
    const detailForm = document.getElementById('car-filter-form');
    const modeToggleButton = document.querySelector('.mode-toggle-button');

    if (hybridMode) hybridMode.style.display = 'block';
    if (detailForm) detailForm.style.display = 'none';
    if (modeToggleButton) {
        modeToggleButton.innerHTML = '<i class="fas fa-sliders-h"></i> 詳細検索に切り替え';
    }

    // セッションストレージにモードを保存
    sessionStorage.setItem('searchMode', 'hybrid');

    // スクロール位置を調整
    setTimeout(() => {
        hybridMode?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function showDetailedSearch() {
    const hybridMode = document.getElementById('hybrid-diagnosis-mode');
    const detailForm = document.getElementById('car-filter-form');
    const modeToggleButton = document.querySelector('.mode-toggle-button');
    const resultsSection = document.getElementById('results');

    if (hybridMode) hybridMode.style.display = 'none';
    if (detailForm) detailForm.style.display = 'block';

    // 詳細検索に切り替える際は、既存の診断結果（もしあれば）をリセットして良いか検討
    // ユーザーは「詳細検索画面に戻りたい」と言っているので、結果エリアを一度隠す
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }

    if (modeToggleButton) {
        modeToggleButton.innerHTML = '<i class="fas fa-brain"></i> スマート診断に戻る';
    }

    // セッションストレージにモードを保存
    sessionStorage.setItem('searchMode', 'detailed');

    // スクロール位置を調整
    setTimeout(() => {
        detailForm?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// ========================================================================
// 通知システム
// ========================================================================

function showHybridNotification(message, type = 'info') {
    // 既存の通知関数があればそれを使用、なければ簡易実装
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        // 簡易通知実装
        console.log(`[${type.toUpperCase()}] ${message}`);
        alert(message);
    }
}

// ========================================================================
// 診断結果表示
// ========================================================================

function displayDiagnosisResults(cars, userProfile) {
    // 結果表示エリアを取得
    const resultsSection = document.getElementById('results');
    if (!resultsSection) {
        console.error('結果表示エリアが見つかりません');
        return;
    }

    // 結果エリアを表示
    resultsSection.style.display = 'block';

    if (cars && cars.length > 0) {
        // 車両カードを生成
        const carsHTML = cars.map(car => {
            const priceRange = (() => {
                const parts = car['価格帯(万円)'].toString().split(/[~～]/);
                const formatted = parts.map(part => {
                    let v = parseFloat(part.replace(/,/g, ''));
                    if (isNaN(v)) return part;
                    if (v >= 100000) v = v / 10000;
                    return v.toLocaleString();
                });
                return formatted.join('～');
            })();

            const fuelEconomy = car['燃費(km/L)'] || '未定';
            const safetyEquipment = car['先進安全装備'] || '未定';
            const recommendationScore = car['推薦スコア'] || 0;
            const recommendationReason = car['推薦理由'] || '';

            return `
                <div class="car-card" data-car-id="${car.id}" data-price="${car['価格帯(万円)']}" data-fuel="${fuelEconomy}" data-score="${recommendationScore}">
                    <div class="car-header">
                        <h3>${car['メーカー']} ${car['車種']}</h3>
                        ${recommendationScore > 0 ? `
                        <div class="score-badge">
                            <span class="score-value">${recommendationScore}</span>
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
                                    <span class="value">${safetyEquipment}</span>
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
                        </div>
                        <div class="car-actions">
                            <a href="/car/${car.id}" class="action-button"><i class="fas fa-info-circle"></i> 詳細</a>
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
                </div>
            `;
        }).join('');

        // 表示の更新 (results全体を破壊せず、各要素を個別に更新)
        const titleDisplay = document.getElementById('result-title');
        if (titleDisplay) titleDisplay.textContent = '診断結果';

        const countDisplay = document.getElementById('result-count-display');
        if (countDisplay) {
            countDisplay.textContent = `(${cars.length}台)`;
        }

        const carContainer = document.getElementById('car-results');
        if (carContainer) {
            carContainer.innerHTML = carsHTML;
        }

        // 検索結果がない場合のメッセージを隠す
        const noResults = document.getElementById('no-results-message');
        if (noResults) noResults.style.display = 'none';

        // ページネーションを非表示にする (スマート診断は1ページのみ)
        const paginationContainer = document.getElementById('pagination-container');
        if (paginationContainer) {
            paginationContainer.style.display = 'none';
        }

        // 並び替えオプションを調整 (推薦順を追加/選択)
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            let optRecommended = sortSelect.querySelector('option[value="recommended"]');
            if (!optRecommended) {
                optRecommended = document.createElement('option');
                optRecommended.value = 'recommended';
                optRecommended.textContent = '推薦順';
                sortSelect.insertBefore(optRecommended, sortSelect.firstChild);
            }
            sortSelect.value = 'recommended';
        }

        // 各種ユーティリティの再実行
        if (typeof setupFavorites === 'function') setupFavorites();
        if (typeof animateCards === 'function') animateCards();
        if (typeof setupCarCards === 'function') setupCarCards();

        // スクロール
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

    } else {
        // 結果が0件の場合
        const carContainer = document.getElementById('car-results');
        if (carContainer) carContainer.innerHTML = '';

        const noResults = document.getElementById('no-results-message');
        if (noResults) noResults.style.display = 'flex';

        const paginationContainer = document.getElementById('pagination-container');
        if (paginationContainer) paginationContainer.style.display = 'none';

        const titleDisplay = document.getElementById('result-title');
        if (titleDisplay) titleDisplay.textContent = '検索結果';

        const countDisplay = document.getElementById('result-count-display');
        if (countDisplay) countDisplay.textContent = '(0台)';

        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
}

// ========================================================================
// ローディング表示
// ========================================================================

function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'flex';
        loading.classList.add('active'); // CSSの.activeにも対応

        // スピナーを確実に表示するための追加処理
        const spinner = loading.querySelector('.spinner');
        if (spinner) spinner.style.display = 'block';

        // ローディング位置にスクロール
        setTimeout(() => {
            loading.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 50);
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
        loading.classList.remove('active');
    }
}

// ========================================================================
// ユーティリティ関数
// ========================================================================

// ユーティリティ関数（script.jsに移行済み）

function resetHybridDiagnosis() {
    // データをリセット
    if (window.hybridDiagnosis) {
        hybridDiagnosis.currentStep = 1;
        hybridDiagnosis.userData = {};
    }
    window.hybridDiagnosisResult = null;

    // UI状態をリセット
    document.querySelectorAll('.choice-card.selected').forEach(card => {
        card.classList.remove('selected');
    });

    document.querySelectorAll('.rating-option.selected').forEach(option => {
        option.classList.remove('selected');
    });

    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.checked = false;
    });

    // 診断モードを表示し、結果を非表示にする
    const hybridMode = document.getElementById('hybrid-diagnosis-mode');
    const resultsSection = document.getElementById('results');

    if (hybridMode) {
        hybridMode.style.display = 'block';
    }
    if (resultsSection) {
        resultsSection.style.display = 'none';
        resultsSection.innerHTML = '';
    }

    // 最初のステップに戻る
    moveToHybridStep(1);

    // プログレスバーもリセット
    updateHybridProgress();

    console.log('ハイブリッド診断をリセットしました');
}

// ========================================================================
// デバッグ用関数
// ========================================================================

function debugHybridDiagnosis() {
    console.log('=== ハイブリッド診断デバッグ情報 ===');
    console.log('現在のステップ:', hybridDiagnosis.currentStep);
    console.log('ユーザーデータ:', hybridDiagnosis.userData);
    console.log('ステップバリデーション:', validateCurrentHybridStep());
    console.log('=====================================');
}

// グローバル関数として公開
window.nextHybridStep = nextHybridStep;
window.previousHybridStep = previousHybridStep;
window.executeHybridDiagnosis = executeHybridDiagnosis;
window.toggleSearchMode = toggleSearchMode;
window.resetHybridDiagnosis = resetHybridDiagnosis;
window.debugHybridDiagnosis = debugHybridDiagnosis;