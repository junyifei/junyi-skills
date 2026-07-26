#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { redactForModel } from '../junyi-ai-weekly-review/scripts/lib.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const collect = path.join(root, 'junyi-ai-weekly-review/scripts/collect.mjs');
const validate = path.join(root, 'junyi-ai-weekly-review/scripts/validate-output.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'junyi-ai-weekly-review-test-'));

function run(script, args, expected = 0) {
  const result = spawnSync(process.execPath, [script, ...args], { encoding: 'utf8' });
  assert.equal(result.status, expected, `${script} exited ${result.status}\n${result.stdout}\n${result.stderr}`);
  return result;
}

function writeJsonl(fp, records) {
  fs.writeFileSync(fp, records.map((item) => JSON.stringify(item)).join('\n') + '\n');
}

try {
  const redacted = redactForModel('账号：demo-user api_key=sk-abcdefghijklmnop 预算￥12,500 Authorization: Bearer abcdefghijklmnop');
  assert.equal(redacted.text.includes('demo-user'), false);
  assert.equal(redacted.text.includes('sk-abcdefghijklmnop'), false);
  assert.equal(redacted.text.includes('12,500'), false);
  assert.equal(redacted.text.includes('abcdefghijklmnop'), false);
  assert.ok(redacted.count >= 4);

  const v1 = path.join(tmp, 'rerun-v1.jsonl');
  const v2 = path.join(tmp, 'rerun-v2.jsonl');
  const base = [
    { id: 'r1', role: 'user', timestamp: '2026-07-25T09:00:00+09:00', session_id: 'one', content: '第一组会话。' },
    { id: 'r2', role: 'assistant', timestamp: '2026-07-25T09:01:00+09:00', session_id: 'one', content: '第一组回复。' },
  ];
  writeJsonl(v1, [
    ...base,
    { id: 'r3', role: 'user', timestamp: '2026-07-25T10:00:00+09:00', session_id: 'two', content: '第二组会话。' },
    { id: 'r4', role: 'assistant', timestamp: '2026-07-25T10:01:00+09:00', session_id: 'two', content: '第二组回复。' },
  ]);
  writeJsonl(v2, base);
  const rerunOut = path.join(tmp, 'rerun-output');
  const common = ['--since', '2026-07-19', '--until', '2026-07-25', '--out', rerunOut, '--adapters', 'custom'];
  run(collect, [...common, '--custom-path', v1]);
  const dayDir = path.join(rerunOut, '2026-W30/days/2026-07-25');
  fs.writeFileSync(path.join(dayDir, 'user-note.md'), '用户文件不得删除。\n');
  run(collect, [...common, '--custom-path', v2]);
  assert.deepEqual(fs.readdirSync(dayDir).filter((name) => /^chunk_\d+\.md$/.test(name)), ['chunk_001.md']);
  assert.equal(fs.existsSync(path.join(dayDir, 'user-note.md')), true);

  const noTime = path.join(tmp, 'no-time.jsonl');
  writeJsonl(noTime, [{ id: 'nt1', role: 'user', content: '没有时间戳。' }]);
  const noTimeOut = path.join(tmp, 'no-time-output');
  run(collect, ['--since', '2026-07-19', '--until', '2026-07-25', '--out', noTimeOut, '--adapters', 'custom', '--custom-path', noTime]);
  const report = JSON.parse(fs.readFileSync(path.join(noTimeOut, '2026-W30/adapters-report.json'), 'utf8'))[0];
  assert.equal(report.missing_timestamp, 1);
  assert.match(report.note, /缺时间戳 1 条/);
  assert.doesNotMatch(report.note, /unparsed=0/);

  const mixed = path.join(tmp, 'mixed-time.jsonl');
  writeJsonl(mixed, [
    { id: 'skip1', role: 'user', content: '第一行没有时间戳。' },
    { id: 'keep2', role: 'user', timestamp: '2026-07-25T11:00:00+09:00', content: '第二行应保留真实行号。' },
  ]);
  const mixedOut = path.join(tmp, 'mixed-output');
  run(collect, ['--since', '2026-07-19', '--until', '2026-07-25', '--out', mixedOut, '--adapters', 'custom', '--custom-path', mixed]);
  const kept = JSON.parse(fs.readFileSync(path.join(mixedOut, '2026-W30/records.cleaned.jsonl'), 'utf8').trim());
  assert.equal(kept.line_no, 2);

  const secrets = path.join(tmp, 'secrets.jsonl');
  writeJsonl(secrets, [{
    id: 'sec1', role: 'user', timestamp: '2026-07-25T12:00:00+09:00', session_id: 'secret',
    content: '账号：demo-user，api_key=sk-abcdefghijklmnop，预算￥12,500。',
  }]);
  const secretsOut = path.join(tmp, 'secrets-output');
  run(collect, ['--since', '2026-07-19', '--until', '2026-07-25', '--out', secretsOut, '--adapters', 'custom', '--custom-path', secrets]);
  const weekDir = path.join(secretsOut, '2026-W30');
  const chunk = fs.readFileSync(path.join(weekDir, 'days/2026-07-25/chunk_001.md'), 'utf8');
  const raw = fs.readFileSync(path.join(weekDir, 'records.cleaned.jsonl'), 'utf8');
  assert.equal(chunk.includes('demo-user'), false);
  assert.equal(chunk.includes('sk-abcdefghijklmnop'), false);
  assert.equal(chunk.includes('12,500'), false);
  assert.equal(raw.includes('sk-abcdefghijklmnop'), true);

  fs.writeFileSync(path.join(weekDir, '本周记录_2026-W30.md'), '# 本周记录\n\n## 三、本周方法\n- 一个方法。出处：rec sec1\n');
  fs.writeFileSync(path.join(weekDir, '本周内容素材_2026-W30.md'), '# 本周内容素材\n\n## 一、可写故事\n- 一个故事。出处：rec sec1\n');
  run(validate, [weekDir]);
  fs.appendFileSync(path.join(weekDir, '本周内容素材_2026-W30.md'), '\n含有——禁用符号。\n');
  run(validate, [weekDir], 1);

  console.log('ai-weekly-review regression valid: rerun cleanup, timestamp diagnostics, redaction, output validation');
} finally {
  fs.rmSync(tmp, { recursive: true, force: true });
}
