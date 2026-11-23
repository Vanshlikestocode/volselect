// Build the 12-slide VolSelect deck from slides/deck_data.json (made by slides/deck_data.py from results/).
//   python slides/deck_data.py && node slides/build_deck.js            -> VolSelect_Presentation.pptx
//   node slides/build_deck.js --single <dir>                            -> one file per slide (for previews)
// Needs pptxgenjs (npm install pptxgenjs).
const path = require("path");
const fs = require("fs");
const pptxgen = require(process.env.PPTXGENJS || "pptxgenjs");
const { applyTheme } = process.env.APPLY_THEME ? require(process.env.APPLY_THEME) : { applyTheme: null };

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "deck_data.json"), "utf8"));
const P = D.perf, F = P.full, DEV = P.development, TEST = P["hold-out"];
const pct = (x, d = 1) => (x < 0 ? "−" : "") + Math.abs(x).toFixed(d) + "%";
const num = (x, d = 2) => (x < 0 ? "−" : "") + Math.abs(x).toFixed(d);

const THEME = { name: "VolSelect", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1B2430", lt1: "FFFFFF", dk2: "13232E", lt2: "EEF4F6", accent1: "1F6F8B", accent2: "C9A227",
            accent3: "8A8A8A", accent4: "B4483C", accent5: "2E7D4F", accent6: "7FA7B5", hlink: "1F6F8B", folHlink: "5B6675" } };
const HEX = { teal: "1F6F8B", gold: "C9A227", grey: "8A8A8A", red: "B4483C", green: "2E7D4F", ink: "1B2430", muted: "5B6675",
              navy: "13232E", tint: "EEF4F6", line: "D9DEE5", white: "FFFFFF", ice: "CFE3EA" };
const W = 13.333;

function deck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.title = "VolSelect"; pres.author = "Vansh Dave, Karthik Agarwal"; pres.subject = "Design Experience project, Portfolio Management";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.defineSlideMaster({ title: "DARK", background: { color: HEX.navy },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.7, y: 2.2, w: 11.9, h: 1.6, fontFace: "Cambria",
      fontSize: 54, bold: false, color: HEX.white, valign: "bottom", align: "left", margin: 0 }, text: "" } }] });
  pres.defineSlideMaster({ title: "CONTENT", background: { color: HEX.white }, margin: [0.5, 0.6, 0.5, 0.6],
    slideNumber: { x: 12.3, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: HEX.muted, fontFace: "Calibri", align: "right" },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.4, w: 12.1, h: 0.9, fontFace: "Cambria", fontSize: 32,
        bold: true, color: HEX.ink, valign: "top", align: "left", margin: 0 }, text: "" } },
      { text: { text: "VolSelect · Design Experience project", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: HEX.muted, fontFace: "Calibri", margin: 0 } } },
    ] });
  return pres;
}

const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: "Calibri", color: HEX.ink, margin: 0, valign: "top" }, o));
const card = (s, x, y, w, h, fill = HEX.tint, name = "card") =>
  s.addShape("roundRect", { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08, objectName: name });
const dot = (s, x, y, label, fill = HEX.teal) => {
  s.addShape("ellipse", { x, y, w: 0.55, h: 0.55, fill: { color: fill }, line: { color: fill }, objectName: "step-dot" });
  T(s, label, { x, y, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: HEX.white, align: "center", valign: "middle" });
};
const stat = (s, x, y, w, value, label, color = HEX.teal) => {
  T(s, value, { x, y, w, h: 0.9, fontSize: 44, bold: true, color, fontFace: "Calibri" });
  T(s, label, { x, y: y + 0.95, w, h: 0.8, fontSize: 14, color: HEX.muted });
};
const content = (pres, title) => { const s = pres.addSlide({ masterName: "CONTENT" }); s.addText(title, { placeholder: "title" }); return s; };

