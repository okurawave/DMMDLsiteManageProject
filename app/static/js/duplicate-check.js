/**
 * 重複チェック機能用スクリプト
 */

/**
 * 商品情報のレンダリング関数
 */
function renderProductDetails(product, platform) {
    if (!product) return '<div class="alert alert-warning">製品情報がありません</div>';
    
    const platformLabel = platform === 'dmm' ? 'DMM' : 'DLsite';
    
    let html = `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">${product.title}</h5>
                <div class="small text-muted mb-2">
                    ${platformLabel} ID: ${product.platform_id || '不明'}
                </div>
                <div class="mb-2">
                    <strong>価格:</strong> ¥${product.price || '不明'}
                </div>
                <div class="mb-2">
                    <strong>サークル/メーカー:</strong> ${product.maker || '不明'}
                </div>
                <div class="mb-2">
                    <strong>発売日:</strong> ${product.release_date || '不明'}
                </div>`;
    
    if (product.category) {
        html += `<div class="mb-2">
            <strong>カテゴリ:</strong> ${product.category}
        </div>`;
    }
    
    if (product.url) {
        html += `<div class="mt-3">
            <a href="${product.url}" target="_blank" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-external-link-alt"></i> ${platformLabel}で表示
            </a>
        </div>`;
    }
    
    html += `</div></div>`;
    
    // 価格履歴を取得するボタンを追加
    html += `<div class="text-center mb-3">
        <button class="btn btn-sm btn-info show-price-history" data-product-id="${product.id}">
            <i class="fas fa-chart-line"></i> 価格履歴を表示
        </button>
        <div id="price-history-${product.id}" class="mt-2" style="display:none;"></div>
    </div>`;
    
    return html;
}

/**
 * 比較結果のレンダリング関数
 */
function renderComparisonResult(comparison, product1, product2) {
    if (!comparison) return '<div class="alert alert-warning">比較データがありません</div>';
    
    let html = '<div class="card">';
    html += '<div class="card-body">';
    
    // タイトル類似度
    const titleSimilarity = comparison.title_similarity * 100;
    const similarityColor = titleSimilarity > 90 ? 'success' : (titleSimilarity > 70 ? 'primary' : 'secondary');
    
    /* cssLint ignore:start */
    html += `<h6>タイトル類似度</h6>
    <div class="progress mb-3" style="height: 20px;">
        <div class="progress-bar bg-${similarityColor}" role="progressbar" 
             style="width: ${titleSimilarity}%;" 
             aria-valuenow="${titleSimilarity}" 
             aria-valuemin="0" aria-valuemax="100">
            ${titleSimilarity.toFixed(1)}%
        </div>
    </div>`;
    /* cssLint ignore:end */
    
    // 高度な類似度（もしあれば）
    if (comparison.advanced_similarity !== null) {
        const advSimilarity = comparison.advanced_similarity * 100;
        /* cssLint ignore:start */
        html += `<h6>高度な類似度分析（TF-IDF）</h6>
        <div class="progress mb-3" style="height: 20px;">
            <div class="progress-bar bg-info" role="progressbar" 
                 style="width: ${advSimilarity}%;" 
                 aria-valuenow="${advSimilarity}" 
                 aria-valuemin="0" aria-valuemax="100">
                ${advSimilarity.toFixed(1)}%
            </div>
        </div>`;
        /* cssLint ignore:end */
    }
    
    // メーカー/サークル一致
    html += `<div class="mb-3">
        <h6>サークル/メーカー一致:</h6>
        <span class="badge bg-${comparison.maker_match ? 'success' : 'secondary'} p-2">
            ${comparison.maker_match ? '一致しています' : '一致していません'}
        </span>
    </div>`;
    
    // 価格比較
    if (comparison.price_difference !== null) {
        const diffAbs = Math.abs(comparison.price_difference);
        const diffPercent = comparison.price_diff_percentage.toFixed(1);
        const cheaper = comparison.price_difference > 0 ? product2.platform.toUpperCase() : product1.platform.toUpperCase();
        const diffColor = comparison.price_difference !== 0 ? (cheaper === 'DLSITE' ? 'success' : 'warning') : 'secondary';
        
        html += `<div class="mb-3">
            <h6>価格差:</h6>
            <div class="alert alert-${diffColor} mb-0">
                ${comparison.price_difference !== 0 
                    ? `${cheaper}の方が<strong>¥${diffAbs}</strong> (${diffPercent}%) 安いです` 
                    : '両方とも同じ価格です'}
            </div>
        </div>`;
    } else {
        html += `<div class="mb-3">
            <h6>価格差:</h6>
            <div class="alert alert-warning mb-0">
                片方または両方の価格が登録されていないため、比較できません
            </div>
        </div>`;
    }
    
    // 総合評価
    html += `<div class="mt-4">
        <h6>総合評価:</h6>
        <div class="alert alert-${comparison.is_same_product ? 'success' : 'info'} mb-0">
            ${comparison.is_same_product 
                ? '<i class="fas fa-check-circle"></i> <strong>高確率で同一作品です</strong>' 
                : '<i class="fas fa-question-circle"></i> <strong>類似していますが、同一作品とは言い切れません</strong>'}
        </div>
    </div>`;
    
    html += '</div></div>';
    
    return html;
}

