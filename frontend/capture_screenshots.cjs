const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 1024 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  page.on('console', msg => console.log('BROWSER:', msg.text()));

  const url = 'http://localhost:5173';
  console.log(`Navigating to ${url}`);
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  // Wait for the app to load and health check to pass
  await page.waitForTimeout(2000);

  const scenarios = [
    {
      name: '01_hinglish_phishing',
      text: 'Aapka account block ho jayega, turant click karein: http://amaz0n-verify.xyz/login'
    },
    {
      name: '02_english_ml_phishing_final',
      text: 'URGENT: Your mobile number has been selected for a cash prize of $50,000. Visit http://192.168.1.10/claim immediately to claim your money.'
    },
    {
      name: '03_url_intelligence',
      text: 'To verify your identity, visit http://192.168.1.10/login or https://bit.ly/update-now'
    },
    {
      name: '04_low_risk_benign',
      text: 'Hey, want to grab coffee tomorrow afternoon?'
    }
  ];

  const results = [];

  for (const scenario of scenarios) {
    console.log(`Running scenario: ${scenario.name}`);
    
    // Clear textarea
    await page.fill('#message-input', '');
    // Type text
    await page.fill('#message-input', scenario.text);
    // Click analyze
    await page.click('#analyze-btn');
    
    // Wait for result to appear
    await page.waitForSelector('#result-section .animate-in', { timeout: 60000 });
    // Wait for animations to finish
    await page.waitForTimeout(1500);

    // Extract actual results for report
    const verdictLabel = await page.$eval('#result-section', el => {
      const match = el.innerText.match(/(High Risk|Suspicious|Low Risk)/i);
      return match ? match[1] : 'N/A';
    }).catch(() => 'N/A');
    
    const riskScore = await page.$eval('.score-ring-progress', el => el.parentElement.parentElement.innerText.split('\n')[0]).catch(() => 'N/A');
    const languageText = await page.$eval('#result-section', el => {
      const match = el.innerText.match(/Language\n(.*)\n/i);
      return match ? match[1] : 'N/A';
    }).catch(() => 'N/A');
    
    const hasMl = await page.$eval('#result-section', el => el.innerText.includes('AI Classification')).catch(() => false);
    let mlPrediction = 'N/A';
    if (hasMl) {
      mlPrediction = await page.$eval('#result-section', el => {
        const match = el.innerText.match(/(\u26A0 Phishing Detected|\u2713 Likely Benign)/);
        return match ? match[1] : 'Found AI Section';
      }).catch(() => 'Error getting ML result');
    }

    results.push({
      scenario: scenario.name,
      verdict: verdictLabel,
      score: riskScore,
      language: languageText,
      ml_result: mlPrediction
    });

    const outPath = path.resolve(__dirname, '..', `${scenario.name}.png`);
    await page.screenshot({ path: outPath, fullPage: true });
    console.log(`Saved screenshot to ${outPath}`);
  }

  await browser.close();

  fs.writeFileSync(path.resolve(__dirname, '..', 'screenshot_results.json'), JSON.stringify(results, null, 2));
  console.log('Done!');
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
