// Execute the actual inline page script against a small DOM harness; no browser or network.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor() {
    this.children = [];
    this.listeners = {};
    this.style = {};
    this.dataset = {};
    this.classList = { add() {}, remove() {}, toggle() {}, contains() { return false; } };
  }
  set innerHTML(value) { this.html = value; this.children = []; }
  get innerHTML() { return this.html || ''; }
  appendChild(node) { this.children.push(node); }
  removeChild() {}
  setAttribute() {}
  addEventListener(event, callback) { this.listeners[event] = callback; }
  querySelectorAll() { return []; }
  focus() {}
  click() {}
}

async function main() {
  const root = path.resolve(__dirname, '..');
  const html = fs.readFileSync(path.join(root, 'market-dashboard.html'), 'utf8');
  const script = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).join('\n');
  const embedded = JSON.parse(script.match(/const INITIAL_SNAPSHOT = (\{.*?\});\s*let currentData/s)[1]);
  const nodes = new Map();
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, new Element());
    return nodes.get(id);
  };
  let csvBlob;
  const context = vm.createContext({
    document: { getElementById: node, createElement: () => new Element(),
      querySelectorAll: () => [], addEventListener() {}, documentElement: new Element(),
      activeElement: new Element(), body: new Element() },
    window: { matchMedia: () => ({ matches: false }) },
    localStorage: { getItem: () => null, setItem() {} }, location: { protocol: 'file:' },
    setTimeout() {}, console, Blob,
    URL: { createObjectURL(blob) { csvBlob = blob; return 'test:csv'; }, revokeObjectURL() {} },
  });
  vm.runInContext(script, context);
  const data = JSON.parse(vm.runInContext('JSON.stringify(currentData)', context));
  const snapshot = JSON.parse(fs.readFileSync(path.join(root, 'cache/quotes_latest.json'), 'utf8'));
  assert.equal(data.items.length, snapshot.items.length);
  assert.deepEqual(embedded, snapshot);
  const sorted = [...data.items].sort((a, b) => b.price_diff_pct - a.price_diff_pct);
  assert.equal(node('tableBody').children.length, data.items.length);
  for (const [index, item] of sorted.entries()) {
    const cells = [...node('tableBody').children[index].innerHTML.matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/g)].map(m => m[1]);
    assert.equal(cells.length, 13);
    assert.ok(cells[8].includes(item.dynamic_base_upside_str), item.company + ' Base column');
    assert.ok(cells[8].includes('Base目标'), item.company + ' target label');
    for (const scenario of ['bear', 'base', 'bull']) {
      const expected = (item[scenario] - item.latest_price) / item.latest_price * 100;
      assert.ok(Math.abs(item[`dynamic_${scenario}_upside`] - expected) < 1e-9);
      assert.ok(Math.abs(snapshot.items.find(d => d.code === item.code)[`dynamic_${scenario}_upside`] - expected) < 1e-9);
    }
    vm.runInContext(`openDrawer(currentData.items.find(d => d.code === ${JSON.stringify(item.code)}))`, context);
    assert.ok(node('drawerBody').innerHTML.includes(item.dynamic_base_upside_str));
  }
  vm.runInContext("currentChartMode = 'dynamic_base'; renderDeviationChart()", context);
  assert.ok(node('devBarsContainer').children[0].innerHTML.includes('最新行情价 → Base估值目标'));
  const winner = [...data.items].sort((a, b) => b.dynamic_base_upside - a.dynamic_base_upside)[0];
  assert.ok(node('devBarsContainer').children[0].innerHTML.includes(winner.company));
  // Every ranking shows exact values and contextual comparisons without decorative bars.
  for (const mode of ['price_diff', 'dynamic_base', 'delta_upside']) {
    vm.runInContext(`currentChartMode = '${mode}'; chartExpanded = true; renderDeviationChart()`, context);
    assert.equal(node('devBarsContainer').children.length, data.items.length);
    const metric = { price_diff: 'price_diff_pct', dynamic_base: 'dynamic_base_upside', delta_upside: 'delta_upside' }[mode];
    const ranking = [...data.items].sort((a, b) => b[metric] - a[metric]);
    for (const [index, row] of node('devBarsContainer').children.entries()) {
      assert.ok(!row.innerHTML.includes('dev-bar'));
      assert.ok(row.innerHTML.includes('class="dev-metric-main mono'));
      assert.ok(row.innerHTML.includes(ranking[index].company));
      assert.match(row.innerHTML, new RegExp('dev-rank[^>]*>' + (index + 1) + '<'));
      if (mode === 'delta_upside') {
        assert.ok(row.innerHTML.includes(`报告 ${ranking[index].report_upside_str} → 当前 ${ranking[index].dynamic_base_upside_str}`));
        assert.ok(row.innerHTML.includes('class="dev-metric-unit">百分点'));
      }
    }
  }
  node('exportCsvBtn').listeners.click();
  const csv = (await csvBlob.text()).replace(/^\uFEFF/, '').split('\r\n');
  const headers = csv[0].split(',');
  assert.equal(headers[13], '最新动态Base空间');
  assert.equal(headers[14], '空间变化(百分点)');
  for (const [index, item] of data.items.entries()) {
    const cells = csv[index + 1].match(/"[^"]*"|[^,]+/g).map(s => s.replace(/^"|"$/g, ''));
    assert.equal(cells.length, headers.length);
    assert.equal(cells[13], item.dynamic_base_upside_str);
    assert.equal(Number(cells[18]), item.base);
  }
  // Distinct targets and deliberately corrupt cached fields exercise the wrong-scenario regression.
  vm.runInContext(`currentData.items = [{ ...currentData.items[0], base_price: 100,
    latest_price: 200, close_price: 200, bear: 80, base: 120, bull: 160,
    report_upside: 19.9, dynamic_base_upside: -60, dynamic_base_upside_str: '-60.0%' }]; updateDashboard()`, context);
  assert.equal(vm.runInContext('currentData.items[0].dynamic_base_upside_str', context), '-40.0%');
  assert.equal(vm.runInContext('currentData.items[0].dynamic_bear_upside_str', context), '-60.0%');
  vm.runInContext('openDrawer(currentData.items[0])', context);
  assert.match(node('drawerBody').innerHTML, /class="mono val-negative">-20\.0%/);
  vm.runInContext('currentData.items[0].latest_price = 100; updateDashboard()', context);
  assert.equal(vm.runInContext('currentData.items[0].delta_upside', context), 0);
  assert.equal(vm.runInContext('formatPrice(3.575)', context), '3.575');
  assert.equal(vm.runInContext("formatSigned(-0.00001, 1, ' 个百分点')", context), '+0.0 个百分点');
  console.log(`PASS: ${data.items.length} companies; table, chart, drawer, CSV, cache correction and boundary cases`);
}
main().catch(error => { console.error(error); process.exitCode = 1; });