const SLIDES = [
  // 1. Title
  (pres) => {
    const s = pres.addSlide({ masterName: "DARK" });
    T(s, "DESIGN EXPERIENCE PROJECT · PORTFOLIO MANAGEMENT", { x: 0.7, y: 1.4, w: 11, h: 0.4, fontSize: 14, color: HEX.ice, charSpacing: 2 });
    s.addText("VolSelect", { placeholder: "title" });
    T(s, "A volatility-aware NIFTY 50 portfolio: forecast when volatility will rise, hold the stocks most likely to hold up, and test it on data the model never saw",
      { x: 0.7, y: 4.0, w: 10.8, h: 1.2, fontSize: 20, italic: true, color: HEX.white, fontFace: "Cambria" });
    T(s, "Vansh Dave · Karthik Agarwal · Guide: Sailesh Kulkarni", { x: 0.7, y: 6.4, w: 8, h: 0.4, fontSize: 14, color: HEX.white });
    T(s, "Academic research prototype · not investment advice", { x: 8.3, y: 6.4, w: 4.4, h: 0.4, fontSize: 12, color: HEX.ice, align: "right" });
    s.addNotes("Introduce the team and the one-line idea: when market volatility is expected to rise, switch which NIFTY 50 stocks we hold, instead of going to cash. Everything shown can be reproduced with python verify.py.");
  },
  // 2. Problem
  (pres) => {
    const s = content(pres, "When volatility rises, most portfolios fall together");
    T(s, "Can a model that expects rising volatility pick the NIFTY 50 stocks that lose less, without giving up too much return in calm markets?",
      { x: 0.6, y: 1.5, w: 6.6, h: 1.4, fontSize: 20, fontFace: "Cambria", italic: true });
    const qs = ["Can India VIX, realised volatility and GARCH forecast high-volatility periods better than a naive rule?",
                "In stress, which stock traits go with beating the index?",
                "Does switching between momentum (calm) and a resilience model (stress) beat NIFTY 50 and equal weight, after costs, out of sample?"];
    qs.forEach((q, i) => { dot(s, 0.6, 3.25 + i * 1.05, String(i + 1)); T(s, q, { x: 1.35, y: 3.25 + i * 1.05, w: 5.85, h: 0.95, fontSize: 15, valign: "middle" }); });
    card(s, 7.8, 1.5, 4.9, 4.9);
    T(s, "NIFTY 50 in two sell-offs", { x: 8.15, y: 1.75, w: 4.3, h: 0.4, fontSize: 15, bold: true, color: HEX.muted });
    stat(s, 8.15, 2.35, 4.3, pct(D.crash.covid.nifty), "COVID crash, 14 Feb – 30 Apr 2020", HEX.red);
    stat(s, 8.15, 4.25, 4.3, pct(D.crash["2022"].nifty), "First half of 2022", HEX.red);
    s.addNotes(`Holding the index means taking every fall in full: NIFTY lost ${pct(D.crash.covid.nifty)} in ten weeks of 2020 and ${pct(D.crash["2022"].nifty)} in the first half of 2022 (results/table_covid.csv, table_2022.csv). Going to cash means missing rebounds. We test a middle path: stay invested, change which stocks we hold.`);
  },
  // 3. Data
  (pres) => {
    const s = content(pres, "Data: 50 stocks, the index and India VIX, daily");
    const rows = [["Source", "Yahoo Finance (yfinance), split- and dividend-adjusted; bundled as CSV with a SHA-256 manifest"],
                  ["Instruments", `All ${D.period.stocks} current NIFTY 50 stocks with sectors, NIFTY 50 index (^NSEI), India VIX (^INDIAVIX)`],
                  ["Frequency", "Daily candles: open, high, low, close, volume"],
                  ["Period", `Prices from 2012 to build features; portfolio test ${D.period.start} to ${D.period.end}`],
                  ["Split", "Build (development): 2016–2021 · Test (out-of-sample): 2022 onward"],
                  ["Cleaning", "Placeholder bars (no trading) dropped; a missing day is a no-trade day"]];
    s.addTable(rows.map(([a, b], i) => [{ text: a, options: { bold: true, color: HEX.teal, fill: { color: i % 2 ? HEX.white : HEX.tint } } },
                                        { text: b, options: { fill: { color: i % 2 ? HEX.white : HEX.tint } } }]),
      { x: 0.6, y: 1.5, w: 7.6, colW: [1.7, 5.9], fontFace: "Calibri", fontSize: 14, color: HEX.ink, rowH: 0.62, valign: "middle", border: { type: "none" } });
    card(s, 8.7, 1.5, 4.0, 4.4, HEX.tint, "bias-card");
    T(s, "Two biases we state up front", { x: 9.0, y: 1.75, w: 3.5, h: 0.4, fontSize: 16, bold: true });
    T(s, [{ text: "Survivorship: ", options: { bold: true } }, { text: "today's NIFTY 50 list is used for every year, which flatters every stock portfolio, the benchmark included.", options: { breakLine: true } },
          { text: " ", options: { breakLine: true } },
          { text: "Dividends: ", options: { bold: true } }, { text: "stocks include dividends, the NIFTY index does not (about 1.2–1.5% a year). Equal weight is the fair comparison." }],
      { x: 9.0, y: 2.3, w: 3.45, h: 3.4, fontSize: 14, color: HEX.ink });
    s.addNotes("Daily data, as the brief specifies for Portfolio Management groups. The data in data/ is exactly what produced every number; verify.py checks it against data/MANIFEST.sha256 before re-running anything.");
  },
  // 4. Method
  (pres) => {
    const s = content(pres, "Method: four steps, every day after the close");
    const steps = [["Forecast the regime", "Chance that NIFTY volatility is high over the next 10 days, from India VIX, realised volatility and GARCH(1,1). Calm < 30%, rising 30–50%, high > 50%."],
                   ["Rank all 50 stocks", "19 measures (beta, sector, trend, RSI, momentum…) as cross-stock ranks. A logistic model trained on stress days scores resilience."],
                   ["Hold the top 10", "Calm: highest 120-day momentum. Rising or high: highest resilience score. Weight = 1 / volatility, scaled to 100%. Rebalance weekly."],
                   ["Measure honestly", "0.15% cost per side, fills at the next open, against NIFTY 50 and equal-weight NIFTY 50."]];
    steps.forEach(([h, b], i) => {
      const x = 0.6 + i * 3.1;
      card(s, x, 1.6, 2.85, 4.7, i === 2 ? HEX.ice : HEX.tint, `step-${i + 1}`);
      dot(s, x + 0.3, 1.9, String(i + 1));
      T(s, h, { x: x + 0.3, y: 2.65, w: 2.3, h: 0.8, fontSize: 18, bold: true, fontFace: "Cambria" });
      T(s, b, { x: x + 0.3, y: 3.5, w: 2.3, h: 2.7, fontSize: 14 });
    });
    s.addNotes("Selection logic is the regime switch: momentum in calm markets, the resilience model when volatility is rising or high. Weighting: inverse volatility, a simple risk-parity rule with no optimiser to overfit. Rebalancing: weekly, at the open of the first session of the week. Code: volselect/regime.py, features.py, selection.py, portfolio.py.");
  },
  // 5. Out-of-sample design
  (pres) => {
    const s = content(pres, "Built on 2016–2021, tested on 2022 onward");
    const y = 2.4;
    s.addShape("rect", { x: 0.9, y: y + 0.42, w: 11.5, h: 0.06, fill: { color: HEX.line }, line: { color: HEX.line }, objectName: "timeline" });
    [["2012", "Prices start: features and first models", 0.9, HEX.grey], ["2016", "Portfolio test starts", 3.9, HEX.teal],
     ["2022", "Out-of-sample test starts", 8.0, HEX.gold], [D.period.end.slice(-8), "End of data; live record follows", 11.9, HEX.grey]]
      .forEach(([yr, lab, x, c]) => {
        s.addShape("ellipse", { x: x - 0.15, y: y + 0.3, w: 0.3, h: 0.3, fill: { color: c }, line: { color: c }, objectName: `mark-${yr}` });
        T(s, yr, { x: x - 0.9, y: y - 0.35, w: 1.8, h: 0.5, fontSize: 20, bold: true, align: "center", color: c });
        T(s, lab, { x: x - 1.0, y: y + 0.75, w: 2.0, h: 0.8, fontSize: 13, align: "center", color: HEX.muted });
      });
    const pts = [["Walk-forward", "Every 1 January the regime model, GARCH and stock models are refitted on data up to the previous 31 December, then used unchanged for that year."],
                 ["Fixed in advance", "10 stocks, weekly rebalance, regime cut-offs, horizons and costs were set while working on 2016–2021."],
                 ["No look-ahead", "Signals at the close, trades at the next open. Tests change future prices and check that past results do not move."]];
    pts.forEach(([h, b], i) => { const x = 0.6 + i * 4.1; card(s, x, 4.2, 3.85, 2.3); T(s, h, { x: x + 0.3, y: 4.45, w: 3.3, h: 0.45, fontSize: 17, bold: true });
                                  T(s, b, { x: x + 0.3, y: 4.95, w: 3.3, h: 1.45, fontSize: 14 }); });
    s.addNotes("This is the brief's requirement 5: build on one period, test on a separate later period. Models only ever see the past; 2022 onward is reported separately as the honest test. The look-ahead tests are in tests/test_vs.py.");
  },
  // 6. Results table
  (pres) => {
    const s = content(pres, `Full walk-forward results, ${D.period.start.slice(-4)}–2026`);
    const head = ["Approach", "Annual return", "Volatility", "Sharpe", "Max drawdown", "Beta", "Alpha a year"].map((t, i) =>
      ({ text: t, options: { bold: true, color: HEX.white, fill: { color: HEX.teal }, align: i ? "right" : "left" } }));
    const rows = [["VolSelect (regime switch)", "volselect"], ["Resilience model only", "resilience"], ["Momentum only", "momentum"],
                  ["Equal-weight NIFTY 50", "equal_weight"], ["NIFTY 50 buy and hold", "nifty"]].map(([n, k], i) => {
      const r = F[k], o = { fill: { color: i === 0 ? HEX.ice : i % 2 ? HEX.white : HEX.tint }, bold: i === 0 };
      return [{ text: n, options: o }, ...[pct(r["CAGR %"]), pct(r["Volatility %"]), num(r.Sharpe), pct(r["Max drawdown %"]), num(r.Beta), pct(r["Alpha % a year"])]
        .map((t) => ({ text: t, options: Object.assign({ align: "right" }, o) }))];
    });
    s.addTable([head, ...rows], { x: 0.6, y: 1.5, w: 12.1, colW: [3.4, 1.55, 1.4, 1.2, 1.75, 1.2, 1.6], fontFace: "Calibri", fontSize: 15,
      color: HEX.ink, rowH: 0.55, valign: "middle", border: { type: "none" } });
    T(s, [{ text: "Read it this way: ", options: { bold: true } },
          { text: `VolSelect beat NIFTY (${pct(F.volselect["CAGR %"])} against ${pct(F.nifty["CAGR %"])} a year) with a smaller worst fall, but equal weight earned more (${pct(F.equal_weight["CAGR %"])}) with a higher Sharpe. The resilience model has the lowest beta (${num(F.resilience.Beta)}). Alpha against NIFTY is inflated by dividends: equal weight's own ${pct(F.equal_weight["Alpha % a year"])} shows the bias.` }],
      { x: 0.6, y: 5.05, w: 12.1, h: 1.6, fontSize: 15 });
    s.addNotes("Metrics required by the brief: annualised return, volatility, Sharpe (6.5% risk-free rate), maximum drawdown, beta and Jensen's alpha against NIFTY 50. All after 0.15% cost per side. Source: results/table_full.csv; formulas in volselect/metrics.py.");
  },
  // 7. Value chart
  (pres) => {
    const s = content(pres, "Portfolio value against the benchmarks");
    const c = D.chart;
    s.addChart("line", [{ name: "VolSelect", labels: c.labels, values: c.volselect }, { name: "Equal-weight NIFTY 50", labels: c.labels, values: c.equal_weight },
                        { name: "NIFTY 50", labels: c.labels, values: c.nifty }],
      { x: 0.6, y: 1.4, w: 8.6, h: 5.3, chartColors: [HEX.teal, HEX.gold, HEX.grey], lineSize: 2, lineDataSymbol: "none",
        showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt", catAxisLabelFrequency: 52, catAxisLabelFontSize: 11,
        valAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted,
        valAxisTitle: "Rs lakh", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: HEX.muted, valGridLine: { color: "E6E9EE", size: 0.5 },
        catGridLine: { style: "none" }, valAxisMinVal: 5, objectName: "value-chart" });
    card(s, 9.6, 1.5, 3.1, 5.1);
    T(s, "Rs 10 lakh became", { x: 9.9, y: 1.75, w: 2.6, h: 0.4, fontSize: 14, color: HEX.muted });
    [["VolSelect", c.volselect.at(-1), HEX.teal], ["Equal weight", c.equal_weight.at(-1), HEX.gold], ["NIFTY 50", c.nifty.at(-1), HEX.grey]]
      .forEach(([n, v, col], i) => { T(s, `Rs ${v.toFixed(1)} lakh`, { x: 9.9, y: 2.25 + i * 1.3, w: 2.6, h: 0.6, fontSize: 26, bold: true, color: col });
                                       T(s, n, { x: 9.9, y: 2.85 + i * 1.3, w: 2.6, h: 0.35, fontSize: 13, color: HEX.muted }); });
    s.addNotes("Weekly values of Rs 10 lakh invested in January 2016 (results/equity_curves.csv). VolSelect stayed within about 12% of equal weight through 2024, then fell behind in 2025 and 2026. Both stock portfolios pull ahead of NIFTY partly because of dividends and survivorship.");
  },
  // 8. Out of sample
  (pres) => {
    const s = content(pres, "The honest test: 2022 onward, data the model never saw");
    const blocks = [["VolSelect", DEV.volselect["CAGR %"], TEST.volselect["CAGR %"], HEX.teal], ["Equal-weight NIFTY 50", DEV.equal_weight["CAGR %"], TEST.equal_weight["CAGR %"], HEX.gold],
                    ["NIFTY 50", DEV.nifty["CAGR %"], TEST.nifty["CAGR %"], HEX.grey]];
    blocks.forEach(([n, a, b, col], i) => {
      const x = 0.6 + i * 4.1; card(s, x, 1.5, 3.85, 3.2);
      T(s, n, { x: x + 0.3, y: 1.7, w: 3.3, h: 0.4, fontSize: 16, bold: true, color: col });
      T(s, "Build 2016–21", { x: x + 0.3, y: 2.25, w: 1.6, h: 0.35, fontSize: 13, color: HEX.muted });
      T(s, "Test 2022+", { x: x + 1.95, y: 2.25, w: 1.6, h: 0.35, fontSize: 13, color: HEX.muted });
      T(s, pct(a), { x: x + 0.3, y: 2.6, w: 1.6, h: 0.8, fontSize: 32, bold: true, color: HEX.muted });
      T(s, pct(b), { x: x + 1.95, y: 2.6, w: 1.6, h: 0.8, fontSize: 32, bold: true, color: col });
      T(s, "a year", { x: x + 0.3, y: 3.45, w: 3.3, h: 0.35, fontSize: 13, color: HEX.muted });
      T(s, `Test max drawdown ${pct(i === 0 ? TEST.volselect["Max drawdown %"] : i === 1 ? TEST.equal_weight["Max drawdown %"] : TEST.nifty["Max drawdown %"])}`,
        { x: x + 0.3, y: 3.95, w: 3.3, h: 0.4, fontSize: 14 });
    });
    T(s, [{ text: "What this means: ", options: { bold: true } },
          { text: `out of sample VolSelect still beat NIFTY (${pct(TEST.volselect["CAGR %"])} against ${pct(TEST.nifty["CAGR %"])}) but trailed equal weight by a wide margin, with a deeper worst fall than NIFTY. The edge seen while building did not carry over: exactly what the literature on backtest overfitting warns about, and why we report both periods.` }],
      { x: 0.6, y: 5.05, w: 12.1, h: 1.6, fontSize: 15 });
    s.addNotes("Sources: results/table_development.csv and results/table_hold-out.csv. Annual returns (CAGR) after costs. Be ready to say: the build-period number is what a careless backtest would advertise; the test number is the honest one.");
  },
  // 9. Crashes
  (pres) => {
    const s = content(pres, "Where it works: it lost less in both sell-offs");
    const k = [["VolSelect", "volselect"], ["Resilience model", "resilience"], ["Equal weight", "equal_weight"], ["NIFTY 50", "nifty"]];
    s.addChart("bar", k.map(([n, key]) => ({ name: n, labels: ["COVID crash, Feb–Apr 2020", "2022 sell-off, Jan–Jun"], values: [D.crash.covid[key], D.crash["2022"][key]] })),
      { x: 0.6, y: 1.4, w: 8.0, h: 5.3, barDir: "col", barGrouping: "clustered", chartColors: [HEX.teal, "7FA7B5", HEX.gold, HEX.grey],
        showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelColor: HEX.ink,
        showLegend: true, legendPos: "t", legendFontSize: 12, legendFontFace: "+mn-lt", catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
        valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted,
        valAxisTitle: "Return over the period %", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: HEX.muted,
        valGridLine: { color: "E6E9EE", size: 0.5 }, catGridLine: { style: "none" }, objectName: "crash-chart" });
    card(s, 9.0, 1.5, 3.7, 5.1);
    T(s, "Why", { x: 9.3, y: 1.75, w: 3.1, h: 0.4, fontSize: 16, bold: true });
    T(s, [{ text: `Resilience model beta ${num(TEST.resilience.Beta)} out of sample`, options: { bullet: true, breakLine: true } },
          { text: "Defensive sectors and stocks that are not overbought kept beating NIFTY in stress after 2022", options: { bullet: true, breakLine: true } },
          { text: "Recent big winners fall hardest when the market turns", options: { bullet: true } }],
      { x: 9.3, y: 2.25, w: 3.15, h: 4.1, fontSize: 14, paraSpaceAfter: 10 });
    s.addNotes(`COVID crash: VolSelect ${pct(D.crash.covid.volselect)}, NIFTY ${pct(D.crash.covid.nifty)}, equal weight ${pct(D.crash.covid.equal_weight)}. 2022 H1: resilience ${pct(D.crash["2022"].resilience)}, NIFTY ${pct(D.crash["2022"].nifty)} (results/table_covid.csv, table_2022.csv). Indicator check: results/overfitting_ic.csv; beta: table_hold-out.csv.`);
  },
  // 10. Forecast and costs
  (pres) => {
    const s = content(pres, "Where it does not: the forecast and the costs");
    card(s, 0.6, 1.5, 5.9, 5.1);
    T(s, "Volatility forecast, 2022+ test", { x: 0.9, y: 1.75, w: 5.3, h: 0.4, fontSize: 17, bold: true });
    stat(s, 0.9, 2.3, 2.5, pct(D.forecast.hit_rate, 0), `days right (naive rule ${pct(D.forecast.naive_hit_rate, 0)})`);
    stat(s, 3.6, 2.3, 2.6, pct(D.forecast.recall, 0), `of high-volatility days caught (naive ${pct(D.forecast.naive_recall, 0)})`, HEX.red);
    T(s, `When it says "high" it is right ${pct(D.forecast.precision, 0)} of the time, but it misses most spikes, so the portfolio is often in the wrong mode early in a sell-off.`,
      { x: 0.9, y: 4.6, w: 5.3, h: 1.7, fontSize: 14 });
    card(s, 6.8, 1.5, 5.9, 5.1);
    T(s, "Before and after costs (annual return)", { x: 7.1, y: 1.75, w: 5.3, h: 0.4, fontSize: 17, bold: true });
    s.addTable([[{ text: "", options: { fill: { color: HEX.tint } } }, ...["Gross 2016–21", "Gross 2022+", "After costs 2022+"].map((t) => ({ text: t, options: { bold: true, align: "right", fill: { color: HEX.tint } } }))],
                [{ text: "VolSelect", options: { bold: true, color: HEX.teal } }, ...[D.gross.volselect.dev, D.gross.volselect.test, TEST.volselect["CAGR %"]].map((v) => ({ text: pct(v), options: { align: "right" } }))],
                [{ text: "Equal weight", options: { bold: true, color: HEX.gold } }, ...[D.gross.equal_weight.dev, D.gross.equal_weight.test, TEST.equal_weight["CAGR %"]].map((v) => ({ text: pct(v), options: { align: "right" } }))]],
      { x: 7.1, y: 2.35, w: 5.3, colW: [1.4, 1.3, 1.2, 1.4], fontFace: "Calibri", fontSize: 14, color: HEX.ink, rowH: 0.5, valign: "middle", fill: { color: HEX.white }, border: { type: "none" } });
    T(s, `Before any cost VolSelect led equal weight while building, and trailed it from 2022 even with no cost. Weekly rebalancing turns the portfolio over about ${F.volselect["Turnover (x/yr)"].toFixed(0)} times a year.`,
      { x: 7.1, y: 4.3, w: 5.3, h: 2.0, fontSize: 14 });
    s.addNotes("Forecast accuracy: results/forecast_accuracy.csv (hit rate, precision, recall against a naive 'next 10 days like the last 10' rule). Costs: results/cost_sensitivity.csv at 0%, 0.05%, 0.15% and 0.30% per side.");
  },
  // 11. Limitations
  (pres) => {
    const s = content(pres, "Limitations");
    const L = [["Survivorship bias", "Today's NIFTY 50 list for every year inflates all stock portfolios."], ["Dividends", "Stocks are total return, the index is not: alpha against NIFTY is overstated."],
               ["Short test", "2022 onward is under five years and mostly one market regime."], ["Forecast recall", "Most high-volatility spells are missed."],
               ["Turnover", `The portfolio turns over about ${F.volselect["Turnover (x/yr)"].toFixed(0)} times a year; costs eat any edge.`], ["Daily data", "Trades at the next open; intraday moves are not modelled."]];
    L.forEach(([h, b], i) => { const x = 0.6 + (i % 3) * 4.1, y = 1.55 + Math.floor(i / 3) * 2.55; card(s, x, y, 3.85, 2.3);
      T(s, h, { x: x + 0.3, y: y + 0.25, w: 3.3, h: 0.45, fontSize: 18, bold: true, fontFace: "Cambria" }); T(s, b, { x: x + 0.3, y: y + 0.85, w: 3.3, h: 1.3, fontSize: 15 }); });
    s.addNotes("Next steps for each: point-in-time index members; a total-return NIFTY benchmark; a longer live record; a forecast tuned for recall; monthly rebalancing or a buffer before replacing a stock; intraday data.");
  },
  // 12. Conclusion and live demo
  (pres) => {
    const s = pres.addSlide({ masterName: "DARK" });
    T(s, "WHAT WE TAKE FROM THIS", { x: 0.7, y: 0.6, w: 11, h: 0.4, fontSize: 14, color: HEX.ice, charSpacing: 2 });
    T(s, "Selection by resilience protects in sell-offs, but it does not beat simply holding all 50 stocks", { x: 0.7, y: 1.1, w: 11.9, h: 1.4, fontSize: 30, fontFace: "Cambria", color: HEX.white });
    const pts = [["Works", `Lost less than NIFTY and equal weight in the COVID crash and the 2022 sell-off; resilience beta ${num(TEST.resilience.Beta)} out of sample`],
                 ["Does not", `Trails equal weight from 2022, even before costs (${pct(D.gross.volselect.test)} vs ${pct(D.gross.equal_weight.test)} gross)`],
                 ["Weak link", `The volatility forecast catches only ${pct(D.forecast.recall, 0)} of high-volatility days`]];
    pts.forEach(([h, b], i) => { const x = 0.7 + i * 4.1; s.addShape("roundRect", { x, y: 2.9, w: 3.85, h: 2.0, fill: { color: "1C3342" }, line: { color: "1C3342" }, rectRadius: 0.08, objectName: `take-${i + 1}` });
      T(s, h, { x: x + 0.3, y: 3.1, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: HEX.ice }); T(s, b, { x: x + 0.3, y: 3.6, w: 3.3, h: 1.2, fontSize: 14, color: HEX.white }); });
    T(s, "LIVE DEMO", { x: 0.7, y: 5.35, w: 4, h: 0.4, fontSize: 14, color: HEX.ice, charSpacing: 2 });
    T(s, [{ text: "streamlit run volselect_app.py", options: { fontFace: "Courier New", color: HEX.white, breakLine: true } },
          { text: "Today's regime and ranking · the live paper-trading record · every result re-run with python verify.py", options: { color: HEX.ice } }],
      { x: 0.7, y: 5.8, w: 11.9, h: 1.0, fontSize: 15 });
    s.addNotes("Demo order (2 minutes): 1) Overview: today's regime and the honest evidence. 2) Live market: the regime, the ranking, the target portfolio for the next rebalance and the forward record. 3) Research: value chart and the 2022+ table. 4) In a terminal: python verify.py to show every number reproduces.");
  },
];

async function main() {
  const single = process.argv.indexOf("--single");
  if (single > -1) {
    const dir = process.argv[single + 1];
    for (let i = 0; i < SLIDES.length; i++) { const p = deck(); SLIDES[i](p); await p.writeFile({ fileName: path.join(dir, `slide-${String(i + 1).padStart(2, "0")}.pptx`) }); }
    return;
  }
  const pres = deck();
  SLIDES.forEach((f) => f(pres));
  const out = path.join(__dirname, "..", "VolSelect_Presentation.pptx");
  await pres.writeFile({ fileName: out });
  if (applyTheme) await applyTheme(out, THEME);
  console.log(`wrote ${out} (${SLIDES.length} slides)`);
}
main();
