package com.aiguibin.platform.core.org.service;

import com.aiguibin.platform.core.org.entity.SysOrg;
import com.baomidou.mybatisplus.extension.service.IService;

public interface SysOrgService extends IService<SysOrg> {
    
    SysOrg getByCode(String orgCode);
}
