package com.aiguibin.platform.core.user.service.impl;

import com.aiguibin.platform.core.user.entity.SysUserOrg;
import com.aiguibin.platform.core.user.mapper.SysUserOrgMapper;
import com.aiguibin.platform.core.user.service.SysUserOrgService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class SysUserOrgServiceImpl extends ServiceImpl<SysUserOrgMapper, SysUserOrg> implements SysUserOrgService {
    
    @Autowired
    private SysUserOrgMapper userOrgMapper;
    
    @Override
    public List<SysUserOrg> getOrgListByUserId(Long userId) {
        return userOrgMapper.selectByUserId(userId);
    }
    
    @Override
    public boolean checkUserOrg(Long userId, String orgCode) {
        return userOrgMapper.checkUserOrg(userId, orgCode) > 0;
    }
}
