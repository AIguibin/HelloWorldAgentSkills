const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const allUrls = new Set();
const urlDetails = new Map();

function normalizeUrl(url) {
    if (!url) return null;
    url = url.trim();
    if (url.startsWith('/') || url.startsWith('http') || url.startsWith('${')) {
        return url;
    }
    if (url.startsWith(' /')) {
        return url.substring(1);
    }
    return '/' + url;
}

function isValidApiUrl(url) {
    if (!url) return false;
    if (url.includes('${') && url.includes('}')) {
        const cleanUrl = url.replace(/\$\{[^}]+\}/g, 'VAR');
        return cleanUrl.includes('/');
    }
    return url.includes('/') && url.length > 3;
}

function extractUrlsFromFile(filePath, content) {
    const patterns = [
        /url:\s*['"`]([^'"`]+)['"`]/g,
        /url:\s*['"`]([^'"`]+)/g
    ];
    
    patterns.forEach(pattern => {
        let match;
        while ((match = pattern.exec(content)) !== null) {
            let url = match[1];
            if (url && !url.includes('xxx/xxx') && !url.includes('mock.apifox')) {
                const normalizedUrl = normalizeUrl(url);
                if (isValidApiUrl(normalizedUrl)) {
                    const cleanUrl = normalizedUrl.replace(/\$\{[^}]+\}/g, '').replace(/\/+/g, '/').replace(/\/$/, '');
                    if (cleanUrl && cleanUrl.length > 2) {
                        allUrls.add(cleanUrl);
                        if (!urlDetails.has(cleanUrl)) {
                            urlDetails.set(cleanUrl, {
                                files: [],
                                originalUrls: new Set()
                            });
                        }
                        urlDetails.get(cleanUrl).files.push(filePath);
                        urlDetails.get(cleanUrl).originalUrls.add(url);
                    }
                }
            }
        }
    });
}

function scanDirectory(dir, fileExtensions = ['.js', '.vue', '.ts', '.jsx', '.tsx'], excludeDirs = ['node_modules', 'dist', 'build']) {
    console.log(`正在扫描目录: ${dir}`);
    
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
            if (!excludeDirs.includes(item)) {
                scanDirectory(fullPath, fileExtensions, excludeDirs);
            }
        } else if (stat.isFile()) {
            const ext = path.extname(fullPath).toLowerCase();
            if (fileExtensions.includes(ext)) {
                try {
                    const content = fs.readFileSync(fullPath, 'utf-8');
                    extractUrlsFromFile(fullPath, content);
                } catch (err) {
                    console.log(`无法读取文件: ${fullPath}`);
                }
            }
        }
    }
}

function getModule(url) {
    const modulePatterns = [
        { pattern: '/homeCalenderRemind', module: '日历模块' },
        { pattern: '/homeCardManage', module: '卡片管理' },
        { pattern: '/qa/', module: '智能客服' },
        { pattern: '/sysLink', module: '通用功能' },
        { pattern: '/userTheme', module: '主题配置' },
        { pattern: '/homePageDef', module: '首页配置' },
        { pattern: '/searchHistory', module: '搜索历史' },
        { pattern: '/helpGuideFlagAction', module: '帮助中心' },
        { pattern: '/helpDefExceptionAction', module: '帮助中心' },
        { pattern: '/helpFeedbackAction', module: '帮助中心' },
        { pattern: '/helpTipsAction', module: '帮助中心' },
        { pattern: '/workflow', module: '工作流' },
        { pattern: '/ucmp-manage-base', module: '基础管理' },
        { pattern: '/ucmp-business-corporate', module: '对公业务' },
        { pattern: '/ucmp-business-retail', module: '零售业务' },
        { pattern: '/ucmp-collateral-manage', module: '押品管理' },
        { pattern: '/ucmp-cust-manage', module: '客户管理' },
        { pattern: '/tansun-tcp-system-boot', module: '系统启动' },
        { pattern: '/tansun-tcp-common', module: '公共服务' },
        { pattern: '/tansun-tcp-workflow', module: '工作流服务' },
        { pattern: '/tansun-tcp-collateral', module: '押品服务' },
        { pattern: '/tansun-tcp-corporate-boot', module: '对公启动' },
        { pattern: '/tansun-tcp-creditlimitaply', module: '授信申请' },
        { pattern: '/tansun-tcp-sys', module: '系统服务' },
        { pattern: '/tansun-tcp-docmanage', module: '文档管理' },
        { pattern: '/tansun-tcp-ldrp', module: '贷款还款' },
        { pattern: '/ncms-manage-creditcontrol', module: '授信管控' },
        { pattern: '/ncms-process-postloanmgt', module: '贷后管理' },
        { pattern: '/ipcPdElmt', module: '产品要素' },
        { pattern: '/ipcPdElmtGroup', module: '要素组' },
        { pattern: '/ipcPdElmtExmp', module: '要素示例' },
        { pattern: '/ipcFcnScnInf', module: '功能场景' },
        { pattern: '/ipc/rule', module: '规则引擎' },
        { pattern: '/ipc/workflow', module: '工作流引擎' },
        { pattern: '/conElcDocTplTbl', module: '电子文档模板' },
        { pattern: '/fileServer', module: '文件服务' },
        { pattern: '/ucmp-doc-manage', module: '文档管理' },
        { pattern: '/elcDoc', module: '电子文档' },
        { pattern: '/param', module: '参数配置' },
        { pattern: '/login', module: '登录模块' },
        { pattern: '/getSession', module: '会话管理' },
        { pattern: '/createToken', module: '令牌管理' }
    ];
    
    for (const { pattern, module } of modulePatterns) {
        if (url.includes(pattern)) return module;
    }
    return '其他模块';
}

