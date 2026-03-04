const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
        const files = [
            '/Users/satvikjain/Downloads/PM/output/Satvik_Jain_Google_GenAI_PM.html',
            '/Users/satvikjain/Downloads/PM/output/Satvik_Jain_Microsoft_Copilot_PM.html',
            '/Users/satvikjain/Downloads/PM/output/Satvik_Jain_Amazon_Principal_PMT.html'
        ];
        // 1123px is A4 height at 96 DPI
        const A4_HEIGHT = 1123;
        
        for (let f of files) {
            const page = await browser.newPage();
            // A4 exact dimensions in CSS pixels (96dpi)
            await page.setViewport({ width: 794, height: 1123 });
            
            await page.goto('file://' + f).catch(e => {}); 
            // Wait a tiny bit just in case styles jump
            await new Promise(r => setTimeout(r, 1000));
            
            const pageHeight = await page.evaluate(() => {
                const el = document.querySelector('.page');
                return el ? el.getBoundingClientRect().height : document.body.scrollHeight;
            });
            
            console.log(f.split('/').pop() + ':');
            console.log('  Content Height = ' + pageHeight + 'px');
            console.log('  A4 Target = ' + A4_HEIGHT + 'px');
            
            if (pageHeight > A4_HEIGHT) {
                console.log('  STATUS: OVERFLOW by ' + (pageHeight - A4_HEIGHT).toFixed(1) + 'px (Will generate 2 pages)');
            } else {
                console.log('  STATUS: FITS 1 PAGE. White space remaining: ' + (A4_HEIGHT - pageHeight).toFixed(1) + 'px');
            }
            console.log('---');
            
            // Output PDF so we know what we get
            await page.pdf({
                path: f.replace('.html', '.pdf'),
                format: 'A4',
                printBackground: true,
                margin: { top: 0, right: 0, bottom: 0, left: 0 }
            });
            
            await page.close();
        }
        await browser.close();
    } catch(e) {
        console.error("Script failed:", e);
    }
})();
