// Records one MP4 per screen of index.html: a fake cursor moves, scrolls and clicks.
// Frame-by-frame capture, so motion is smooth regardless of machine speed.
// Run: node demo/make_videos.js   (needs Playwright + ffmpeg)
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');

const FPS = 30;
const VIEW = { width: 1600, height: 900 };
const SCALE = 1.2; // 1600x900 * 1.2 = 1920x1080 video
const OUT = path.join(__dirname, 'videos');

// Each step: wait, cap (caption), move (to element), click, scroll (element into view)
const SCREENS = [
  { id: 'rm', file: '1-relationship-manager-radar', steps: [
    { cap: 'The relationship manager sees which owners to talk to' },
    { wait: 700 },
    { move: '#rm .feature .score' }, { wait: 500 },
    { move: '#rm .feature .chips .chip:nth-child(3)' }, { wait: 600 },
    { cap: '…and why: age, no heir, falling investment' }, { wait: 900 },
    { move: '#rm .feature .btn' }, { wait: 300 }, { click: '#rm .feature .btn' },
    { cap: 'One click opens the conversation, with consent' }, { wait: 1200 },
    { scroll: '#rm .g-2' }, { move: '#rm .g-2 .card:nth-child(2) .lnk' }, { wait: 1500 },
  ]},
  { id: 'owner', file: '3-owner-next-owner', reset: true, steps: [
    { cap: 'Jan, the owner, sees what Bakkerij Peeters is worth' },
    { wait: 700 },
    { move: '#owner .big' }, { wait: 700 },
    { move: '#owner .feature .lnk' }, { wait: 900 },
    { scroll: '#owner .g-2' },
    { cap: 'Jan sets the timing and a role after the sale' },
    { move: '#owner .choices:nth-of-type(1) button:nth-child(2)' }, { click: '#owner .choices:nth-of-type(1) button:nth-child(2)' }, { wait: 400 },
    { move: '#owner .choices:nth-of-type(2) button:nth-child(2)' }, { click: '#owner .choices:nth-of-type(2) button:nth-child(2)' }, { wait: 600 },
    { cap: '…and sees anonymous successors with a fit score' },
    { move: '#owner .g-2 .card:nth-child(2) .row:nth-of-type(1) .score' }, { wait: 1000 },
    { scroll: '#owner .content > p .btn' },
    { cap: 'One click starts the search' },
    { move: '#owner .content > p .btn' }, { wait: 300 }, { click: '#owner .content > p .btn' }, { wait: 1600 },
  ]},
  { id: 'headhunter', file: '4-headhunter-partner-portal', steps: [
    { cap: 'The headhunter receives an anonymous brief' },
    { wait: 700 },
    { move: '#headhunter .fact:nth-child(1)' }, { wait: 400 },
    { move: '#headhunter .fact:nth-child(2)' }, { wait: 400 },
    { move: '#headhunter .fact:nth-child(3)' }, { wait: 500 },
    { cap: 'The company name stays locked until the NDA' },
    { move: '#headhunter .lock' }, { wait: 1000 },
    { cap: 'The headhunter submits a fitting candidate' },
    { move: '#headhunter .feature .btn' }, { wait: 300 }, { click: '#headhunter .feature .btn' }, { wait: 1000 },
    { scroll: '#headhunter .g-2' },
    { cap: '…and earn a fee per qualified candidate' },
    { move: '#headhunter .g-2 .card:nth-child(2) .lnk' }, { wait: 1500 },
  ]},
  { id: 'candidate', file: '5-candidate-ready-to-own', steps: [
    { cap: 'Sarah, a candidate, follows the Ready-to-Own path' },
    { wait: 700 },
    { move: '#candidate .step:nth-child(1) .dot' }, { wait: 300 },
    { move: '#candidate .step:nth-child(2) .dot' }, { wait: 300 },
    { move: '#candidate .step:nth-child(3) .dot' }, { wait: 500 },
    { cap: 'Tested, funding checked, in training' }, { wait: 800 },
    { scroll: '#candidate .feature' },
    { cap: 'KBC matches Sarah with a company' },
    { move: '#candidate .feature .score' }, { wait: 800 },
    { move: '#candidate .feature .btn' }, { wait: 300 }, { click: '#candidate .feature .btn' },
    { cap: 'One click shows interest' }, { wait: 1600 },
  ]},
  { id: 'deal', file: '6-relationship-manager-deal-room', steps: [
    { cap: 'The relationship manager brings owner and successor together' },
    { wait: 700 },
    { move: '#deal .person:nth-child(1) .face' }, { wait: 500 },
    { move: '#deal .link .fit' }, { wait: 600 },
    { move: '#deal .person:nth-child(3) .face' }, { wait: 500 },
    { move: '#deal .card > p .btn' }, { wait: 300 }, { click: '#deal .card > p .btn' },
    { cap: 'The introduction meeting is planned' }, { wait: 1200 },
    { scroll: '#deal .g-2' },
    { cap: 'Deal progress and financing in one view' },
    { move: '#deal .checklist li.now' }, { wait: 700 },
    { move: '#deal .money .main' }, { wait: 700 },
    { move: '#deal .gain span:first-child' }, { wait: 1500 },
  ]},
];

