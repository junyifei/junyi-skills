#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const dir = path.resolve(process.argv[2] || process.cwd());
const errors = [];

if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
  console.error(JSON.stringify({ valid: false, errors: [`目录不存在：${dir}`] }, null, 2));
  process.exit(1);
}

const names = fs.readdirSync(dir);
const specs = [
  { label: '本周记录', pattern: /^本周记录_\d{4}-W\d{2}\.md$/ },
  { label: '本周内容素材', pattern: /^本周内容素材_\d{4}-W\d{2}\.md$/ },
];

function topLevelBlocks(lines) {
  const blocks = [];
  let section = '';
  for (let i = 0; i < lines.length; i++) {
    if (/^##\s+/.test(lines[i])) section = lines[i];
    if (section.includes('来源索引')) continue;
    if (!/^(?:\d+\.\s|[-*]\s|>\s)/.test(lines[i])) continue;
    let end = i + 1;
    while (end < lines.length && !/^##\s+/.test(lines[end]) && !/^(?:\d+\.\s|[-*]\s|>\s)/.test(lines[end])) end++;
    blocks.push({ line: i + 1, text: lines.slice(i, end).join('\n') });
  }
  return blocks;
}

for (const spec of specs) {
  const found = names.filter((name) => spec.pattern.test(name));
  if (found.length !== 1) {
    errors.push(`${spec.label}文件应恰好有 1 个，实际 ${found.length} 个`);
    continue;
  }
  const fp = path.join(dir, found[0]);
  const text = fs.readFileSync(fp, 'utf8');
  if (!text.trim()) errors.push(`${found[0]} 是空文件`);
  if (text.includes('——')) errors.push(`${found[0]} 含禁用破折号“——”`);
  if (text.includes('━')) errors.push(`${found[0]} 含禁用横线“━”`);
  if (text.includes('\uFFFD')) errors.push(`${found[0]} 含乱码 U+FFFD`);

  const isEmptyWeek = text.includes('未发现有效 AI 对话记录');
  if (!isEmptyWeek) {
    for (const block of topLevelBlocks(text.split('\n'))) {
      if (!/出处[:：]/.test(block.text)) {
        errors.push(`${found[0]} 第 ${block.line} 行开始的条目缺少出处`);
      }
    }
  }
}

const result = { valid: errors.length === 0, directory: dir, errors };
console.log(JSON.stringify(result, null, 2));
process.exit(errors.length ? 1 : 0);
