package com.aiguibin.platform.core.user.mapper;

import com.aiguibin.platform.core.user.entity.SysUserOrg;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface SysUserOrgMapper extends BaseMapper<SysUserOrg> {
    
    List<SysUserOrg> selectByUserId(@Param("userId") Long userId);
    
    int checkUserOrg(@Param("userId") Long userId, 
                     @Param("orgCode") String orgCode);
}
