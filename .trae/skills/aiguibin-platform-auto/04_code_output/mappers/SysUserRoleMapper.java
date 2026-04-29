package com.aiguibin.platform.core.user.mapper;

import com.aiguibin.platform.core.user.entity.SysUserRole;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface SysUserRoleMapper extends BaseMapper<SysUserRole> {
    
    int deleteByUserId(@Param("userId") Long userId);
    
    int batchInsert(@Param("list") List<SysUserRole> list);
}
