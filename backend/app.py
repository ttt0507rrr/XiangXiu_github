from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import hashlib
from config import config

# 创建Flask应用
app = Flask(__name__)

# 加载配置
app_config = config[os.getenv('FLASK_ENV') or 'default']
app.config.from_object(app_config)

# 初始化扩展
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 密码加密函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # 关联
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    collect_items = db.relationship('CollectItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # 关联
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    collect_items = db.relationship('CollectItem', backref='product', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class CollectItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # 唯一约束：用户不能重复收藏同一商品
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_uc'),)

# API路由
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证数据
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': '缺少必要参数'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已被注册'}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hash_password(data['password'])
    )
    
    # 保存到数据库
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user_id': new_user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 验证数据
    if not data.get('username') or not data.get('password'):
        return jsonify({'message': '缺少必要参数'}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    # 验证密码
    if not user or user.password != hash_password(data['password']):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    return jsonify({'message': '登录成功', 'user_id': user.id}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

# 产品相关API
@app.route('/api/products', methods=['GET'])
def get_products():
    # 支持按类别筛选
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()
    
    result = []
    for product in products:
        result.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'image': product.image,
            'category': product.category,
            'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image': product.image,
        'category': product.category,
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

# 购物车相关API
@app.route('/api/cart', methods=['GET'])
def get_cart():
    # 从请求中获取用户ID，实际应用中应该从JWT令牌中获取
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': '缺少用户ID'}), 400
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    result = []
    for item in cart_items:
        result.append({
            'id': item.id,
            'user_id': item.user_id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'product_price': item.product.price,
            'product_image': item.product.image,
            'quantity': item.quantity,
            'total_price': item.product.price * item.quantity,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    
    if not data.get('user_id') or not data.get('product_id') or not data.get('quantity'):
        return jsonify({'message': '缺少必要参数'}), 400
    
    # 检查商品是否存在
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': '商品不存在'}), 404
    
    # 检查购物车中是否已存在该商品
    existing_item = CartItem.query.filter_by(
        user_id=data['user_id'],
        product_id=data['product_id']
    ).first()
    
    if existing_item:
        # 更新数量
        existing_item.quantity += data['quantity']
        db.session.commit()
        return jsonify({'message': '购物车商品数量已更新', 'item_id': existing_item.id}), 200
    else:
        # 添加新商品到购物车
        new_item = CartItem(
            user_id=data['user_id'],
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': '商品已添加到购物车', 'item_id': new_item.id}), 201

@app.route('/api/cart/<int:id>', methods=['PUT'])
def update_cart_item(id):
    data = request.get_json()
    cart_item = CartItem.query.get_or_404(id)
    
    if data.get('quantity'):
        cart_item.quantity = data['quantity']
    
    db.session.commit()
    return jsonify({'message': '购物车商品已更新'}), 200

@app.route('/api/cart/<int:id>', methods=['DELETE'])
def remove_from_cart(id):
    cart_item = CartItem.query.get_or_404(id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': '商品已从购物车移除'}), 200

# 收藏相关API
@app.route('/api/collect', methods=['GET'])
def get_collect():
    # 从请求中获取用户ID，实际应用中应该从JWT令牌中获取
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': '缺少用户ID'}), 400
    
    collect_items = CollectItem.query.filter_by(user_id=user_id).all()
    result = []
    for item in collect_items:
        result.append({
            'id': item.id,
            'user_id': item.user_id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'product_price': item.product.price,
            'product_image': item.product.image,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200

@app.route('/api/collect', methods=['POST'])
def add_to_collect():
    data = request.get_json()
    
    if not data.get('user_id') or not data.get('product_id'):
        return jsonify({'message': '缺少必要参数'}), 400
    
    # 检查商品是否存在
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'message': '商品不存在'}), 404
    
    # 检查是否已收藏
    existing_item = CollectItem.query.filter_by(
        user_id=data['user_id'],
        product_id=data['product_id']
    ).first()
    
    if existing_item:
        return jsonify({'message': '商品已收藏'}), 400
    
    # 添加到收藏
    new_item = CollectItem(
        user_id=data['user_id'],
        product_id=data['product_id']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': '商品已收藏', 'item_id': new_item.id}), 201

@app.route('/api/collect/<int:id>', methods=['DELETE'])
def remove_from_collect(id):
    collect_item = CollectItem.query.get_or_404(id)
    db.session.delete(collect_item)
    db.session.commit()
    return jsonify({'message': '商品已从收藏夹移除'}), 200

if __name__ == '__main__':
    app.run(debug=True)
