/**
 * DMM/DLsite 購入管理システム カスタムJavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // ツールチップの初期化（Bootstrapのツールチップ機能）
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 「戻るボタン」の動作
    const backButtons = document.querySelectorAll('.btn-back');
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.history.back();
        });
    });

    // 検索フォームのクリアボタン
    const clearSearchButtons = document.querySelectorAll('.clear-search');
    clearSearchButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            const inputs = form.querySelectorAll('input:not([type=submit]), select');
            inputs.forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });
            // フォームをリセット後に自動的に送信
            form.submit();
        });
    });

    // 商品検索用の自動補完機能（フェーズ2で実装予定）
    const productSearchInput = document.getElementById('product-search');
    if (productSearchInput) {
        productSearchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length < 2) return;
            
            // ここにAjaxリクエストの実装（フェーズ2）
            console.log('検索クエリ: ' + query);
            
        }, 300));
    }
    
    // 重複チェックのUI更新（フェーズ2で実装予定）
    const updateDuplicateCheckUI = function(results) {
        // フェーズ2で実装
        console.log('重複チェックの結果を更新');
    };
    
    // Bootstrapフォームバリデーションの初期化
    initFormValidation();
    
    // 購入履歴フォームの表示/非表示の初期化
    initPurchaseDetailsToggle();
});

/**
 * 連続したイベントの発火を防ぐためのdebounce関数
 */
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Bootstrapフォームバリデーションの初期化
 */
function initFormValidation() {
    'use strict';
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms)
        .forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
}

/**
 * 購入履歴フォームの表示/非表示切り替え
 */
function initPurchaseDetailsToggle() {
    const addPurchaseCheckbox = document.getElementById('add_purchase');
    const purchaseDetails = document.getElementById('purchase_details');
    
    if (addPurchaseCheckbox && purchaseDetails) {
        addPurchaseCheckbox.addEventListener('change', function() {
            purchaseDetails.style.display = this.checked ? 'block' : 'none';
        });
    }
}