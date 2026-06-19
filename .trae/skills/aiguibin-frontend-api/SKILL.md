---
name: "frontend-api-mock"
description: "指导前端开发不使用写死数据，通过API接口获取数据。无后端服务时，提供本地mock方案，确保入参正确，返回标准JSON结构。"
---

# 前端API接口请求与本地Mock技能

## 功能介绍

该技能指导前端开发人员在编写页面逻辑时，不使用写死的数据，而是通过API接口获取数据。当没有后端服务时，提供完整的本地mock方案，确保：

- API请求结构规范
- 入参设置正确
- 返回标准JSON格式
- 支持多种前端框架
- 本地开发环境mock数据

## 使用场景

当你需要开发前端页面并处理数据时，该技能可以帮助你：

- 编写规范的API请求代码
- 避免使用写死的数据
- 在无后端服务时实现本地mock
- 确保API请求结构正确
- 生成标准的JSON返回数据

## 示例代码

### React API请求示例

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 正确设置API请求，包含必要的参数
    const fetchUsers = async () => {
      try {
        setLoading(true);
        // 真实环境下请求后端API
        // const response = await axios.get('/api/users', {
        //   params: { page: 1, limit: 10 }
        // });
        
        // 本地开发时使用mock数据
        const response = await axios.get('/api/mock/users', {
          params: { page: 1, limit: 10 }
        });
        
        setUsers(response.data.data);
      } catch (err) {
        setError('Failed to fetch users');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>User List</h1>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name} - {user.email}</li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;
```

### Vue API请求示例

```javascript
<template>
  <div>
    <h1>Product List</h1>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else>
      <li v-for="product in products" :key="product.id">
        {{ product.name }} - ${{ product.price }}
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProductList',
  data() {
    return {
      products: [],
      loading: false,
      error: null
    };
  },
  mounted() {
    this.fetchProducts();
  },
  methods: {
    async fetchProducts() {
      try {
        this.loading = true;
        // 正确设置请求参数
        const params = {
          category: 'electronics',
          minPrice: 100,
          sort: 'price'
        };
        
        // 本地mock请求
        const response = await axios.get('/api/mock/products', { params });
        this.products = response.data.data;
      } catch (err) {
        this.error = 'Failed to fetch products';
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

### 本地Mock配置示例（Vite）

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { createServer } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        bypass: (req, res) => {
          // 处理mock请求
          if (req.url.startsWith('/api/mock')) {
            return handleMockRequest(req, res);
          }
          return null;
        }
      }
    }
  }
});