function getDescription(url) {
    const actionMap = {
        'get': '获取',
        'query': '查询',
        'save': '保存',
        'saveOrUpdate': '保存或更新',
        'delete': '删除',
        'update': '更新',
        'create': '创建',
        'list': '列表',
        'page': '分页查询',
        'tree': '树形查询',
        'submit': '提交',
        'cancel': '取消',
        'handle': '处理',
        'init': '初始化',
        'check': '检查',
        'copy': '复制'
    };
    
    const parts = url.split('/');
    const lastPart = parts[parts.length - 1];
    
    for (const [action, desc] of Object.entries(actionMap)) {
        if (lastPart.toLowerCase().includes(action)) {
            return desc + lastPart.replace(new RegExp(action, 'gi'), '');
        }
    }
    
    return '待补充描述';
}

function getMethod(url) {
    const getKeywords = ['get', 'query', 'list', 'page', 'tree', 'find', 'select'];
    const lastPart = url.split('/').pop().toLowerCase();
    
    for (const keyword of getKeywords) {
        if (lastPart.includes(keyword)) {
            return 'GET';
        }
    }
    return 'POST';
}

function createExcel(outputPath) {
    console.log('开始创建Excel文档...');
    
    const sortedUrls = Array.from(allUrls).sort();
    
    console.log(`共发现 ${sortedUrls.length} 个唯一接口URL`);
    
    const wb = XLSX.utils.book_new();
    
    const headers = ['序号', '接口地址', '接口描述', '请求方式', '接口参数', '所属模块', '来源文件数', '是否规范化URL'];
    const data = [headers];
    
    let normalizedCount = 0;
    
    sortedUrls.forEach((url, index) => {
        const details = urlDetails.get(url);
        const isNormalized = details && Array.from(details.originalUrls).some(u => !u.startsWith('/'));
        if (isNormalized) normalizedCount++;
        
        data.push([
            index + 1,
            url,
            getDescription(url),
            getMethod(url),
            '',
            getModule(url),
            details ? details.files.length : 1,
            isNormalized ? '是(已添加/前缀)' : '否'
        ]);
    });
    
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    ws['!cols'] = [
        { wch: 8 },
        { wch: 80 },
        { wch: 40 },
        { wch: 12 },
        { wch: 30 },
        { wch: 20 },
        { wch: 12 },
        { wch: 20 }
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, '接口清单');
    
    try {
        XLSX.writeFile(wb, outputPath);
        console.log('Excel文件已成功生成: ' + outputPath);
        console.log(`共输出 ${sortedUrls.length} 个接口 (已去重)`);
        console.log(`其中规范化URL（添加/前缀）的接口数量: ${normalizedCount}`);
        return true;
    } catch (err) {
        console.error('写入Excel文件失败:', err.message);
        const backupPath = outputPath.replace('.xlsx', `_${Date.now()}.xlsx`);
        XLSX.writeFile(wb, backupPath);
        console.log('Excel文件已保存到备用路径: ' + backupPath);
        return false;
    }
}

function main(projectPath, outputPath, options = {}) {
    const {
        fileExtensions = ['.js', '.vue', '.ts', '.jsx', '.tsx'],
        excludeDirs = ['node_modules', 'dist', 'build']
    } = options;
    
    console.log('========================================');
    console.log('API接口扫描工具');
    console.log('========================================');
    console.log(`项目路径: ${projectPath}`);
    console.log(`输出路径: ${outputPath}`);
    console.log('========================================');
    
    console.log('开始扫描项目文件...');
    scanDirectory(projectPath, fileExtensions, excludeDirs);
    console.log('文件扫描完成');
    
    const success = createExcel(outputPath);
    
    console.log('========================================');
    console.log('处理完成');
    console.log('========================================');
    
    return success;
}

module.exports = { main, scanDirectory, createExcel, normalizeUrl, getModule, getDescription, getMethod };
