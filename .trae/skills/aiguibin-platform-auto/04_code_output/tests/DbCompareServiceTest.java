package com.aiguibin.platform.modules.dbcompare;

import com.aiguibin.platform.modules.dbcompare.service.DbCompareService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DbCompareServiceTest {
    
    @Mock
    private DbCompareService compareService;
    
    @BeforeEach
    void setUp() {
    }
    
    @Test
    @DisplayName("执行DEV环境比对")
    void testCompareDev() {
        doNothing().when(compareService).compareEnv("DEV", "MANUAL");
        
        compareService.compareEnv("DEV", "MANUAL");
        
        verify(compareService, times(1)).compareEnv("DEV", "MANUAL");
    }
    
    @Test
    @DisplayName("执行全环境比对")
    void testCompareAllEnv() {
        doNothing().when(compareService).compareAllEnv("MANUAL");
        
        compareService.compareAllEnv("MANUAL");
        
        verify(compareService, times(1)).compareAllEnv("MANUAL");
    }
}
