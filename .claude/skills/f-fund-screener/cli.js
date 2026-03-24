#!/usr/bin/env node
/**
 * 基金分析技能 CLI
 * 通过 npx mutual-fund-skills 直接运行
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function printBanner() {
  console.log(`${colors.cyan}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           基金分析技能 (Mutual Fund Skills) v1.3.0                 ║
║                                                                  ║
║     基于 AkShare 的高夏普比率、低回撤基金筛选工具                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝${colors.reset}\n`);
}

function checkPython() {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', ['--version']);
    let version = '';
    
    python.stdout.on('data', (data) => {
      version += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve(version.trim());
      } else {
        // 尝试 python
        const python2 = spawn('python', ['--version']);
        python2.on('close', (code2) => {
          if (code2 === 0) {
            resolve('python');
          } else {
            reject(new Error('未找到 Python，请先安装 Python 3.8+'));
          }
        });
      }
    });
  });
}

async function main() {
  printBanner();
  
  try {
    // 检查 Python
    const pythonVersion = await checkPython();
    console.log(`${colors.green}✓ 检测到 ${pythonVersion}${colors.reset}\n`);
    
    // 获取脚本路径
    const scriptPath = path.join(__dirname, 'fund_screener.py');
    
    if (!fs.existsSync(scriptPath)) {
      console.error(`${colors.red}✗ 错误: 找不到 fund_screener.py${colors.reset}`);
      process.exit(1);
    }
    
    // 运行 Python 脚本
    console.log(`${colors.yellow}正在启动基金筛选器...${colors.reset}\n`);
    
    const pythonCmd = pythonVersion === 'python' ? 'python' : 'python3';
    const child = spawn(pythonCmd, [scriptPath], {
      stdio: 'inherit',
      cwd: __dirname
    });
    
    child.on('close', (code) => {
      if (code !== 0) {
        console.error(`${colors.red}\n✗ 程序异常退出 (code: ${code})${colors.reset}`);
        process.exit(code);
      }
    });
    
  } catch (error) {
    console.error(`${colors.red}✗ 错误: ${error.message}${colors.reset}`);
    console.log(`\n${colors.yellow}请先安装 Python 3.8+:${colors.reset}`);
    console.log('  macOS: brew install python');
    console.log('  Linux: sudo apt-get install python3');
    console.log('  Windows: https://python.org/downloads\n');
    process.exit(1);
  }
}

// 处理命令行参数
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`${colors.cyan}
基金分析技能 - 使用方法

命令:
  # 基金类型筛选
  npx mutual-fund-skills --bond                    纯债基金筛选（低风险）
  npx mutual-fund-skills --gushou-plus            固收+专业筛选（铁三角）
  npx mutual-fund-skills --stock                  股票类基金筛选
  npx mutual-fund-skills --stock-alpha            专业Alpha策略筛选
  
  # 自定义筛选参数
  npx mutual-fund-skills --bond --min-sharpe 1.0 --max-dd 2
  npx mutual-fund-skills --gushou-plus --min-sortino 1.5
  npx mutual-fund-skills --stock-alpha --min-calmar 0.8 --min-return 10
  
  # 数量控制
  npx mutual-fund-skills --bond --max 50          筛选50只
  npx mutual-fund-skills <基金代码>              分析单个基金
  
  # 帮助
  npx mutual-fund-skills --help                   显示帮助信息
  npx mutual-fund-skills --version                 显示版本

筛选模式说明:
  • --bond / --pure-bond: 纯债基金筛选（夏普>1.0 & 回撤<2%）
  • --gushou-plus: 固收+基金筛选（夏普>0.8 & 索提诺>1.2 & 回撤<5%）
  • --stock: 股票类基金筛选（普通模式）
  • --stock-alpha: Alpha策略筛选（卡玛>1.2 & 收益>10%）

自定义参数:
  • --min-sharpe <value>: 最小夏普比率
  • --max-dd <value>: 最大回撤百分比（正数，如5表示回撤<5%）
  • --min-return <value>: 最小年化收益率
  • --min-calmar <value>: 最小卡玛比率
  • --min-sortino <value>: 最小索提诺比率
  • --max <value>: 最大分析数量（50-500）

示例:
  # 纯债基金筛选
  npx mutual-fund-skills --bond
  
  # 纯债基金，自定义标准
  npx mutual-fund-skills --bond --min-sharpe 1.0 --max-dd 2 --min-return 2.5
  
  # 固收+基金筛选
  npx mutual-fund-skills --gushou-plus
  
  # 股票型Alpha筛选
  npx mutual-fund-skills --stock-alpha

专业指标说明:
  • 夏普比率 (Sharpe): 风险调整收益，>0.5良好，>1.0优秀
  • 索提诺比率 (Sortino): 只惩罚下行波动，>1.2良好，>2.0优秀（固收+核心）
  • 卡玛比率 (Calmar): 收益/回撤，>0.8良好，>1.2优秀（股票核心）
  • 最大回撤: 历史上最大亏损，越小越好

依赖:
  • Python 3.8+
  • akshare, pandas, numpy

安装依赖:
  pip install akshare pandas numpy
${colors.reset}`);
  process.exit(0);
}

if (args.includes('--version') || args.includes('-v')) {
  console.log('v1.3.0');
  process.exit(0);
}

// 检查是否是单个基金分析模式
if (args.length > 0 && !args[0].startsWith('--')) {
  // 单个基金分析模式
  const fundCode = args[0];
  const fundName = args[1] || null;
  
  printBanner();
  
  checkPython().then((pythonVersion) => {
    console.log(`${colors.green}✓ 检测到 ${pythonVersion}${colors.reset}\n`);
    
    const scriptPath = path.join(__dirname, 'fund_screener.py');
    
    if (!fs.existsSync(scriptPath)) {
      console.error(`${colors.red}✗ 错误: 找不到 fund_screener.py${colors.reset}`);
      process.exit(1);
    }
    
    console.log(`${colors.yellow}正在分析基金: ${fundCode}${colors.reset}\n`);
    
    const pythonCmd = pythonVersion === 'python' ? 'python' : 'python3';
    const pythonArgs = [scriptPath, fundCode];
    if (fundName) {
      pythonArgs.push(fundName);
    }
    
    const child = spawn(pythonCmd, pythonArgs, {
      stdio: 'inherit',
      cwd: __dirname
    });
    
    child.on('close', (code) => {
      if (code !== 0) {
        console.error(`${colors.red}\n✗ 程序异常退出 (code: ${code})${colors.reset}`);
        process.exit(code);
      }
    });
  }).catch((error) => {
    console.error(`${colors.red}✗ 错误: ${error.message}${colors.reset}`);
    console.log(`\n${colors.yellow}请先安装 Python 3.8+:${colors.reset}`);
    console.log('  macOS: brew install python');
    console.log('  Linux: sudo apt-get install python3');
    console.log('  Windows: https://python.org/downloads\n');
    process.exit(1);
  });
} else {
  // 批量筛选模式 - 默认全市场筛选
  printBanner();
  
  checkPython().then((pythonVersion) => {
    console.log(`${colors.green}✓ 检测到 ${pythonVersion}${colors.reset}\n`);
    
    const scriptPath = path.join(__dirname, 'fund_screener.py');
    
    // 构建参数 - 透传所有支持的参数给 Python
    const pythonArgs = [scriptPath];

    // 透传带值的参数
    const valueArgs = ['--max', '--min-sharpe', '--max-dd', '--min-return', '--min-calmar', '--min-sortino'];
    for (const argName of valueArgs) {
      if (args.includes(argName)) {
        const idx = args.indexOf(argName);
        if (idx + 1 < args.length) {
          pythonArgs.push(argName, args[idx + 1]);
        }
      }
    }

    // 透传开关参数
    const flagArgs = ['--gushou-plus', '--stock', '--stock-alpha', '--smart-pick', '--dividend', '--bond', '--pure-bond'];
    for (const flag of flagArgs) {
      if (args.includes(flag)) {
        pythonArgs.push(flag);
      }
    }

    // 显示模式提示
    if (args.includes('--bond') || args.includes('--pure-bond')) {
      console.log(`${colors.yellow}启动纯债基金筛选...${colors.reset}\n`);
    } else if (args.includes('--gushou-plus')) {
      console.log(`${colors.yellow}启动固收+基金专业筛选...${colors.reset}\n`);
    } else if (args.includes('--dividend')) {
      console.log(`${colors.yellow}启动红利/高股息基金筛选...${colors.reset}\n`);
    } else if (args.includes('--smart-pick')) {
      console.log(`${colors.yellow}启动智选主动基金筛选（哑铃结构）...${colors.reset}\n`);
    } else if (args.includes('--stock-alpha')) {
      console.log(`${colors.yellow}启动专业Alpha策略筛选...${colors.reset}\n`);
    } else if (args.includes('--stock')) {
      console.log(`${colors.yellow}启动股票类基金智能筛选...${colors.reset}\n`);
    } else {
      console.log(`${colors.yellow}启动全市场基金智能筛选...${colors.reset}\n`);
    }
    
    const pythonCmd = pythonVersion === 'python' ? 'python' : 'python3';
    const child = spawn(pythonCmd, pythonArgs, {
      stdio: 'inherit',
      cwd: __dirname
    });
    
    child.on('close', (code) => {
      if (code !== 0) {
        console.error(`${colors.red}\n✗ 程序异常退出 (code: ${code})${colors.reset}`);
        process.exit(code);
      }
    });
  }).catch((error) => {
    console.error(`${colors.red}✗ 错误: ${error.message}${colors.reset}`);
    console.log(`\n${colors.yellow}请先安装 Python 3.8+:${colors.reset}`);
    console.log('  macOS: brew install python');
    console.log('  Linux: sudo apt-get install python3');
    console.log('  Windows: https://python.org/downloads\n');
    process.exit(1);
  });
}
