const XLSX = require('xlsx');

function verifyExcel(filePath) {
    console.log('========================================');
    console.log('Excel文件验证报告');
    console.log('========================================');
    console.log(`文件路径: ${filePath}`);
    
    try {
        const workbook = XLSX.readFile(filePath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet);
        
        console.log(`工作表名称: ${sheetName}`);
        console.log(`总接口数量: ${data.length}`);
        console.log(`列名: ${Object.keys(data[0]).join(', ')}`);
        
        let normalizedCount = 0;
        let moduleStats = {};
        let methodStats = {};
        
        data.forEach(row => {
            if (row['是否规范化URL'] && row['是否规范化URL'].includes('是')) {
                normalizedCount++;
            }
            const module = row['所属模块'] || '其他模块';
            moduleStats[module] = (moduleStats[module] || 0) + 1;
            
            const method = row['请求方式'] || 'POST';
            methodStats[method] = (methodStats[method] || 0) + 1;
        });
        
        console.log(`\n规范化URL数量（添加/前缀）: ${normalizedCount}`);
        
        console.log('\n请求方式分布:');
        Object.entries(methodStats)
            .sort((a, b) => b[1] - a[1])
            .forEach(([method, count]) => {
                console.log(`  ${method}: ${count}个接口`);
            });
        
        console.log('\n模块分布统计:');
        Object.entries(moduleStats)
            .sort((a, b) => b[1] - a[1])
            .forEach(([module, count]) => {
                console.log(`  ${module}: ${count}个接口`);
            });
        
        console.log('\n前10条记录:');
        data.slice(0, 10).forEach((row, index) => {
            console.log(`${index + 1}. ${row['接口地址']} - ${row['接口描述']} [${row['请求方式']}]`);
        });
        
        console.log('\n最后10条记录:');
        data.slice(-10).forEach((row, index) => {
            console.log(`${data.length - 9 + index}. ${row['接口地址']} - ${row['接口描述']} [${row['请求方式']}]`);
        });
        
        console.log('\n========================================');
        console.log('验证完成');
        console.log('========================================');
        
        return {
            success: true,
            totalCount: data.length,
            normalizedCount,
            moduleStats,
            methodStats
        };
        
    } catch (err) {
        console.error('读取Excel文件失败:', err.message);
        return {
            success: false,
            error: err.message
        };
    }
}

function main() {
    const args = process.argv.slice(2);
    const filePath = args[0] || '项目接口清单_完整版.xlsx';
    verifyExcel(filePath);
}

module.exports = { verifyExcel };

if (require.main === module) {
    main();
}
