from flask import Flask, render_template, request
import json
import pymongo 
from datetime import datetime, timedelta, date
app = Flask(__name__) 

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["Log"]
mycol = mydb["Employees"]

@app.route('/')
def login():
	return render_template('login.html')
	
def get_date(datetime_obj):
	return datetime_obj.strftime("%d/%m/%Y")

def get_time(datetime_obj):
	return datetime_obj.strftime("%H:%M:%S")

def to_datetime(year, month, date):
	return datetime(year, month, date)

def fill_template_with_records(results):
	log_by_date = {}
	for result in results:
		try:
			_datetime = result['datetime']
		except:
			continue
		_date = get_date(_datetime)
		time = get_time(_datetime)
		if _date not in log_by_date:
			log_by_date[_date] = []
		log_by_date[_date].append(
			{'name': result['name'],
			 'time': time,
			 'status': result.get('status', "Unknown")})
	return render_template('log.html', log_by_date=log_by_date)

@app.route('/Attendance', methods = ['GET'])
def default():
	now = date.today()
	now = datetime(now.year, now.month, now.day)
	results = mycol.find({'datetime': {'$gte': now}})
	log_by_date = {}
	names = set()
	for result in results:
		try:
			_datetime = result['datetime']
		except:
			continue
		_date = get_date(_datetime)
		time = get_time(_datetime)
		if _date not in log_by_date:
			log_by_date[_date] = []
		log_by_date[_date].append(
			{'name': result['name'],
			 'time': time,
			 'status': result.get('status', "Unknown")})
		names.add(result['name'])
	return render_template('index.html', log_by_date=log_by_date, names=names)

@app.route('/filter_by_date', methods=['POST'])
def filter_by_date():
	data = request.form
	from_date = data.get('from_date')
	to_date = data.get('to_date')
	name = data.get('name')
	names = [name]
	conditions = {}
	if from_date and to_date:
		from_year, from_month, from_date = from_date.split("-")
		to_year, to_month, to_date = to_date.split("-")
		from_date = to_datetime(int(from_year), int(from_month), int(from_date))
		to_date = to_datetime(int(to_year), int(to_month), int(to_date)) + timedelta(days=1)
		to_date = datetime(to_date.year, to_date.month, to_date.day)
		conditions['datetime'] = {"$gte": from_date, "$lte": to_date}
	if name and names:
		conditions["name"] = {"$in": names}
	results = mycol.find(conditions)
	return fill_template_with_records(results)

# @app.route('/entry', methods=['POST'])
# def make_entry():
# 	data = json.loads(request.data)
# 	names = data.get('names', [])
# 	status = data.get('status', 'Unknown')
# 	now = datetime.now()
# 	for name in names:
# 		mycol.insert_one({'name': name, 'datetime': now, 'status': status})

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)

