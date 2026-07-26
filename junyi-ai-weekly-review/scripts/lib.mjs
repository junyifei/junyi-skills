// lib.mjs — ai-weekly-review 共享工具（被 collect.mjs 与各适配器复用）
// 纯本地，无网络，无模型调用。
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import os from 'node:os';

export const HOME = os.homedir();
export const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');

// ---- 进入模型上下文前的尽力脱敏 ----
// records.cleaned.jsonl 保留本地原文以便追溯；day chunks 只写脱敏后的文本。
// 这里只处理高置信度凭据、显式账号字段与金额，不声称覆盖所有个人信息。
export function redactForModel(input) {
  let text = String(input || '');
  let count = 0;
  const apply = (pattern, replacement) => {
    text = text.replace(pattern, (...args) => {
      count++;
      return typeof replacement === 'function' ? replacement(...args) : replacement;
    });
  };

  apply(/\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b/gi, 'Bearer [REDACTED]');
  apply(/\b(?:sk|rk)-[A-Za-z0-9_-]{12,}\b|\bgh[pousr]_[A-Za-z0-9_]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b|\bxox[baprs]-[A-Za-z0-9-]{10,}\b/g, '[REDACTED_SECRET]');
  apply(/((?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|app[_ -]?secret|password|passwd|cookie|authorization|账号|账户)\s*[:=：]\s*)(?!Bearer\b)(["']?)([^\s,"';，；]{4,})\2/gi, (_match, prefix) => `${prefix}[REDACTED]`);
  apply(/(?:¥|￥|\$|€|£)\s?\d[\d,]*(?:\.\d+)?/g, '[REDACTED_AMOUNT]');
  apply(/\d[\d,]*(?:\.\d+)?\s*(?:万元|元|块钱|人民币|美元|美金|CNY|RMB|USD|EUR)/gi, '[REDACTED_AMOUNT]');
  return { text, count };
}

// ---- 本地时区日期（用机器本地时区，不写死，符合设计「本地时区过去 7 天」）----
export function localDateStr(d = new Date()) {
  return new Intl.DateTimeFormat('en-CA', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(d);
}
export function toLocal(iso) {
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return { date: null, local: null };
    const s = new Intl.DateTimeFormat('en-CA', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    }).format(d);
    return { date: s.slice(0, 10), local: s.replace(',', '') };
  } catch { return { date: null, local: null }; }
}

// 生成时间窗口内的本地日期列表（升序）
export function windowDates({ days = 7, since = null, until = null } = {}) {
  const out = [];
  const end = until ? new Date(until + 'T12:00:00') : new Date();
  if (since) {
    const cur = new Date(since + 'T12:00:00');
    while (cur <= end) { out.push(localDateStr(cur)); cur.setDate(cur.getDate() + 1); }
  } else {
    const cur = new Date(end);
    for (let i = 0; i < days; i++) { out.push(localDateStr(cur)); cur.setDate(cur.getDate() - 1); }
    out.reverse();
  }
  return out;
}

// ISO 周编号 YYYY-Wxx（用窗口末日）
export function isoWeekId(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  const dt = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = (dt.getUTCDay() + 6) % 7;
  dt.setUTCDate(dt.getUTCDate() - dayNum + 3);
  const firstThu = new Date(Date.UTC(dt.getUTCFullYear(), 0, 4));
  const week = 1 + Math.round(((dt - firstThu) / 86400000 - 3 + ((firstThu.getUTCDay() + 6) % 7)) / 7);
  return `${dt.getUTCFullYear()}-W${String(week).padStart(2, '0')}`;
}

// ---- 提取文本：兼容 string / block list（claude text、codex input_text/output_text、thinking、工具块）----
export function extractText(content) {
  if (content == null) return '';
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    const parts = [];
    for (const b of content) {
      if (typeof b === 'string') { parts.push(b); continue; }
      if (b && typeof b === 'object') {
        if (typeof b.text === 'string' && (b.type === 'text' || b.type === 'input_text' || b.type === 'output_text')) parts.push(b.text);
        else if (b.type === 'thinking' && typeof b.thinking === 'string') parts.push('[thinking] ' + b.thinking);
        else if (b.type === 'tool_use') parts.push(`[tool_use:${b.name || '?'}]`);
        else if (b.type === 'tool_result') {
          const t = typeof b.content === 'string' ? b.content : extractText(b.content);
          parts.push('[tool_result] ' + t);
        }
      }
    }
    return parts.join('\n');
  }
  return '';
}

// ---- OpenClaw user 消息元数据噪音清洗 ----
export function stripOcMetadata(text) {
  if (!text) return text;
  let t = text;
  t = t.replace(/Conversation info \(untrusted metadata\):\s*```json[\s\S]*?```/g, '');
  t = t.replace(/Sender \(untrusted metadata\):\s*```json[\s\S]*?```/g, '');
  t = t.replace(/\[message_id:[^\]]*\]/g, '');
  t = t.replace(/^ou_[a-z0-9]+:\s*/gim, '');
  return t.trim();
}

