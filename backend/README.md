# 湘绣项目后端

## 技术栈

- Flask 3.0.3
- Flask-CORS 4.0.1
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.0.7
- MySQL 8.0

## 项目结构

```
backend/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖列表
├── .env                # 环境变量配置
├── migrations/         # 数据库迁移文件
└── README.md           # 项目说明
```

## 环境变量配置

在`.env`文件中配置以下环境变量：

```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql+mysqlconnector://root:hutbhutb0000@localhost:3306/xiangxiu
SECRET_KEY=your_secret_key_here
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库迁移

```bash
# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade
```

## 运行项目

```bash
python app.py
```

## API接口文档

### 用户相关

#### 注册
- **URL**: `/api/register`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "message": "注册成功",
    "user_id": 1
  }
  ```

#### 登录
- **URL**: `/api/login`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "username": "testuser",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "message": "登录成功",
    "user_id": 1
  }
  ```

#### 获取用户列表
- **URL**: `/api/users`
- **方法**: `GET`
- **响应**:
  ```json
  [
    {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "created_at": "2023-01-01 12:00:00"
    }
  ]
  ```

### 产品相关

#### 获取产品列表
- **URL**: `/api/products`
- **方法**: `GET`
- **查询参数**:
  - `category`: 可选，按类别筛选
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "湘绣作品1",
      "description": "这是一幅精美的湘绣作品",
      "price": 199.0,
      "image": "product1.jpg",
      "category": "刺绣",
      "created_at": "2023-01-01 12:00:00"
    }
  ]
  ```

#### 获取产品详情
- **URL**: `/api/products/{id}`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "id": 1,
    "name": "湘绣作品1",
    "description": "这是一幅精美的湘绣作品",
    "price": 199.0,
    "image": "product1.jpg",
    "category": "刺绣",
    "created_at": "2023-01-01 12:00:00"
  }
  ```

### 购物车相关

#### 获取购物车
- **URL**: `/api/cart`
- **方法**: `GET`
- **查询参数**:
  - `user_id`: 必填，用户ID
- **响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "product_name": "湘绣作品1",
      "product_price": 199.0,
      "product_image": "product1.jpg",
      "quantity": 2,
      "total_price": 398.0,
      "created_at": "2023-01-01 12:00:00"
    }
  ]
  ```

#### 添加到购物车
- **URL**: `/api/cart`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "user_id": 1,
    "product_id": 1,
    "quantity": 2
  }
  ```
- **响应**:
  ```json
  {
    "message": "商品已添加到购物车",
    "item_id": 1
  }
  ```

#### 更新购物车商品
- **URL**: `/api/cart/{id}`
- **方法**: `PUT`
- **请求体**:
  ```json
  {
    "quantity": 3
  }
  ```
- **响应**:
  ```json
  {
    "message": "购物车商品已更新"
  }
  ```

#### 从购物车移除
- **URL**: `/api/cart/{id}`
- **方法**: `DELETE`
- **响应**:
  ```json
  {
    "message": "商品已从购物车移除"
  }
  ```

### 收藏夹相关

#### 获取收藏夹
- **URL**: `/api/collect`
- **方法**: `GET`
- **查询参数**:
  - `user_id`: 必填，用户ID
- **响应**:
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "product_name": "湘绣作品1",
      "product_price": 199.0,
      "product_image": "product1.jpg",
      "created_at": "2023-01-01 12:00:00"
    }
  ]
  ```

#### 添加到收藏夹
- **URL**: `/api/collect`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "user_id": 1,
    "product_id": 1
  }
  ```
- **响应**:
  ```json
  {
    "message": "商品已收藏",
    "item_id": 1
  }
  ```

#### 从收藏夹移除
- **URL**: `/api/collect/{id}`
- **方法**: `DELETE`
- **响应**:
  ```json
  {
    "message": "商品已从收藏夹移除"
  }
  ```
