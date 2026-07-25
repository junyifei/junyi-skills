#!/usr/bin/env node
/**
 * collect.mjs — ai-weekly-review 抓取 + 标准化 + 按天分块（Step 1-3）
 *
 * 不调用任何模型。纯本地脚本。蒸馏（Step 4-5）由 skill 的 agent 完成。
 *
 * 用法:
 *   node collect.mjs                         # 默认过去 7 天（本地时区）
 *   node collect.mjs --days 7
 *   node collect.mjs --since 2026-06-19 --until 2026-06-25
 *   node collect.mjs --out ~/周报输出          # 输出目录（默认 ./ai-weekly-review-output）
 *   node collect.mjs --adapters claude_code,openclaw,codex   # 只跑指定来源
 *   node collect.mjs --custom-path ~/导出/我的对话.jsonl       # 启用 custom 兜底
 *
 * 产出（<out>/<YYYY-Wxx>/）:
 *   manifest.md            # 窗口 / 适配器报告 / 各天 chunk 数 / agent 清单
 *   adapters-report.json   # 各适配器命中/未支持/记录数（机器可读）
 *   records.cleaned.jsonl  # 清洗去重后的统一记录
 *   days/<YYYY-MM-DD>/chunk_NNN.md   # 逐日 chunk（供逐日蒸馏）
 */
import fs from 'node:fs';
import path from 'node:path';
import { HOME, windowDates, isoWeekId } from './lib.mjs';
import claudeCode from './adapters/claude-code.mjs';
import openclaw from './adapters/openclaw.mjs';
import codex from './adapters/codex.mjs';
import hermes from './adapters/hermes.mjs';
import workbuddy from './adapters/workbuddy.mjs';
import custom from './adapters/custom.mjs';

// ---- 解析参数 ----
function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === '--days') a.days = argv[++i];
    else if (t === '--since') a.since = argv[++i];
    else if (t === '--until') a.until = argv[++i];
    else if (t === '--out') a.out = argv[++i];
    else if (t === '--adapters') a.adapters = argv[++i];
    else if (t === '--custom-path') a.customPath = argv[++i];
    else if (/^\d+$/.test(t) && !a.days) a.days = t; // 位置参数当 days
  }
  return a;
}
const args = parseArgs(process.argv.slice(2));
const days = args.days ? parseInt(args.days, 10) : 7;
const dates = windowDates({ days, since: args.since, until: args.until });
const windowSet = new Set(dates);
const prefilterDays = (args.since && args.until) ? 400 : days + 2; // mtime 预筛宽容度
const weekId = isoWeekId(dates[dates.length - 1]);
const outRoot = args.out ? path.resolve(args.out.replace(/^~(?=$|\/)/, HOME)) : path.resolve(process.cwd(), 'ai-weekly-review-output');
const OUT = path.join(outRoot, weekId);
const DAYS_DIR = path.join(OUT, 'days');
fs.mkdirSync(DAYS_DIR, { recursive: true });

// ---- 抓取层：跑各适配器 ----
const BUILTIN = [claudeCode, openclaw, codex, hermes, workbuddy];
const enabled = args.adapters ? new Set(args.adapters.split(',').map((s) => s.trim())) : null;
const ctx = { home: HOME, windowSet, prefilterDays, customPath: args.customPath };

const adapterReports = [];
const allRecords = [];
function runAdapter(ad) {
  if (enabled && !enabled.has(ad.source)) return;
  let r;
  try { r = ad.collect(ctx); }
  catch (e) { r = { source: ad.source, label: ad.label, status: ad.status, available: false, paths: [], records: [], files: 0, self_skipped: 0, note: '采集出错: ' + e.message }; }
  adapterReports.push({
    source: r.source, label: r.label, status: r.status, available: !!r.available,
    files: r.files || 0, self_skipped: r.self_skipped || 0, records: r.records.length,
    paths: r.paths || [], note: r.note || '',
  });
  allRecords.push(...r.records);
}
for (const ad of BUILTIN) runAdapter(ad);
if (args.customPath) runAdapter(custom); // custom 仅在显式给路径时跑

// ---- 标准化层：跨源去重 + 去工具独白 + 超长截断（角色过滤/自指排除已在 scanJsonl 内完成）----
const seen = new Set();
const cleaned = [];
for (const r of allRecords) {
  if (r.role !== 'user' && r.role !== 'assistant') continue;
  if (seen.has(r.content_hash)) continue;
  const stripped = r.content.replace(/\[tool_(use|result)[^\]]*\]/g, '').trim();
  if (!stripped) continue; // 纯工具独白
  if (r.content.length > 2000) {
    r.content_full_len = r.content.length;
    r.content = r.content.slice(0, 2000) + `\n…[truncated, full ${r.content.length} chars @ ${path.basename(r.source_path)}:${r.line_no}]`;
  }
  seen.add(r.content_hash);
  cleaned.push(r);
}
cleaned.sort((a, b) => new Date(a.timestamp_utc) - new Date(b.timestamp_utc));
fs.writeFileSync(path.join(OUT, 'records.cleaned.jsonl'), cleaned.map((r) => JSON.stringify(r)).join('\n') + (cleaned.length ? '\n' : ''));

