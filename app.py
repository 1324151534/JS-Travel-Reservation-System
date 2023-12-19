from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 导入 CORS
from sqlalchemy import func
from flask import abort

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/TravelSystem'

db = SQLAlchemy(app)

# 定义数据模型
class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)  # 自动增长的ID
    flightnum = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    numseats = db.Column(db.Integer, nullable=False)
    numavail = db.Column(db.Integer, nullable=False)
    fromcity = db.Column(db.String(255), nullable=False)
    arivcity = db.Column(db.String(255), nullable=False)

class Hotel(db.Model):
    __tablename__ = 'hotels'
    location = db.Column(db.String(255), primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    numrooms = db.Column(db.Integer, nullable=False)
    numavail = db.Column(db.Integer, nullable=False)

class Bus(db.Model):
    __tablename__ = 'bus'
    id = db.Column(db.Integer, primary_key=True)  # 自动增长的ID
    location = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    numbus = db.Column(db.Integer, nullable=False)
    numavail = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    __tablename__ = 'customers'
    custname = db.Column(db.String(255), primary_key=True)
    custid = db.Column(db.Integer, primary_key=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    resvkey = db.Column(db.Integer, primary_key=True)  # 自动增长的ID
    custname = db.Column(db.String(255), db.ForeignKey('customers.custname'), nullable=False)
    resvtype = db.Column(db.Integer, nullable=False)
    flightid = db.Column(db.Integer, db.ForeignKey('flights.id'))  # 外键引用
    busid = db.Column(db.Integer, db.ForeignKey('bus.id'))  # 外键引用
    hotellocation = db.Column(db.String(255), db.ForeignKey('hotels.location'))  # 外键引用

# 示例路由：获取所有航班信息
@app.route('/flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()

    # 将航班信息转换为JSON格式
    flights_data = []
    for flight in flights:
        flight_data = {
            'id' : flight.id,
            'flight_num': flight.flightnum,
            'from_city': flight.fromcity,
            'ariv_city': flight.arivcity,
            'num_seats': flight.numseats,
            'num_avail': flight.numavail,
            'price': flight.price
        }
        flights_data.append(flight_data)

    return jsonify(flights_data)

@app.route('/flights/<from_city>', methods=['GET'])
def get_flights_by_city(from_city):
    # 将传入的城市名称转换为小写，并查询数据库
    flights = Flight.query.filter(func.lower(Flight.fromcity) == func.lower(from_city)).all()

    # 将航班信息转换为JSON格式
    flights_data = []
    for flight in flights:
        flight_data = {
            'id' : flight.id,
            'flight_num': flight.flightnum,
            'from_city': flight.fromcity,
            'ariv_city': flight.arivcity,
            'num_seats': flight.numseats,
            'num_avail': flight.numavail,
            'price': flight.price
        }
        flights_data.append(flight_data)

    # 返回JSON响应
    return jsonify(flights_data)

# 新的路由：创建预定记录
@app.route('/flights', methods=['POST'])
def create_flight_reservation():
    # 获取前端POST的数据
    data = request.json

    # 确保必要的数据存在
    required_fields = ['custname', 'flight_id']
    if not all(field in data for field in required_fields):
        abort(400, description='Missing required fields')

    # 解析数据
    custname = data['custname']
    flight_id = data['flight_id']

    # 检查用户是否存在，如果不存在则创建用户
    customer = Customer.query.filter_by(custname=custname).first()
    if customer is None:
        # 创建用户并获取自增的用户id
        new_customer = Customer(custname=custname)
        db.session.add(new_customer)
        db.session.commit()

    # 检查航班是否存在
    flight = Flight.query.get(flight_id)
    if flight is None:
        abort(404, description='Flight not found')

    # 检查可用座位是否足够
    if flight.numavail <= 0:
        abort(400, description='No available seats for this flight')

    # 创建预定记录
    reservation = Reservation(
        custname=custname,
        resvtype=1,  # 航班类型
        flightid=flight_id
    )
    
    # 更新可用座位数量
    flight.numavail -= 1

    # 保存到数据库
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation created successfully'}), 201

# 获取巴士信息
@app.route('/bus/<bus_location>', methods=['GET'])
def get_bus_by_location(bus_location):
    # 将传入的巴士位置名称转换为小写，并查询数据库
    buses = Bus.query.filter(func.lower(Bus.location) == func.lower(bus_location)).all()

    # 将巴士信息转换为JSON格式
    buses_data = []
    for bus in buses:
        bus_data = {
            'id': bus.id,
            'location': bus.location,
            'price': bus.price,
            'num_bus': bus.numbus,
            'num_avail': bus.numavail
        }
        buses_data.append(bus_data)

    # 返回JSON响应
    return jsonify(buses_data)

# 获取巴士信息
@app.route('/bus', methods=['GET'])
def get_bus():
    # 将传入的巴士位置名称转换为小写，并查询数据库
    buses = Bus.query.all()

    # 将巴士信息转换为JSON格式
    buses_data = []
    for bus in buses:
        bus_data = {
            'id': bus.id,
            'location': bus.location,
            'price': bus.price,
            'num_bus': bus.numbus,
            'num_avail': bus.numavail
        }
        buses_data.append(bus_data)

    # 返回JSON响应
    return jsonify(buses_data)

# 新的路由：创建预定记录
@app.route('/bus', methods=['POST'])
def create_bus_reservation():
    # 获取前端POST的数据
    data = request.json

    # 确保必要的数据存在
    required_fields = ['custname', 'bus_id']
    if not all(field in data for field in required_fields):
        abort(400, description='Missing required fields')

    # 解析数据
    custname = data['custname']
    bus_id = data['bus_id']

    # 检查用户是否存在，如果不存在则创建用户
    customer = Customer.query.filter_by(custname=custname).first()
    if customer is None:
        # 创建用户并获取自增的用户id
        new_customer = Customer(custname=custname)
        db.session.add(new_customer)
        db.session.commit()

    # 检查航班是否存在
    bus = Bus.query.get(bus_id)
    if bus is None:
        abort(404, description='Bus not found')

    # 检查可用座位是否足够
    if bus.numavail <= 0:
        abort(400, description='No available seats for this flight')

    # 创建预定记录
    reservation = Reservation(
        custname=custname,
        resvtype=3,  # 巴士类型
        busid=bus_id
    )
    
    # 更新可用座位数量
    bus.numavail -= 1

    # 保存到数据库
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation created successfully'}), 201

# 示例路由：获取所有宾馆信息
@app.route('/hotels', methods=['GET'])
def get_hotels():
    hotels = Hotel.query.all()
    return jsonify([hotel.location for hotel in hotels])

# 主函数
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
