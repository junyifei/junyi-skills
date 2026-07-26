// custom.mjs — 兜底适配器：用户自带路径，现场推断字段
// 内置 5 个适配器都没命中、或用户用的是别的工具时：
//   1. SKILL.md 让 agent 问用户「你的 AI 对话记录在哪？导出文件还是某工具的本地存储？」
//   2. 用户给路径 → 用 --custom-path 调本适配器，自动尝试推断常见字段名；
//   3. 推断不出来 → 如实报「无法识别，请整理成 {role, timestamp, content} 的 jsonl」。
//
// 支持输入：单个 .jsonl（逐行 JSON）、单个 .json（数组或 {records:[...]}）、或一个目录（递归找 .jsonl）。
import fs from 'node:fs';
import path from 'node:path';
import { extractText, makeRecord, toLocal, hasStrongSelf, hasSoftSelf } from '../lib.mjs';

// 常见字段名推断
function pickRole(o) {
  const r = o.role || o.sender || o.from || o.speaker || (o.message && o.message.role) || (o.payload && o.payload.role);
  if (!r) return null;
  const s = String(r).toLowerCase();
  if (['user', 'human', 'me', '用户', '我'].includes(s)) return 'user';
  if (['assistant', 'ai', 'bot', 'model', 'gpt', '助手'].includes(s)) return 'assistant';
  return s === 'user' || s === 'assistant' ? s : (s.includes('user') ? 'user' : s.includes('assist') ? 'assistant' : null);
}
function pickContent(o) {
  if (typeof o.content === 'string') return o.content;
  if (o.content) return extractText(o.content);
  if (typeof o.text === 'string') return o.text;
  if (o.message) return typeof o.message.content === 'string' ? o.message.content : extractText(o.message.content);
  if (o.payload && o.payload.content) return extractText(o.payload.content);
  return '';
}
function pickTs(o) {
  return o.timestamp || o.time || o.created_at || o.createdAt || o.ts || o.date || (o.message && o.message.timestamp) || null;
}

function parseRecords(raw, fp, windowSet, out, state) {
  for (const o of raw) {
    const sourceLine = ++state.line;
    if (!o || typeof o !== 'object') continue;
    const role = pickRole(o);
    const content = pickContent(o);
    if (!role || !content || !content.trim()) { out.unparsed++; continue; }
    if (role !== 'user' && role !== 'assistant') continue;
    if (hasStrongSelf(content)) continue;
    if (hasSoftSelf(content)) continue;
    const ts = pickTs(o);
    if (!ts) { out.missing_timestamp++; continue; }
    const { date, local } = toLocal(ts);
    if (!date) { out.invalid_timestamp++; continue; }
    if (windowSet && !windowSet.has(date)) { out.outside_window++; continue; }
    out.records.push(makeRecord({
      source: 'custom', agent_id: o.agent || o.agent_id || 'custom', session_id: o.session_id || o.session || o.conversation_id || state.session,
      role, content, ts, local, date, fp, line: sourceLine, uuid: o.id || o.uuid || o.record_id,
    }));
  }
}

export default {
  source: 'custom',
  label: 'Custom（自带路径）',
  status: 'supported',
  detect({ customPath }) {
    return { available: !!customPath && fs.existsSync(customPath), paths: customPath ? [customPath] : [], note: customPath ? '' : '未提供 --custom-path' };
  },
  collect({ customPath, windowSet }) {
    const out = {
      source: this.source, label: this.label, status: this.status, available: !!customPath,
      paths: customPath ? [customPath] : [], records: [], files: 0, self_skipped: 0,
      unparsed: 0, missing_timestamp: 0, invalid_timestamp: 0, outside_window: 0, note: '',
    };
    if (!customPath) { out.note = '未提供 --custom-path，custom 适配器跳过'; return out; }
    if (!fs.existsSync(customPath)) { out.note = `路径不存在：${customPath}`; out.available = false; return out; }
    const state = { line: 0, session: 'custom-session' };
    const files = [];
    const st = fs.statSync(customPath);
    if (st.isDirectory()) {
      const walk = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (e.name.endsWith('.jsonl') || e.name.endsWith('.json')) files.push(p); } };
      walk(customPath);
    } else { files.push(customPath); }
    out.files = files.length;
    for (const fp of files) {
      let txt; try { txt = fs.readFileSync(fp, 'utf8'); } catch { continue; }
      if (fp.endsWith('.jsonl')) {
        const raw = txt.split('\n').map((l) => l.trim()).filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
        parseRecords(raw, fp, windowSet, out, state);
      } else {
        let j; try { j = JSON.parse(txt); } catch { out.note = `无法解析 JSON：${fp}`; continue; }
        const raw = Array.isArray(j) ? j : (Array.isArray(j.records) ? j.records : (Array.isArray(j.messages) ? j.messages : null));
        if (!raw) { out.note = `无法识别结构（既非数组也无 records/messages 字段）：${fp}`; continue; }
        parseRecords(raw, fp, windowSet, out, state);
      }
    }
    const excluded = [];
    if (out.unparsed) excluded.push(`字段无法识别 ${out.unparsed} 条`);
    if (out.missing_timestamp) excluded.push(`缺时间戳 ${out.missing_timestamp} 条`);
    if (out.invalid_timestamp) excluded.push(`时间戳无效 ${out.invalid_timestamp} 条`);
    if (out.outside_window) excluded.push(`窗口外 ${out.outside_window} 条`);
    if (excluded.length) out.note = (out.note ? out.note + ' ' : '') + `已排除：${excluded.join('，')}。`;
    if (out.records.length === 0) {
      out.note = (out.note ? out.note + ' ' : '') + '没有可用于本周复盘的记录。Custom 记录必须包含可解析的 role、content 与 timestamp；建议整理成逐行 JSON：{"role":"user|assistant","timestamp":"ISO","content":"..."}';
    }
    return out;
  },
};
