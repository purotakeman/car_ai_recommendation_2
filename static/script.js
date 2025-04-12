document.addEventListener('DOMContentLoaded', function() {
    // チェックボックスの選択状態を保持する
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            //フォーム送信時にローディング表示などを追加できます
            console.log('フォームを送信しています...');
        });
    }

    // 車のカードにホバーエフェクトを追加
    const carCards =this.document.querySelectorAll('.car-card');
    carCards.forEach(card => {
        card.addEventListener('click', function() {
            // 将来的に詳細ビューを表示する機能など
            console.log('車の詳細:', this.querySelector('h3').textContent);
        });
    });
    // 価格スライダーの実装（将来的な機能）
        // const priceInput = document.querySelector('input[name="max_price"]');
        // if (priceInput) {
        //     const priceValue = document.createElement('span');
        //     priceValue.id = 'price-value';
        //     priceValue.textContent = priceInput.value + '万円';
        //     priceInput.parentNode.appendChild(priceValue);
        //     
        //     priceInput.addEventListener('input', function() {
        //         priceValue.textContent = this.value + '万円';
        //     });
        // }
});

