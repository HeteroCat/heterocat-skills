#!/usr/bin/env node
/**
 * 安装后脚本 - 检查 Python 依赖
 */

const { spawn } = require('child_process');
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m'
};

console.log(`${colors.cyan}\n🚀 基金分析技能安装完成!${colors.reset}\n`);

// 检查 Python 依赖
console.log(`${colors.yellow}检查 Python 依赖...${colors.reset}`);

const checkDep = (dep) => {
  return new Promise((resolve) => {
    const python = spawn('python3', ['-c', `import ${dep}`]);
    python.on('close', (code) => resolve(code === 0));
  });
};

(async () => {
  const deps = ['akshare', 'pandas', 'numpy'];
  const missing = [];
  
  for (const dep of deps) {
    const hasDep = await checkDep(dep);
    if (hasDep) {
      console.log(`  ${colors.green}✓${colors.reset} ${dep}`);
    } else {
      console.log(`  ${colors.red}✗${colors.reset} ${dep}`);
      missing.push(dep);
    }
  }
  
  if (missing.length > 0) {
    console.log(`\n${colors.yellow}缺少以下 Python 依赖，请运行:${colors.reset}`);
    console.log(`${colors.cyan}  pip install ${missing.join(' ')}${colors.reset}\n`);
  } else {
    console.log(`\n${colors.green}✓ 所有依赖已安装${colors.reset}`);
    console.log(`${colors.cyan}\n现在可以运行: npx mutual-fund-skills${colors.reset}\n`);
  }
})();