// ---- Codex 注入式系统内容（非真实用户对话）----
export function isCodexInjected(text) {
  if (!text) return true;
  const t = text.trimStart();
  const startMarkers = ['<environment_context>', '<permissions instructions>', '<user_instructions>', '<workspace_context>'];
  if (startMarkers.some((m) => t.startsWith(m))) return true;
  if (t.includes('context-compaction summarization engine')) return true;
  if (t.startsWith('You summarize a SEGMENT of')) return true;
  return false;
}

// ---- 自指排除：本 skill 自己的蒸馏产物不能被再蒸馏 ----
export const STRONG_SELF_MARKERS = ['ai-weekly-review', 'ai-dialogue-distill', 'collect-ai-dialogues'];
export const SOFT_SELF_MARKERS = ['AI对话沉淀'];
export function hasStrongSelf(text) { return !!text && STRONG_SELF_MARKERS.some((m) => text.includes(m)); }
export function hasSoftSelf(text) { return !!text && SOFT_SELF_MARKERS.some((m) => text.includes(m)); }

// ---- 统一记录结构（设计 §4）+ 工具用扩展字段 ----
export function makeRecord({ source, agent_id, session_id, role, content, ts, local, date, fp, line, uuid }) {
  return {
    record_id: uuid || sha(fp + role + content),
    content_hash: sha((role || '') + content),
    source,
    agent_id: agent_id || 'unknown',
    session_id: session_id || null,
    role,
    content,
    content_type: 'text',
    timestamp_utc: ts || null,
    timestamp_local: local || null,
    local_date: date || null,
    source_path: fp,
    line_no: line,
  };
}

// ---- 递归找 jsonl（按 mtime 预筛）----
export function findJsonl(root, { recursive = false, maxAgeDays = Infinity } = {}) {
  const out = [];
  if (!fs.existsSync(root)) return out;
  const walk = (dir) => {
    let ents; try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) { if (recursive) walk(p); }
      else if (e.isFile() && e.name.endsWith('.jsonl')) {
        try { const st = fs.statSync(p); if ((Date.now() - st.mtimeMs) / 86400000 <= maxAgeDays) out.push(p); } catch { /* skip */ }
      }
    }
  };
  walk(root);
  return out;
}

// ---- 通用逐行 jsonl 扫描：自指排除 + 窗口过滤 + 统一记录 ----
// mapFn(o, state) -> { role, content, session_id, ts, uuid, agent_id } | null
export function scanJsonl(fp, { windowSet, source, agentHint = null }, mapFn, out) {
  let lines; try { lines = fs.readFileSync(fp, 'utf8').split('\n'); } catch { return; }
  const recs = [];
  let strongHits = 0, dlg = 0;
  const state = { sessionId: null, agentId: agentHint };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    let o; try { o = JSON.parse(line); } catch { continue; }
    const mapped = mapFn(o, state);
    if (!mapped) continue;
    const { role, content, session_id, ts, uuid, agent_id } = mapped;
    if (role !== 'user' && role !== 'assistant') continue;
    if (!content || !content.trim()) continue;
    dlg++;
    if (hasStrongSelf(content)) strongHits++;
    if (hasSoftSelf(content)) continue;
    const { date, local } = toLocal(ts);
    if (!windowSet.has(date)) continue;
    recs.push(makeRecord({
      source, agent_id: agent_id || state.agentId,
      session_id: session_id || state.sessionId || path.basename(fp, '.jsonl'),
      role, content, ts, local, date, fp, line: i + 1, uuid,
    }));
  }
  // 整文件自指排除：文件路径含强标记，或强标记占对话消息比 ≥ 60%
  if (hasStrongSelf(fp) || (strongHits > 0 && dlg > 0 && strongHits / dlg >= 0.6)) { out.self_skipped++; return; }
  out.records.push(...recs);
}