// Overlay drawn inside the page: cursor, click ripple, caption
const OVERLAY = `
  .demo-bar { display: none !important; }
  .content { margin: 0 auto; }
  #fx-cur { position: fixed; left: 0; top: 0; z-index: 99999; pointer-events: none; width: 34px; height: 34px; transform-origin: 6px 4px; }
  #fx-rip { position: fixed; z-index: 99998; pointer-events: none; border-radius: 50%; background: rgba(0,159,223,.35); }
  #fx-cap { position: fixed; left: 50%; bottom: 36px; transform: translateX(-50%); z-index: 99997; pointer-events: none;
    background: rgba(0,55,104,.94); color: #fff; font: 700 26px "Nunito Sans", sans-serif; padding: 14px 30px; border-radius: 999px;
    white-space: nowrap; box-shadow: 0 8px 30px rgba(0,40,80,.25); }`;
const ARROW = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M5 2l14 11.5-6.2.6 3.8 7.4-2.8 1.4-3.7-7.5L5 20z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
const HAND = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M9 11V4.5a1.5 1.5 0 0 1 3 0V10m0-1.5a1.5 1.5 0 0 1 3 0V11m0-1a1.5 1.5 0 0 1 3 0v5.5c0 3.5-2.5 6.5-6 6.5h-1c-2.5 0-4-1.2-5.3-3.2L3.5 14.5a1.5 1.5 0 0 1 2.4-1.8L9 15z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';

const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const frames = ms => Math.max(1, Math.round(ms / 1000 * FPS));

async function record(page, screen) {
  const out = path.join(OUT, screen.file + '.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  const done = new Promise(r => ff.on('close', r));

  await page.evaluate(([id, reset]) => {
    show(id);
    if (reset) document.querySelectorAll('#' + id + ' .choices button').forEach(b => b.classList.remove('on'));
  }, [screen.id, !!screen.reset]);

  const s = { x: 1150, y: 640, press: 1, rip: null, cap: '', capAge: 99, scrollY: 0 };

  async function frame() {
    s.capAge++;
    if (s.rip) s.rip.age++;
    await page.mouse.move(s.x, s.y);
    await page.evaluate(([s, ARROW, HAND]) => {
      window.scrollTo(0, s.scrollY);
      const cur = document.getElementById('fx-cur');
      const over = document.elementFromPoint(s.x, s.y);
      const hand = over && over.closest('button, a');
      if (cur.dataset.kind !== (hand ? 'h' : 'a')) { cur.innerHTML = hand ? HAND : ARROW; cur.dataset.kind = hand ? 'h' : 'a'; }
      cur.style.transform = `translate(${s.x - (hand ? 12 : 6)}px, ${s.y - 4}px) scale(${s.press})`;
      const rip = document.getElementById('fx-rip');
      if (s.rip && s.rip.age < 16) {
        const r = 12 + s.rip.age * 3.5;
        Object.assign(rip.style, { display: 'block', left: (s.rip.x - r) + 'px', top: (s.rip.y - r) + 'px', width: 2 * r + 'px', height: 2 * r + 'px', opacity: 1 - s.rip.age / 16 });
      } else rip.style.display = 'none';
      const cap = document.getElementById('fx-cap');
      cap.textContent = s.cap;
      cap.style.display = s.cap ? 'block' : 'none';
      cap.style.opacity = Math.min(1, s.capAge / 8);
    }, [s, ARROW, HAND]);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }

  async function centerOf(sel) {
    const box = await page.locator(sel).first().boundingBox();
    if (!box) throw new Error('Not found: ' + sel);
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  }

  for (let i = 0; i < frames(400); i++) await frame();
  for (const st of screen.steps) {
    if (st.cap !== undefined) { s.cap = st.cap; s.capAge = 0; }
    if (st.wait) for (let i = 0; i < frames(st.wait); i++) await frame();
    if (st.move) {
      const to = await centerOf(st.move), from = { x: s.x, y: s.y };
      const dist = Math.hypot(to.x - from.x, to.y - from.y);
      const n = frames(Math.min(1100, 350 + dist * 0.8));
      for (let i = 1; i <= n; i++) {
        const k = ease(i / n);
        s.x = from.x + (to.x - from.x) * k;
        s.y = from.y + (to.y - from.y) * k - Math.sin(Math.PI * i / n) * dist * 0.06; // slight arc
        await frame();
      }
    }
    if (st.click) {
      for (const p of [0.92, 0.85]) { s.press = p; await frame(); }
      await page.mouse.click(s.x, s.y);
      s.rip = { x: s.x, y: s.y, age: 0 };
      for (const p of [0.9, 1, 1]) { s.press = p; await frame(); }
    }
    if (st.scroll) {
      const target = await page.evaluate(([sel, cur]) => {
        const r = document.querySelector(sel).getBoundingClientRect();
        const max = document.documentElement.scrollHeight - innerHeight;
        return Math.max(0, Math.min(max, cur + r.top + r.height / 2 - innerHeight * 0.45));
      }, [st.scroll, s.scrollY]);
      const from = s.scrollY, n = frames(900);
      for (let i = 1; i <= n; i++) { s.scrollY = from + (target - from) * ease(i / n); await frame(); }
    }
  }
  for (let i = 0; i < frames(600); i++) await frame();

  ff.stdin.end();
  await done;
  console.log('wrote', path.relative(process.cwd(), out));
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
  const browser = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
  const only = process.argv[2];
  for (const screen of SCREENS) {
    if (only && screen.id !== only) continue;
    const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: SCALE, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    await page.goto('file://' + path.join(__dirname, 'index.html'));
    await page.evaluate(() => document.fonts.ready);
    await page.addStyleTag({ content: OVERLAY });
    await page.evaluate(() => {
      for (const id of ['fx-rip', 'fx-cur', 'fx-cap']) { const d = document.createElement('div'); d.id = id; document.body.appendChild(d); }
    });
    await record(page, screen);
    await ctx.close();
  }
  await browser.close();
})();