// ---- 按天分组 → 每天内按 源>agent>session>时间 分块（≤10000 字符，不跨 group 合并）----
const MAX_CHARS = 10000;
const byDay = new Map();
for (const r of cleaned) {
  const d = r.local_date || 'unknown';
  if (!byDay.has(d)) byDay.set(d, []);
  byDay.get(d).push(r);
}
function chunkDay(recs) {
  const groups = new Map();
  for (const r of recs) {
    const k = `${r.source}|${r.agent_id}|${r.session_id}`;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(r);
  }
  const chunks = [];
  for (const [, gr] of groups) {
    let buf = [], len = 0;
    for (const r of gr) {
      const piece = r.content.length + 200;
      if (len + piece > MAX_CHARS && buf.length) { chunks.push(buf); buf = []; len = 0; }
      buf.push(r); len += piece;
    }
    if (buf.length) chunks.push(buf); // 每个 group 结束强制 flush
  }
  return chunks;
}
function renderChunk(ch, idx) {
  const f = ch[0];
  const out = [
    `# Chunk ${String(idx).padStart(3, '0')}`, '',
    `- source: ${f.source}`,
    `- agent: ${f.agent_id}`,
    `- session: ${f.session_id}`,
    `- records: ${ch.length}`,
    `- time_range: ${f.timestamp_local} → ${ch[ch.length - 1].timestamp_local}`,
    '', '---', '',
  ];
  for (const r of ch) {
    out.push(`### [${r.role}] ${r.timestamp_local}  (rec ${String(r.record_id).slice(0, 8)})`, '', r.content, '');
  }
  return out.join('\n');
}

const perDay = [];
for (const date of dates) {
  const recs = byDay.get(date) || [];
  const dir = path.join(DAYS_DIR, date);
  fs.mkdirSync(dir, { recursive: true });
  const chunks = chunkDay(recs);
  chunks.forEach((ch, i) => fs.writeFileSync(path.join(dir, `chunk_${String(i + 1).padStart(3, '0')}.md`), renderChunk(ch, i + 1)));
  perDay.push({ date, records: recs.length, chunks: chunks.length });
}

// ---- agent 清单（供「多 agent 工作概览」是否成节决策）----
const agentMap = new Map();
for (const r of cleaned) {
  const k = `${r.source}/${r.agent_id}`;
  agentMap.set(k, (agentMap.get(k) || 0) + 1);
}

// ---- 写报告 ----
fs.writeFileSync(path.join(OUT, 'adapters-report.json'), JSON.stringify(adapterReports, null, 2));

const totalRecords = cleaned.length;
const isEmpty = totalRecords === 0;
const manifest = [
  `# ai-weekly-review 抓取 manifest`, '',
  `- 周编号: ${weekId}`,
  `- 时间窗口（本地时区）: ${dates[0]} ~ ${dates[dates.length - 1]}（${dates.length} 天）`,
  `- 生成时间: ${new Date().toISOString()}`,
  `- 输出目录: ${OUT}`,
  `- 状态: ${isEmpty ? 'empty-week（窗口内无有效对话）' : 'chunked'}`,
  '',
  `## 适配器报告（诚实标注）`,
  `| 来源 | 状态 | 命中 | 文件 | 自指排除 | 记录数 | 说明 |`,
  `|------|------|------|------|----------|--------|------|`,
  ...adapterReports.map((a) => `| ${a.label} | ${a.status} | ${a.available ? '是' : '否'} | ${a.files} | ${a.self_skipped} | ${a.records} | ${(a.note || '').replace(/\|/g, '/').slice(0, 80)} |`),
  '',
  `## 各 agent 记录数（用于多 agent 工作概览）`,
  agentMap.size <= 1 ? '- 仅 1 个 agent（或无）→ 周报「各 agent 本周工作」一节自动省略' : '',
  ...Array.from(agentMap.entries()).map(([k, n]) => `- ${k}: ${n} 条`),
  '',
  `## 各天 chunk 状态`,
  ...perDay.map((d) => `- ${d.date}: ${d.records} 条记录 → ${d.chunks} chunk`),
  '',
  `## 下一步（交给 skill 的 agent）`,
  isEmpty
    ? `- 窗口内无有效对话，生成空周报（empty-week）并如实说明扫描范围。`
    : `- 逐日读 days/<date>/chunk_*.md 蒸馏三类候选 → 汇周去重印证 → 出《本周记录》+《本周内容素材》。`,
  '',
].filter((l) => l !== '').join('\n');
fs.writeFileSync(path.join(OUT, 'manifest.md'), manifest);

// ---- 控制台摘要 ----
console.log(JSON.stringify({
  week: weekId,
  window: `${dates[0]} ~ ${dates[dates.length - 1]}`,
  out_dir: OUT,
  adapters: adapterReports.map((a) => ({ source: a.source, status: a.status, available: a.available, records: a.records })),
  agents: agentMap.size,
  cleaned_records: totalRecords,
  total_chunks: perDay.reduce((s, d) => s + d.chunks, 0),
  status: isEmpty ? 'empty-week' : 'chunked',
}, null, 2));
