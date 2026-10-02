if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light-theme');
}

// Copy to clipboard helper
function copyText(text) {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
        showToast(`Copied: ${text.length > 30 ? text.substring(0, 27) + '...' : text}`);
    }).catch(() => {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('Copied to clipboard!');
    });
}

function showToast(msg) {
    const toast = document.getElementById('copyToast');
    const toastText = document.getElementById('copyToastText');
    if (!toast || !toastText) return;
    toastText.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2500);
}

// Live Products Table Loader
let catalogProducts = [];

function toSlug(name) {
    return (name || '').trim().toLowerCase().replace(/ /g, '_');
}

async function loadProductsTable() {
    const tbody = document.getElementById('productsTableBody');
    const countBadge = document.getElementById('productCountBadge');
    if (!tbody || !countBadge) return;

    try {
        const res = await fetch('/api/public/products');
        if (res.ok) {
            catalogProducts = await res.json();
        }
    } catch (e) {
        console.error("Failed to load products dynamically:", e);
    }

    if (!catalogProducts || catalogProducts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">No products found in catalog.</td></tr>`;
        countBadge.textContent = '0 items';
        return;
    }

    countBadge.textContent = `${catalogProducts.length} items`;
    renderProductsTable(catalogProducts);
}

function renderProductsTable(prods) {
    const tbody = document.getElementById('productsTableBody');
    if (!tbody) return;
    if (prods.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching products found.</td></tr>`;
        return;
    }

    tbody.innerHTML = prods.map(p => {
        const slug = toSlug(p.name);
        let logoUrl = p.logo;
        if (logoUrl && logoUrl.trim() !== '') {
            if (!logoUrl.startsWith('/') && !logoUrl.startsWith('http')) {
                logoUrl = `https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://${encodeURIComponent(p.logo)}&size=64`;
            }
        } else {
            logoUrl = 'assets/logo.jpg';
        }

        const stockNum = typeof p.stock === 'number' ? p.stock : 0;
        const isOutOfStock = stockNum <= 0;
        const isCapped = p.stockCapped;
        const stockDisplay = isCapped ? '>1000' : stockNum;

        let tiersHtml = '';
        if (p.tiers && p.tiers.length > 0) {
            tiersHtml = p.tiers.map(t => {
                const range = t.maxQty ? `${t.minQty}–${t.maxQty}` : `${t.minQty}+`;
                return `<span class="tier-badge-chip">${range}: $${t.price.toFixed(2)}</span>`;
            }).join(' ');
        } else {
            tiersHtml = '<span style="color: var(--text-muted); font-size: 0.85rem;">Standard</span>';
        }

        return `
            <tr>
                <td>
                    <div class="prod-name-cell">
                        <img src="${logoUrl}" alt="logo" class="prod-logo-img">
                        <div>
                            <div style="font-weight: 600;">${escapeHtml(p.name)}</div>
                            <div style="font-size: 0.78rem; color: var(--text-muted);">${escapeHtml(p.type || 'Digital Product')}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="slug-pill" data-copy-text="${escapeHtml(slug)}" title="Click to copy slug">
                        <code>${escapeHtml(slug)}</code>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                    </span>
                </td>
                <td>
                    <div class="stock-indicator">
                        <span class="stock-dot ${isOutOfStock ? 'out' : ''}"></span>
                        <span>${stockDisplay}</span>
                    </div>
                </td>
                <td style="font-weight: 700; font-family: var(--font-mono);">
                    $${(p.priceFrom || 0).toFixed(2)}
                </td>
                <td>
                    ${tiersHtml}
                </td>
            </tr>
        `;
    }).join('');
}

function filterProductsTable() {
    const searchInput = document.getElementById('productSearchInput');
    if (!searchInput) return;
    const query = searchInput.value.trim().toLowerCase();
    if (!query) {
        renderProductsTable(catalogProducts);
        return;
    }

    const filtered = catalogProducts.filter(p => {
        const nameMatch = (p.name || '').toLowerCase().includes(query);
        const slugMatch = toSlug(p.name).includes(query);
        return nameMatch || slugMatch;
    });
    renderProductsTable(filtered);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        const sunIcon = themeBtn.querySelector('.theme-icon-sun');
        const moonIcon = themeBtn.querySelector('.theme-icon-moon');
        let isDark = localStorage.getItem('theme') !== 'light';

        if (!isDark && sunIcon && moonIcon) {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }

        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            isDark = !isDark;
            localStorage.setItem('theme', isDark ? 'dark' : 'light');

            const outgoing = isDark ? moonIcon : sunIcon;
            const incoming = isDark ? sunIcon : moonIcon;

            if (outgoing && incoming) {
                outgoing.style.transition = 'transform 0.3s ease-in, opacity 0.3s ease-in';
                outgoing.style.transform = 'rotate(90deg) scale(0)';
                outgoing.style.opacity = '0';

                setTimeout(() => {
                    outgoing.style.display = 'none';
                    outgoing.style.transform = '';
                    outgoing.style.opacity = '';

                    incoming.style.display = 'block';
                    incoming.style.transform = 'rotate(-90deg) scale(0)';
                    incoming.style.opacity = '0';

                    incoming.offsetHeight; // reflow
                    incoming.style.transition = 'transform 0.3s ease-out, opacity 0.3s ease-out';
                    incoming.style.transform = 'rotate(0deg) scale(1)';
                    incoming.style.opacity = '1';
                }, 300);
            }
        });
    }

    // Delegated click for copy pills and buttons
    document.addEventListener('click', (e) => {
        const pill = e.target.closest('[data-copy-text]');
        if (pill) {
            copyText(pill.getAttribute('data-copy-text'));
            return;
        }

        const btn = e.target.closest('[onclick]');
        if (btn) {
            const code = btn.getAttribute('onclick');
            if (code && code.includes('copyText(')) {
                const match = code.match(/copyText\((.*)\)/);
                if (match) {
                    let arg = match[1].trim();
                    if ((arg.startsWith("'") && arg.endsWith("'")) || (arg.startsWith('"') && arg.endsWith('"'))) {
                        copyText(arg.slice(1, -1));
                    } else if (arg.includes('.innerText')) {
                        const idMatch = arg.match(/getElementById\(['"]([^'"]+)['"]\)/);
                        if (idMatch) {
                            const target = document.getElementById(idMatch[1]);
                            if (target) copyText(target.innerText);
                        }
                    }
                }
            }
        }
    });

    const searchInput = document.getElementById('productSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterProductsTable);
    }

    loadProductsTable();
});
