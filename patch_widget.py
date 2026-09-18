#!/usr/bin/env python3
"""Usage: python3 patch_widget.py your-widget.html [output.html]
Turns hardcoded design values in the widget into config variables the dashboard can control.
Fails loudly (assertion) if the file doesn't match the expected original, so it never half-patches."""
import re, sys
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else 'widget.html'
s = open(src, encoding='utf-8').read()
h, t = s.split('</style>', 1)

# ---- CSS: colors, gradients, corners, pill delay ----
h = h.replace('#F2EFE6', 'var(--bubble)').replace('#ECE8DE', 'var(--line)')
for g in ['linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%)', 'linear-gradient(135deg, var(--accent), var(--accent2))']:
    assert g in h, g; h = h.replace(g, 'var(--grad)')
for g in ['linear-gradient(135deg, var(--c1) 0%, var(--c2) 100%)', 'linear-gradient(135deg, var(--c1), var(--c2))']:
    assert g in h, g; h = h.replace(g, 'var(--hgrad)')
M = {18: '1', 16: '1', 14: '2', 12: '2', 10: '3', 9: '3', 26: 'p', 30: 'p', 50: 'p', 20: 'p'}
h = re.sub(r'border-radius:\s*(\d+)px', lambda m: 'border-radius: var(--r%s)' % M[int(m[1])] if int(m[1]) in M else m[0], h)
assert h.count('--gap: 24px;') == 1
h = h.replace('--gap: 24px;', '--gap: 24px; --bubble:#F2EFE6; --line:#ECE8DE; --grad:linear-gradient(135deg,var(--accent),var(--accent2)); --hgrad:linear-gradient(135deg,var(--c1),var(--c2)); --r1:18px; --r2:14px; --r3:10px; --rp:50px; --on-accent:#fff; --pill-delay:0.6s;')
a = 'cubic-bezier(.2,.9,.3,1.2) 0.6s both'
assert h.count(a) == 1; h = h.replace(a, 'cubic-bezier(.2,.9,.3,1.2) var(--pill-delay) both')
h += '''
  .opt-pill:hover, .tour-badge, .tour-btn.book, .tour-modal-book, .ck-submit-btn { color: var(--on-accent); }
  .send-btn svg path { stroke: var(--on-accent); }
  .launcher-btn .li { width: 30px; height: 30px; stroke: var(--on-accent); pointer-events: none; }
  .launcher-btn img.li { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
'''
s = h + '</style>' + t

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)

# ---- JS: defaults ----
rep("colors: { primary: '#2B2E48', secondary: '#494e6c', accent: '#F2994A', accent2: '#F6C453' },",
"""colors: { primary: '#2B2E48', secondary: '#494e6c', accent: '#F2994A', accent2: '#F6C453', ink: '#24263A', muted: '#7B7E96', surface: '#FBFAF8', bubble: '#F2EFE6', line: '#ECE8DE' },
    corners: 'soft', gradient: true, launcherIcon: 'sun', launcherIconUrl: '', fontUrl: '', autoOpenSec: 0, pillDelaySec: 0.6,
    onlineLabel: 'Online', aiBadge: 'AI', youLabel: 'You', errorText: 'Sorry, there was a connection issue. Please try again.', retryText: 'Retry',
    detailsText: 'Details', bookText: 'Book Now', poweredText: 'Powered by', poweredLabel: 'botyama.com', poweredUrl: 'https://botyama.com',""")

# ---- JS: helpers ----
rep("  function applyConfig() {", '''  const contrast = (h) => { const n = parseInt(String(h).replace('#', '').padEnd(6, '0').slice(0, 6), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; return (0.299 * r + 0.587 * g + 0.114 * b) > 165 ? '#1d1d2b' : '#fff'; };
  const ICON = {
    sun: '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4M12 19.1v2.4M4.2 4.2l1.7 1.7M18.1 18.1l1.7 1.7M2.5 12h2.4M19.1 12h2.4M4.2 19.8l1.7-1.7M18.1 5.9l1.7-1.7"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.2-4.4A8 8 0 1 1 21 12z"/>',
    headset: '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/><path d="M19 20a4 4 0 0 1-4 2h-2"/>',
    sparkle: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>'
  };
  function applyConfig() {''')

