// workbuddy.mjs — ⚠️ unsupported（未经真机验证）
// 2026-06-25 Claude Code 落地时现场探测：本机【完全未发现】WorkBuddy 任何痕迹
// （无 ~/.workbuddy、无 App Support、find 全盘无命中）。无样本可推断字段。
// 设计铁律：探测不到 → 标 unsupported，不凭空写死路径、不伪造数据。
//
// 将来要支持 WorkBuddy：步骤同 hermes.mjs（先找真实存储 → 真样本推断字段 →
// 写 mapLine → 真机验证后才可标「已验证」）。在此之前用户走 custom 适配器。
import fs from 'node:fs';
import path from 'node:path';

function candidatePaths(home) {
  return [
    path.join(home, '.workbuddy'),
    path.join(home, 'workbuddy'),
    path.join(home, '.work-buddy'),
    path.join(home, 'Library/Application Support/WorkBuddy'),
    path.join(home, 'Library/Application Support/workbuddy'),
    path.join(home, '.config/workbuddy'),
  ];
}

export default {
  source: 'workbuddy',
  label: 'WorkBuddy',
  status: 'unsupported',
  verified: false,
  detect({ home }) {
    const cands = candidatePaths(home);
    const found = cands.filter((p) => fs.existsSync(p));
    return {
      available: false,
      paths: cands,
      found,
      note: found.length
        ? `发现疑似路径 ${found.join(', ')}，但未验证格式，暂不解析（避免臆测）。`
        : '本机未探测到 WorkBuddy 任何存储。',
    };
  },
  collect({ home }) {
    const d = this.detect({ home });
    return {
      source: this.source, label: this.label, status: 'unsupported', available: false,
      paths: d.paths, records: [], files: 0, self_skipped: 0,
      note: '⚠️ 未支持/未验证：' + d.note + ' 若你用 WorkBuddy，请走 custom 适配器（--custom-path 指定导出文件），或在 workbuddy.mjs 里按真实格式补全。',
    };
  },
};
