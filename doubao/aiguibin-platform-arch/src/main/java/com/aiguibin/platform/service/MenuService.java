package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.dto.MenuCreateDTO;
import com.aiguibin.platform.dto.MenuQueryDTO;
import com.aiguibin.platform.dto.MenuUpdateDTO;
import com.aiguibin.platform.entity.SysMenu;
import com.aiguibin.platform.mapper.SysMenuMapper;
import com.aiguibin.platform.vo.MenuTreeVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MenuService extends ServiceImpl<SysMenuMapper, SysMenu> {

    public List<MenuTreeVO> getMenuTree(MenuQueryDTO queryDTO) {
        LambdaQueryWrapper<SysMenu> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getMenuName())) {
            wrapper.like(SysMenu::getMenuName, queryDTO.getMenuName());
        }
        if (queryDTO.getMenuType() != null) {
            wrapper.eq(SysMenu::getMenuType, queryDTO.getMenuType());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(SysMenu::getStatus, queryDTO.getStatus());
        }
        wrapper.orderByAsc(SysMenu::getSortOrder);
        
        List<SysMenu> menuList = this.list(wrapper);
        
        List<MenuTreeVO> treeVOList = menuList.stream()
                .map(this::convertToTreeVO)
                .collect(Collectors.toList());
        
        return buildTree(treeVOList);
    }

    public MenuTreeVO getMenuDetail(Long menuId) {
        SysMenu menu = this.getById(menuId);
        if (menu == null) {
            throw new BusinessException("菜单不存在");
        }
        return convertToTreeVO(menu);
    }

    @Transactional(rollbackFor = Exception.class)
    public void createMenu(MenuCreateDTO createDTO) {
        LambdaQueryWrapper<SysMenu> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysMenu::getMenuCode, createDTO.getMenuCode());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("菜单编码已存在");
        }
        
        SysMenu menu = new SysMenu();
        BeanUtil.copyProperties(createDTO, menu);
        
        if (menu.getSortOrder() == null) {
            menu.setSortOrder(0);
        }
        menu.setStatus(1);
        this.save(menu);
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateMenu(MenuUpdateDTO updateDTO) {
        SysMenu menu = this.getById(updateDTO.getId());
        if (menu == null) {
            throw new BusinessException("菜单不存在");
        }
        
        BeanUtil.copyProperties(updateDTO, menu);
        this.updateById(menu);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteMenu(Long menuId) {
        SysMenu menu = this.getById(menuId);
        if (menu == null) {
            throw new BusinessException("菜单不存在");
        }
        
        LambdaQueryWrapper<SysMenu> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysMenu::getParentId, menuId);
        if (this.count(wrapper) > 0) {
            throw new BusinessException("存在下级菜单，无法删除");
        }
        this.removeById(menuId);
    }

    private MenuTreeVO convertToTreeVO(SysMenu menu) {
        MenuTreeVO treeVO = new MenuTreeVO();
        BeanUtil.copyProperties(menu, treeVO);
        return treeVO;
    }

    private List<MenuTreeVO> buildTree(List<MenuTreeVO> menuList) {
        List<MenuTreeVO> rootList = new ArrayList<>();
        for (MenuTreeVO menu : menuList) {
            if (menu.getParentId() == null || menu.getParentId() == 0) {
                rootList.add(menu);
            }
        }
        for (MenuTreeVO root : rootList) {
            buildChildren(root, menuList);
        }
        return rootList;
    }

    private void buildChildren(MenuTreeVO parent, List<MenuTreeVO> menuList) {
        List<MenuTreeVO> children = new ArrayList<>();
        for (MenuTreeVO menu : menuList) {
            if (parent.getId().equals(menu.getParentId())) {
                children.add(menu);
            }
        }
        parent.setChildren(children);
        for (MenuTreeVO child : children) {
            buildChildren(child, menuList);
        }
    }
}
