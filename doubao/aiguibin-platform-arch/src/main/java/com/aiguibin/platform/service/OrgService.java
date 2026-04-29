package com.aiguibin.platform.service;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.aiguibin.platform.common.exception.BusinessException;
import com.aiguibin.platform.dto.OrgCreateDTO;
import com.aiguibin.platform.dto.OrgQueryDTO;
import com.aiguibin.platform.dto.OrgUpdateDTO;
import com.aiguibin.platform.entity.SysOrg;
import com.aiguibin.platform.mapper.SysOrgMapper;
import com.aiguibin.platform.vo.OrgTreeVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class OrgService extends ServiceImpl<SysOrgMapper, SysOrg> {

    public List<OrgTreeVO> getOrgTree(OrgQueryDTO queryDTO) {
        LambdaQueryWrapper<SysOrg> wrapper = new LambdaQueryWrapper<>();
        if (StrUtil.isNotBlank(queryDTO.getOrgName())) {
            wrapper.like(SysOrg::getOrgName, queryDTO.getOrgName());
        }
        if (StrUtil.isNotBlank(queryDTO.getOrgType())) {
            wrapper.eq(SysOrg::getOrgType, queryDTO.getOrgType());
        }
        if (queryDTO.getStatus() != null) {
            wrapper.eq(SysOrg::getStatus, queryDTO.getStatus());
        }
        wrapper.orderByAsc(SysOrg::getSortOrder);
        
        List<SysOrg> orgList = this.list(wrapper);
        
        List<OrgTreeVO> treeVOList = orgList.stream()
                .map(this::convertToTreeVO)
                .collect(Collectors.toList());
        
        return buildTree(treeVOList);
    }

    public OrgTreeVO getOrgDetail(Long orgId) {
        SysOrg org = this.getById(orgId);
        if (org == null) {
            throw new BusinessException("机构不存在");
        }
        return convertToTreeVO(org);
    }

    @Transactional(rollbackFor = Exception.class)
    public void createOrg(OrgCreateDTO createDTO) {
        LambdaQueryWrapper<SysOrg> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysOrg::getOrgCode, createDTO.getOrgCode());
        if (this.count(wrapper) > 0) {
            throw new BusinessException("机构编码已存在");
        }
        
        SysOrg org = new SysOrg();
        BeanUtil.copyProperties(createDTO, org);
        
        if (StrUtil.isNotBlank(createDTO.getParentCode())) {
            LambdaQueryWrapper<SysOrg> parentWrapper = new LambdaQueryWrapper<>();
            parentWrapper.eq(SysOrg::getOrgCode, createDTO.getParentCode());
            SysOrg parentOrg = this.getOne(parentWrapper);
            if (parentOrg != null) {
                org.setLevel(parentOrg.getLevel() + 1);
                org.setParentCodes(parentOrg.getParentCodes() + "," + createDTO.getParentCode());
            } else {
                org.setLevel(1);
                org.setParentCodes(createDTO.getParentCode());
            }
        } else {
            org.setLevel(1);
            org.setParentCodes(createDTO.getOrgCode());
        }
        
        if (org.getSortOrder() == null) {
            org.setSortOrder(0);
        }
        org.setStatus(1);
        this.save(org);
    }

    @Transactional(rollbackFor = Exception.class)
    public void updateOrg(OrgUpdateDTO updateDTO) {
        SysOrg org = this.getById(updateDTO.getId());
        if (org == null) {
            throw new BusinessException("机构不存在");
        }
        
        BeanUtil.copyProperties(updateDTO, org);
        this.updateById(org);
    }

    @Transactional(rollbackFor = Exception.class)
    public void deleteOrg(Long orgId) {
        SysOrg org = this.getById(orgId);
        if (org == null) {
            throw new BusinessException("机构不存在");
        }
        
        LambdaQueryWrapper<SysOrg> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(SysOrg::getParentCodes, org.getOrgCode());
        if (this.count(wrapper) > 1) {
            throw new BusinessException("存在下级机构，无法删除");
        }
        this.removeById(orgId);
    }

    private OrgTreeVO convertToTreeVO(SysOrg org) {
        OrgTreeVO treeVO = new OrgTreeVO();
        BeanUtil.copyProperties(org, treeVO);
        return treeVO;
    }

    private List<OrgTreeVO> buildTree(List<OrgTreeVO> orgList) {
        List<OrgTreeVO> rootList = new ArrayList<>();
        for (OrgTreeVO org : orgList) {
            if (StrUtil.isBlank(org.getParentCode()) || "0".equals(org.getParentCode())) {
                rootList.add(org);
            }
        }
        for (OrgTreeVO root : rootList) {
            buildChildren(root, orgList);
        }
        return rootList;
    }

    private void buildChildren(OrgTreeVO parent, List<OrgTreeVO> orgList) {
        List<OrgTreeVO> children = new ArrayList<>();
        for (OrgTreeVO org : orgList) {
            if (parent.getOrgCode().equals(org.getParentCode())) {
                children.add(org);
            }
        }
        parent.setChildren(children);
        for (OrgTreeVO child : children) {
            buildChildren(child, orgList);
        }
    }
}
