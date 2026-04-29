package com.aiguibin.platform.core.org.service.impl;

import com.aiguibin.platform.core.org.entity.SysOrg;
import com.aiguibin.platform.core.org.mapper.SysOrgMapper;
import com.aiguibin.platform.core.org.service.SysOrgService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SysOrgServiceImpl extends ServiceImpl<SysOrgMapper, SysOrg> implements SysOrgService {
    
    @Autowired
    private SysOrgMapper orgMapper;
    
    @Override
    public SysOrg getByCode(String orgCode) {
        return orgMapper.selectByOrgCode(orgCode);
    }
}
