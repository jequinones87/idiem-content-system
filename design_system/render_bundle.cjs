/* Rasteriza cada gráfica standalone del bundle a PNG 1080x1080.
   Uso: node design_system/render_bundle.cjs <manifest.json>
   El manifest es un array de {html, png}. Espera a que Montserrat cargue
   (document.fonts.ready) antes de capturar, para fidelidad de marca. */
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

(async () => {
  const manifestPath = process.argv[2];
  if (!manifestPath) { console.error('falta manifest.json'); process.exit(1); }
  const items = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
  });

  let ok = 0;
  for (const it of items) {
    await page.goto('file://' + it.html, { waitUntil: 'load', timeout: 60000 });
    try { await page.evaluate(() => document.fonts.ready); } catch (e) {}
    try { await page.evaluate(() => document.fonts.load('800 40px Montserrat')); } catch (e) {}
    await page.waitForTimeout(500);
    const el = await page.$('.export');
    await el.screenshot({ path: it.png });
    ok++;
    console.log('png ' + ok + '/' + items.length + '  ' + it.png.split('/').pop());
  }
  await browser.close();
  console.log('done ' + ok + ' PNG');
})();
