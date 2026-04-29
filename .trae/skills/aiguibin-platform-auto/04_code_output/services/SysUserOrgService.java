package com.aiguibin.platform.core.user.service;

import com.aiguibin.platform.core.user.entity.SysUserOrg;
import com.baomidou.mybatisplus.extension.service.IService;
import java.util.List;

public interface SysUserOrgService extends IService<SysUserOrg> {
    
    List<SysUserOrg> getOrgListByUserId(Long userId);
    
    boolean checkUserOrg(Long userId, String orgCode);
}
