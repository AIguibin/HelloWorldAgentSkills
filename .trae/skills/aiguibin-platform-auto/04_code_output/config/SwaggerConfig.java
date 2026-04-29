package com.aiguibin.platform.common.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {
    
    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("架构管理平台API")
                .description("aiguibin-platform-arch API文档")
                .version("1.0.0")
                .contact(new Contact()
                    .name("AIguibin")
                    .email("support@aiguibin.com")));
    }
}