/**
 * 重複チェック機能の初期化
 */
function initDuplicateCheck() {
    // 類似度閾値スライダーの値表示
    const thresholdSlider = document.getElementById('threshold');
    const thresholdValue = document.getElementById('threshold-value');
    if (thresholdSlider && thresholdValue) {
        thresholdSlider.addEventListener('input', function() {
            thresholdValue.textContent = this.value;
        });
    }
    
    // 重複チェックボタンの処理
    const form = document.getElementById('duplicate-settings-form');
    if (form) {
        form.addEventListener('submit', function() {
            document.getElementById('loading-indicator').style.display = 'block';
        });
    }
    
    // 詳細比較ボタンの処理
    document.querySelectorAll('.compare-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var dmmId = this.getAttribute('data-dmm-id');
            var dlsiteId = this.getAttribute('data-dlsite-id');
            
            // モーダル内の情報をクリア
            document.getElementById('dmm-product-details').innerHTML = 
                '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.getElementById('dlsite-product-details').innerHTML = 
                '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.getElementById('comparison-results').innerHTML = 
                '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            
            // モーダル表示
            var compareModal = new bootstrap.Modal(document.getElementById('compareModal'));
            compareModal.show();
            
            // API経由で商品比較データを取得
            fetch(`/api/compare_products?product1_id=${dmmId}&product2_id=${dlsiteId}`)
                .then(response => response.json())
                .then(data => {
                    // DMMの商品情報表示
                    const product1 = data.product1;
                    document.getElementById('dmm-product-details').innerHTML = 
                        renderProductDetails(product1, 'dmm');
                    
                    // DLsiteの商品情報表示
                    const product2 = data.product2;
                    document.getElementById('dlsite-product-details').innerHTML = 
                        renderProductDetails(product2, 'dlsite');
                    
                    // 比較結果表示
                    const comparison = data.comparison;
                    document.getElementById('comparison-results').innerHTML = 
                        renderComparisonResult(comparison, product1, product2);
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('dmm-product-details').innerHTML = 
                        '<div class="alert alert-danger">データ取得中にエラーが発生しました</div>';
                    document.getElementById('dlsite-product-details').innerHTML = 
                        '<div class="alert alert-danger">データ取得中にエラーが発生しました</div>';
                    document.getElementById('comparison-results').innerHTML = 
                        '<div class="alert alert-danger">データ取得中にエラーが発生しました</div>';
                });
        });
    });
    
    // 価格履歴表示ボタンの処理
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('show-price-history') || 
            e.target.parentElement.classList.contains('show-price-history')) {
                
            const button = e.target.classList.contains('show-price-history') 
                ? e.target 
                : e.target.parentElement;
            
            const productId = button.getAttribute('data-product-id');
            const historyContainer = document.getElementById(`price-history-${productId}`);
            
            if (historyContainer.style.display === 'none') {
                historyContainer.style.display = 'block';
                historyContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> 読み込み中...</div>';
                
                // 価格履歴データを取得
                fetch(`/api/price_history/${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.price_history && data.price_history.length > 0) {
                            let html = '<div class="card"><div class="card-body"><h6>価格履歴</h6><ul class="list-group">';
                            
                            data.price_history.forEach(item => {
                                const date = item.date || '不明';
                                const price = item.price || '不明';
                                const source = item.source === 'current' ? '現在価格' : '購入時価格';
                                
                                html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                                    <span>${date}</span>
                                    <span class="badge bg-primary rounded-pill">¥${price}</span>
                                    <span class="badge bg-secondary">${source}</span>
                                </li>`;
                            });
                            
                            html += '</ul></div></div>';
                            historyContainer.innerHTML = html;
                        } else {
                            historyContainer.innerHTML = '<div class="alert alert-info">価格履歴データがありません</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        historyContainer.innerHTML = '<div class="alert alert-danger">価格履歴の取得に失敗しました</div>';
                    });
                
                button.innerHTML = '<i class="fas fa-chart-line"></i> 価格履歴を隠す';
            } else {
                historyContainer.style.display = 'none';
                button.innerHTML = '<i class="fas fa-chart-line"></i> 価格履歴を表示';
            }
        }
    });
}

// メインのJavaScriptに重複チェック機能を登録
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.duplicate-check-page')) {
        initDuplicateCheck();
    }
});