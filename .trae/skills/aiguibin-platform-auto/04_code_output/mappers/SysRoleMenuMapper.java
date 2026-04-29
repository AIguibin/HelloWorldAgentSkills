package com.aiguibin.platform.core.role.mapper;

import com.aiguibin.platform.core.role.entity.SysRoleMenu;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface SysRoleMenuMapper extends BaseMapper<SysRoleMenu> {
    
    int deleteByRoleId(@Param("roleId") Long roleId);
    
    int batchInsert(@Param("list") List<SysRoleMenu> list);
}
