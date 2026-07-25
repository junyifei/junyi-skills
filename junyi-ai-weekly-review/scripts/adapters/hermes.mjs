// hermes.mjs — ⚠️ unsupported（未经真机验证）
// 2026-06-25 Claude Code 落地时现场探测：本机【未发现】任何 Hermes 本地会话存储。
// 探测过的候选路径见 detect()。Hermes 仅在对比文档里被提及，无样本可推断字段。
// 设计铁律：探测不到 → 标 unsupported，不凭空写死路径、不伪造数据。
//
// 将来要支持 Hermes：
//   1. 找到 Hermes 真实会话存储（jsonl/json/sqlite？），用真样本 `head` 推断字段；
//   2. 仿照 codex.mjs 写 mapLine（吐 {role,content,session_id,ts,uuid}）；
//   3. 把 status 改成 'supported'，并在真机用真实数据跑通后才可标「已验证」。
//   4. 在此之前，用户可走 custom 适配器手动指定导出文件路径。
import fs from 'node:fs';
import path from 'node:path';

function candidatePaths(home) {
  return [
    path.join(home, '.hermes'),
    path.join(home, 'hermes'),
    path.join(home, '.hermes/sessions'),
    path.join(home, 'Library/Application Support/Hermes'),
    path.join(home, 'Library/Application Support/hermes'),
    path.join(home, '.config/hermes'),
  ];
}

export default {
  source: 'hermes',
  label: 'Hermes',
  status: 'unsupported',
  verified: false,
  detect({ home }) {
    const cands = candidatePaths(home);
    const found = cands.filter((p) => fs.existsSync(p));
    return {
      available: false, // 即使路径存在也不当作已支持：未验证格式，绝不臆测解析
      paths: cands,
      found,
      note: found.length
        ? `发现疑似路径 ${found.join(', ')}，但未验证格式，暂不解析（避免臆测）。`
        : '本机未探测到 Hermes 会话存储。',
    };
  },
  collect({ home }) {
    const d = this.detect({ home });
    return {
      source: this.source, label: this.label, status: 'unsupported', available: false,
      paths: d.paths, records: [], files: 0, self_skipped: 0,
      note: '⚠️ 未支持/未验证：' + d.note + ' 若你用 Hermes，请走 custom 适配器（--custom-path 指定导出文件），或在 hermes.mjs 里按真实格式补全。',
    };
  },
};
