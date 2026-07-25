// claude-code.mjs — ✅ 路径+字段已知（参考 collect-ai-dialogues.mjs）
// 存储：~/.claude/projects/<proj>/*.jsonl，逐行 JSON，type∈{user,assistant}，
// 文本在 message.content（string 或 block list）。排除 claude-mem-observer 目录。
import fs from 'node:fs';
import path from 'node:path';
import { extractText, findJsonl, scanJsonl } from '../lib.mjs';

const mapLine = (o, state) => {
  if (o.sessionId) state.sessionId = o.sessionId;
  if (o.type !== 'user' && o.type !== 'assistant') return null;
  const m = o.message || {};
  return {
    role: m.role || o.type,
    content: extractText(m.content),
    session_id: o.sessionId,
    ts: o.timestamp,
    uuid: o.uuid,
    agent_id: 'claude-code',
  };
};

export default {
  source: 'claude_code',
  label: 'Claude Code',
  status: 'supported',
  detect({ home }) {
    const root = path.join(home, '.claude/projects');
    return { available: fs.existsSync(root), paths: [root], note: '' };
  },
  collect({ home, windowSet, prefilterDays }) {
    const root = path.join(home, '.claude/projects');
    const out = { source: this.source, label: this.label, status: this.status, available: fs.existsSync(root), paths: [root], records: [], files: 0, self_skipped: 0, note: '' };
    if (!out.available) { out.note = '未发现 ~/.claude/projects'; return out; }
    let projDirs;
    try {
      projDirs = fs.readdirSync(root).map((d) => path.join(root, d))
        .filter((p) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } });
    } catch { out.note = '读取 projects 目录失败'; return out; }
    for (const pd of projDirs) {
      if (pd.includes('claude-mem-observer')) continue; // 后台记忆观察 session，工具独白非真实对话
      const files = findJsonl(pd, { recursive: false, maxAgeDays: prefilterDays });
      out.files += files.length;
      for (const fp of files) scanJsonl(fp, { windowSet, source: this.source }, mapLine, out);
    }
    return out;
  },
};
