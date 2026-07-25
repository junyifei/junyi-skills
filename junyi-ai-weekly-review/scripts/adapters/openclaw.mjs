// openclaw.mjs — ✅ 路径+字段已知（参考 collect-ai-dialogues.mjs）
// 存储：~/.openclaw/agents/<agentId>/sessions/*.jsonl，逐行 JSON，type==="message"，
// role 在 message.role，内容在 message.content。user 消息清洗元数据噪音。
import fs from 'node:fs';
import path from 'node:path';
import { extractText, stripOcMetadata, findJsonl, scanJsonl } from '../lib.mjs';

const mapLine = (o, state) => {
  if (o.id && !state.sessionId) state.sessionId = o.id;
  if (o.type !== 'message') return null;
  const m = o.message || {};
  let content = extractText(m.content);
  if (m.role === 'user') content = stripOcMetadata(content);
  return {
    role: m.role,
    content,
    session_id: state.sessionId, // 会话级 id（首条消息 id 作代理），不要用每条消息的 o.id
    ts: o.timestamp || m.timestamp,
    uuid: o.id, // 消息级 id → record_id
    agent_id: state.agentId,
  };
};

export default {
  source: 'openclaw',
  label: 'OpenClaw',
  status: 'supported',
  detect({ home }) {
    const root = path.join(home, '.openclaw/agents');
    return { available: fs.existsSync(root), paths: [root], note: '' };
  },
  collect({ home, windowSet, prefilterDays }) {
    const root = path.join(home, '.openclaw/agents');
    const out = { source: this.source, label: this.label, status: this.status, available: fs.existsSync(root), paths: [root], records: [], files: 0, self_skipped: 0, note: '' };
    if (!out.available) { out.note = '未发现 ~/.openclaw/agents'; return out; }
    let agentDirs;
    try {
      agentDirs = fs.readdirSync(root).map((d) => path.join(root, d))
        .filter((p) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } });
    } catch { out.note = '读取 agents 目录失败'; return out; }
    for (const ad of agentDirs) {
      const agentId = path.basename(ad);
      const sessDir = path.join(ad, 'sessions');
      const files = findJsonl(sessDir, { recursive: false, maxAgeDays: prefilterDays });
      out.files += files.length;
      for (const fp of files) scanJsonl(fp, { windowSet, source: this.source, agentHint: agentId }, mapLine, out);
    }
    return out;
  },
};
