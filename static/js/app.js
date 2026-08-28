document.addEventListener('DOMContentLoaded', () => {
    const inputArea = document.getElementById('inputArea');
    const outputArea = document.getElementById('outputArea');
    const spritesGrid = document.getElementById('spritesGrid');
    const statusText = document.getElementById('statusText');
    const statusTime = document.getElementById('statusTime');

    const btnEncrypt = document.getElementById('btnEncrypt');
    const btnDecrypt = document.getElementById('btnDecrypt');
    const btnSwap = document.getElementById('btnSwap');
    const btnCopy = document.getElementById('btnCopy');
    const btnClear = document.getElementById('btnClear');
    const btnToggleSprites = document.getElementById('btnToggleSprites');

    let currentTokens = [];
    let isSpriteView = false;

    function updateStatus(message, duration = 3000) {
        statusText.textContent = message;
        if (duration > 0) {
            setTimeout(() => {
                if (statusText.textContent === message) {
                    statusText.textContent = 'READY';
                }
            }, duration);
        }
    }

    function clearOutput() {
        outputArea.innerHTML = '';
        spritesGrid.innerHTML = '';
        spritesGrid.style.display = 'none';
        outputArea.style.display = 'block';
        currentTokens = [];
    }

    // Toggle Sprites / Text View
    btnToggleSprites.addEventListener('click', () => {
        isSpriteView = !isSpriteView;
        if (isSpriteView) {
            btnToggleSprites.textContent = 'SPRITES: ON 👾';
            if (currentTokens.length > 0) {
                outputArea.style.display = 'none';
                spritesGrid.style.display = 'flex';
            } else {
                updateStatus('NO SPRITES TO SHOW (ENCODE FIRST)');
            }
        } else {
            btnToggleSprites.textContent = 'SPRITES: OFF 📝';
            outputArea.style.display = 'block';
            spritesGrid.style.display = 'none';
        }
    });

    // Render Sprites Grid
    function renderSprites(tokens) {
        spritesGrid.innerHTML = '';
        if (!tokens || tokens.length === 0) {
            return;
        }

        tokens.forEach(token => {
            if (token.type === 'pokemon' && token.dex_id) {
                const card = document.createElement('div');
                card.className = 'sprite-card';

                const img = document.createElement('img');
                img.className = 'sprite-img';
                img.alt = token.name;
                img.src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${token.dex_id}.png`;
                img.onerror = () => {
                    img.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png';
                };

                const nameLabel = document.createElement('span');
                nameLabel.className = 'sprite-name';
                nameLabel.textContent = token.name;

                card.appendChild(img);
                card.appendChild(nameLabel);
                spritesGrid.appendChild(card);
            } else {
                const badge = document.createElement('span');
                badge.className = 'special-token-badge';
                badge.textContent = token.name;
                spritesGrid.appendChild(badge);
            }
        });
    }

    // Encrypt
    btnEncrypt.addEventListener('click', async () => {
        const text = inputArea.value;
        if (!text.trim()) {
            updateStatus('ENTER TEXT TO ENCRYPT');
            outputArea.textContent = 'Please enter text to encrypt.';
            return;
        }

        updateStatus('ENCRYPTING...');
        try {
            const res = await fetch('/api/encode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await res.json();
            if (res.ok) {
                outputArea.textContent = data.encoded;
                currentTokens = data.tokens || [];
                renderSprites(currentTokens);

                if (isSpriteView) {
                    outputArea.style.display = 'none';
                    spritesGrid.style.display = 'flex';
                }

                statusTime.textContent = `(${data.elapsed.toFixed(3)}s)`;
                updateStatus('ENCRYPTED OK!');
            } else {
                outputArea.textContent = data.error || 'Encryption failed.';
                updateStatus('ERROR');
            }
        } catch (err) {
            outputArea.textContent = 'Network or server error.';
            updateStatus('SERVER ERROR');
        }
    });

    // Decrypt
    btnDecrypt.addEventListener('click', async () => {
        const text = inputArea.value.trim();
        if (!text) {
            updateStatus('ENTER POKÉMON NAMES TO DECRYPT');
            outputArea.textContent = 'Please enter Pokémon names to decrypt.';
            return;
        }

        updateStatus('DECRYPTING...');
        try {
            const res = await fetch('/api/decode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await res.json();
            if (res.ok) {
                // Parse highlights for [x,y] ambiguous and {x,y} state errors
                let decodedStr = data.decoded;
                let htmlFormatted = decodedStr
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;');

                // Highlight ambiguous [x,y]
                htmlFormatted = htmlFormatted.replace(/\[([^\]]+)\]/g, '<span class="highlight-ambiguous">[$1]</span>');
                // Highlight state errors {x,y}
                htmlFormatted = htmlFormatted.replace(/\{([^}]+)\}/g, '<span class="highlight-error">{$1}</span>');

                outputArea.innerHTML = htmlFormatted;
                spritesGrid.style.display = 'none';
                outputArea.style.display = 'block';

                statusTime.textContent = `(${data.elapsed.toFixed(3)}s)`;
                updateStatus('DECRYPTED OK!');
            } else {
                outputArea.textContent = data.error || 'Decryption failed.';
                updateStatus('ERROR');
            }
        } catch (err) {
            outputArea.textContent = 'Network or server error.';
            updateStatus('SERVER ERROR');
        }
    });

    // Swap
    btnSwap.addEventListener('click', () => {
        const outText = outputArea.textContent.trim();
        if (!outText) {
            updateStatus('NOTHING TO SWAP');
            return;
        }
        inputArea.value = outText;
        clearOutput();
        updateStatus('OUTPUT SWAPPED TO INPUT');
    });

    // Copy
    btnCopy.addEventListener('click', () => {
        const outText = outputArea.textContent.trim();
        if (outText) {
            navigator.clipboard.writeText(outText).then(() => {
                updateStatus('COPIED TO CLIPBOARD!');
            }).catch(() => {
                updateStatus('COPY FAILED');
            });
        } else {
            updateStatus('NO OUTPUT TO COPY');
        }
    });

    // Clear
    btnClear.addEventListener('click', () => {
        inputArea.value = '';
        clearOutput();
        statusTime.textContent = '';
        updateStatus('CLEARED');
    });
});
