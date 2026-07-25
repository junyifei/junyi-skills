// codex.mjs — ✅ 本机现场探测确认（2026-06-25，Claude Code 落地时实测）
// 存储：~/.codex/sessions/YYYY/MM/DD/rollout-<ISO>-<uuid>.jsonl
// 逐行 JSON：{timestamp, type, payload}
//   type==="session_meta" → payload.id 为 session id
//   type==="response_item" 且 payload.type==="message" → payload.role∈{user,assistant,developer}
//   内容在 payload.content[]，块 type∈{input_text,output_text}（取 .text）
// 过滤：developer 角色（系统）丢弃；user 角色里 <environment_context>/<permissions instructions>/
//       compaction summarization 等注入式系统内容丢弃（见 lib.isCodexInjected）。
import fs from 'node:fs';
import path from 'node:path';
import { extractText, isCodexInjected, findJsonl, scanJsonl } from '../lib.mjs';

const mapLine = (o, state) => {
  if (o.type === 'session_meta') {
    const p = o.payload || {};
    if (p.id) state.sessionId = p.id;
    return null;
  }
  if (o.type !== 'response_item') return null;
  const p = o.payload || {};
  if (p.type !== 'message') return null;
  if (p.role !== 'user' && p.role !== 'assistant') return null; // 丢 developer/系统
  const content = extractText(p.content);
  if (p.role === 'user' && isCodexInjected(content)) return null; // 丢注入式系统上下文
  return {
    role: p.role,
    content,
    session_id: state.sessionId, // 会话级 id（来自 session_meta.payload.id），不要用消息级 p.id
    ts: o.timestamp,
    uuid: p.id, // 消息级 id → record_id
    agent_id: 'codex',
  };
};

export default {
  source: 'codex',
  label: 'Codex CLI',
  status: 'supported',
  detect({ home }) {
    const root = path.join(home, '.codex/sessions');
    return { available: fs.existsSync(root), paths: [root], note: '' };
  },
  collect({ home, windowSet, prefilterDays }) {
    const root = path.join(home, '.codex/sessions');
    const out = { source: this.source, label: this.label, status: this.status, available: fs.existsSync(root), paths: [root], records: [], files: 0, self_skipped: 0, note: '' };
    if (!out.available) { out.note = '未发现 ~/.codex/sessions'; return out; }
    // 会话按 YYYY/MM/DD 深层分区，递归找
    const files = findJsonl(root, { recursive: true, maxAgeDays: prefilterDays });
    out.files += files.length;
    for (const fp of files) scanJsonl(fp, { windowSet, source: this.source }, mapLine, out);
    return out;
  },
};