# ---- JS: apply variables ----
rep("s.setProperty('--accent2', c.colors.accent2);", '''s.setProperty('--accent2', c.colors.accent2);
    const k = c.colors;
    s.setProperty('--ink', k.ink); s.setProperty('--muted', k.muted); s.setProperty('--surface', k.surface);
    s.setProperty('--bubble', k.bubble); s.setProperty('--line', k.line);
    const R = ({ sharp: [4, 3, 2, 8], soft: [18, 14, 10, 50], round: [26, 20, 14, 50] })[c.corners] || [18, 14, 10, 50];
    ['r1', 'r2', 'r3', 'rp'].forEach((n, i) => s.setProperty('--' + n, R[i] + 'px'));
    const solid = c.gradient === false;
    s.setProperty('--grad', solid ? 'var(--accent)' : 'linear-gradient(135deg, var(--accent), var(--accent2))');
    s.setProperty('--hgrad', solid ? 'var(--c1)' : 'linear-gradient(135deg, var(--c1), var(--c2))');
    s.setProperty('--on-accent', contrast(k.accent));
    s.setProperty('--pill-delay', (c.pillDelaySec == null ? 0.6 : c.pillDelaySec) + 's');''')

rep("$('powered').style.display = c.showPoweredBy ? '' : 'none';", '''$('powered').style.display = c.showPoweredBy ? '' : 'none';
    $('powered').innerHTML = esc(c.poweredText) + ' <a href="' + esc(c.poweredUrl) + '" target="_blank" rel="noopener">' + esc(c.poweredLabel) + '</a>';
    $('hdr-online').textContent = c.onlineLabel;
    if (c.fontUrl && !loadedFonts[c.fontUrl]) { loadedFonts[c.fontUrl] = 1; const fl = document.createElement('link'); fl.rel = 'stylesheet'; fl.href = c.fontUrl; document.head.appendChild(fl); }
    const lb = $('launcherBtn');
    lb.querySelectorAll('.li, svg').forEach((x) => x.remove());
    lb.insertAdjacentHTML('beforeend', (c.launcherIcon === 'custom' && c.launcherIconUrl) ? '<img class="li" src="' + esc(c.launcherIconUrl) + '" alt="">' : '<svg class="li" viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + (ICON[c.launcherIcon] || ICON.sun) + '</svg>');''')

# ---- HTML/JS strings that become editable ----
rep('<span class="agent-badge">Online</span>', '<span class="agent-badge" id="hdr-online">Online</span>')
rep('<span class="agent-row-badge">AI</span>', '<span class="agent-row-badge">${esc(CONFIG.aiBadge)}</span>')
rep('<div class="u-av">You</div>', '<div class="u-av">${esc(CONFIG.youLabel)}</div>')
rep('Sorry, there was a connection issue. Please try again.<br><button class="retry-btn" data-act="retry">Retry</button>',
    '${esc(CONFIG.errorText)}<br><button class="retry-btn" data-act="retry">${esc(CONFIG.retryText)}</button>')
rep('data-act="details" data-key="${key}">Details</button>', 'data-act="details" data-key="${key}">${esc(CONFIG.detailsText)}</button>')
rep('data-act="book" data-key="${key}">Book Now</button>', 'data-act="book" data-key="${key}">${esc(CONFIG.bookText)}</button>', 2)

# ---- auto-open ----
rep("  init();\n})();", """  init().then(() => {
    if (!PREVIEW && CONFIG.autoOpenSec > 0) setTimeout(() => { if (!isOpen && !hasOpenedOnce) openWidget(); }, CONFIG.autoOpenSec * 1000);
  });
})();""")

open(out, 'w', encoding='utf-8').write(s)
print('Done ->', out)
