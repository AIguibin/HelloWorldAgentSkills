# 模块映射参考

本文档提供了URL路径到模块名称的完整映射规则。

## 映射规则

| URL模式 | 模块名称 |
|---------|----------|
| /homeCalenderRemind | 日历模块 |
| /homeCardManage | 卡片管理 |
| /qa/ | 智能客服 |
| /sysLink | 通用功能 |
| /userTheme | 主题配置 |
| /homePageDef | 首页配置 |
| /searchHistory | 搜索历史 |
| /helpGuideFlagAction | 帮助中心 |
| /helpDefExceptionAction | 帮助中心 |
| /helpFeedbackAction | 帮助中心 |
| /helpTipsAction | 帮助中心 |
| /workflow | 工作流 |
| /ucmp-manage-base | 基础管理 |
| /ucmp-business-corporate | 对公业务 |
| /ucmp-business-retail | 零售业务 |
| /ucmp-collateral-manage | 押品管理 |
| /ucmp-cust-manage | 客户管理 |
| /tansun-tcp-system-boot | 系统启动 |
| /tansun-tcp-common | 公共服务 |
| /tansun-tcp-workflow | 工作流服务 |
| /tansun-tcp-collateral | 押品服务 |
| /tansun-tcp-corporate-boot | 对公启动 |
| /tansun-tcp-creditlimitaply | 授信申请 |
| /tansun-tcp-sys | 系统服务 |
| /tansun-tcp-docmanage | 文档管理 |
| /tansun-tcp-ldrp | 贷款还款 |
| /ncms-manage-creditcontrol | 授信管控 |
| /ncms-process-postloanmgt | 贷后管理 |
| /ipcPdElmt | 产品要素 |
| /ipcPdElmtGroup | 要素组 |
| /ipcPdElmtExmp | 要素示例 |
| /ipcFcnScnInf | 功能场景 |
| /ipc/rule | 规则引擎 |
| /ipc/workflow | 工作流引擎 |
| /conElcDocTplTbl | 电子文档模板 |
| /fileServer | 文件服务 |
| /ucmp-doc-manage | 文档管理 |
| /elcDoc | 电子文档 |
| /param | 参数配置 |
| /login | 登录模块 |
| /getSession | 会话管理 |
| /createToken | 令牌管理 |

## 自定义映射

如果需要添加自定义模块映射，可以在 `scripts/scan_apis.js` 文件中的 `modulePatterns` 数组中添加：

```javascript
const modulePatterns = [
    // 添加自定义映射
    { pattern: '/your-api-path', module: '你的模块名' },
    // ... 其他映射
];
```