// Mock数据处理函数
function handleMockRequest(req, res) {
  const url = req.url;
  
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  // 根据不同的API路径返回不同的mock数据
  if (url === '/api/mock/users') {
    // 解析请求参数
    const params = new URLSearchParams(req.url.split('?')[1]);
    const page = parseInt(params.get('page') || '1');
    const limit = parseInt(params.get('limit') || '10');
    
    // 返回标准JSON结构
    res.end(JSON.stringify({
      code: 200,
      message: 'success',
      data: [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com' }
      ].slice((page - 1) * limit, page * limit),
      pagination: {
        page,
        limit,
        total: 3
      }
    }));
  } 
  else if (url.startsWith('/api/mock/products')) {
    res.end(JSON.stringify({
      code: 200,
      message: 'success',
      data: [
        { id: 1, name: 'Laptop', price: 999.99, category: 'electronics' },
        { id: 2, name: 'Smartphone', price: 699.99, category: 'electronics' },
        { id: 3, name: 'Headphones', price: 199.99, category: 'electronics' }
      ]
    }));
  } 
  else {
    res.statusCode = 404;
    res.end(JSON.stringify({
      code: 404,
      message: 'API not found'
    }));
  }
}
```

### Axios拦截器配置

```javascript
import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // 确保参数格式正确
    if (config.method === 'get') {
      config.params = config.params || {};
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    // 统一处理响应数据
    return response.data;
  },
  error => {
    // 统一处理错误
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
```

## 本地Mock方案

### 1. 使用Vite Mock插件

```bash
npm install vite-plugin-mock mockjs --save-dev
```

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import { viteMockServe } from 'vite-plugin-mock';

export default defineConfig({
  plugins: [
    viteMockServe({
      mockPath: './mock',
      enable: true
    })
  ]
});
```

```javascript
// mock/user.js
import { MockMethod } from 'vite-plugin-mock';

export default [
  {
    url: '/api/users',
    method: 'get',
    response: (req) => {
      const { page = 1, limit = 10 } = req.query;
      return {
        code: 200,
        message: 'success',
        data: Array.from({ length: limit }).map((_, index) => ({
          id: (page - 1) * limit + index + 1,
          name: `User ${(page - 1) * limit + index + 1}`,
          email: `user${(page - 1) * limit + index + 1}@example.com`
        })),
        pagination: {
          page: Number(page),
          limit: Number(limit),
          total: 100
        }
      };
    }
  }
] as MockMethod[];
```

### 2. 使用JSON Server

```bash
npm install -g json-server
```

```json
// db.json
{
  "users": [
    { "id": 1, "name": "John Doe", "email": "john@example.com" },
    { "id": 2, "name": "Jane Smith", "email": "jane@example.com" }
  ],
  "products": [
    { "id": 1, "name": "Laptop", "price": 999.99 },
    { "id": 2, "name": "Smartphone", "price": 699.99 }
  ]
}
```

```bash
json-server --watch db.json --port 3001
```

### 3. 使用Fetch API本地Mock

```javascript
// mockService.js
const mockData = {
  users: [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
  ]
};

// 重写fetch方法
const originalFetch = window.fetch;
window.fetch = async (url, options) => {
  // 处理本地mock请求
  if (url.startsWith('/api/mock')) {
    const mockUrl = url.replace('/api/mock', '');
    
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // 返回mock数据
    return new Response(JSON.stringify({
      code: 200,
      message: 'success',
      data: mockData[mockUrl.slice(1)] || []
    }), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
  
  // 其他请求使用原始fetch
  return originalFetch(url, options);
};
```

## 最佳实践

1. **API请求封装**：创建统一的API请求工具，处理请求拦截、响应拦截、错误处理
2. **参数验证**：确保API请求参数格式正确，避免无效请求
3. **响应格式统一**：后端返回统一的JSON格式，包含code、message、data字段
4. **本地开发mock**：使用mock工具模拟后端API，确保前端开发不依赖后端
5. **环境配置**：根据不同环境（开发、测试、生产）配置不同的API地址
6. **加载状态处理**：所有API请求都要处理加载状态，提升用户体验
7. **错误处理**：统一处理API错误，展示友好的错误信息
8. **缓存策略**：对于不经常变化的数据，使用缓存减少API请求

## 工具推荐

- **API请求库**：Axios, Fetch API
- **Mock工具**：Vite Mock Server, JSON Server, Mock.js, MSW (Mock Service Worker)
- **API文档**：Swagger, Postman, Apiary
- **状态管理**：Redux (React), Vuex/Pinia (Vue), Zustand, Jotai
- **网络调试**：Chrome DevTools, Charles, Fiddler

## 常见问题

### Q: 如何确保API请求参数正确？
A: 使用TypeScript定义API请求类型，或使用JSON Schema验证参数格式。所有参数都应该有默认值，避免undefined值传递给后端。

### Q: 本地mock数据如何与真实API保持一致？
A: 根据API文档定义mock数据结构，定期更新mock数据以匹配最新的API规范。

### Q: 如何处理不同环境的API地址？
A: 使用环境变量配置不同环境的API地址，例如：
```javascript
const API_BASE_URL = {
  development: '/api',
  test: 'https://test-api.example.com',
  production: 'https://api.example.com'
}[import.meta.env.MODE];
```

### Q: 如何优化API请求性能？
A: 1. 使用防抖和节流减少请求次数；2. 实现请求缓存；3. 使用分页加载大量数据；4. 合并多个相关请求；5. 使用CDN加速静态资源。

### Q: 如何处理API请求失败？
A: 1. 实现错误重试机制；2. 展示友好的错误信息；3. 记录错误日志；4. 提供用户反馈机制。

## 版本历史

- v1.0.0: 初始版本，支持React和Vue API请求示例，提供本地mock方案
- v1.1.0: 添加Vite Mock插件和JSON Server配置示例
- v1.2.0: 增加API请求拦截器和响应拦截器示例
- v1.3.0: 完善最佳实践和常见问题解答