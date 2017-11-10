from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.db import connection, IntegrityError, transaction
from datetime import datetime, date
import re

def home(request):
	return render(request,"home.html")

def menu(request):
	cursor = connection.cursor()
	get_cuisine="SELECT DISTINCT cuisine FROM menu;"
	cursor.execute(get_cuisine)
	cuisine_list = list(cursor.fetchall())
	li=[]
	for c in cuisine_list:
		cui=str(c[0])
		get_dishes="SELECT dish_id, name, type, rate FROM menu WHERE cuisine='"+cui+"' ORDER BY rate;"
		cursor.execute(get_dishes)
		dish_list=list(cursor.fetchall())
		for i in range(len(dish_list)):
			dish_list[i]=list(dish_list[i])
		temp=[]
		temp.append(str(cui))
		temp.append(dish_list)
		li.append(temp)
	return render(request,"menu.html",{'menu':li})

def edit_dish(request):
	cursor = connection.cursor()
	if request.GET.get('dish_name') and request.GET.get('dish_type') and request.GET.get('dish_rate'):
		cursor.execute("UPDATE menu set name='" + request.GET.get('dish_name') + "' where dish_id=" + request.GET.get('dish_id') + ";")
		cursor.execute("UPDATE menu set type='" + request.GET.get('dish_type') + "' where dish_id=" + request.GET.get('dish_id') + ";")
		cursor.execute("UPDATE menu set rate=" + request.GET.get('dish_rate') + " where dish_id=" + request.GET.get('dish_id') + ";")
	
	return HttpResponseRedirect(reverse('menu'))

def delete_dish(request):
	cursor=connection.cursor()
	cursor.execute("DELETE FROM menu where dish_id="+request.GET.get('dish_id')+";")
	return HttpResponseRedirect(reverse('menu'))

def add_dish(request):
	cursor=connection.cursor()
	cursor.execute("INSERT INTO menu (name, cuisine, type, rate) VALUES ('"+request.GET.get('dish_name')+"', '"+request.GET.get('dish_cuisine')+"', '"+request.GET.get('dish_type')+"', "+request.GET.get('dish_rate')+");")
	return HttpResponseRedirect(reverse('menu'))

def register(request):
	
	return render(request,'register.html')

def create_acc(request):
	if request.POST:
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		contact_no = request.POST['contact_no']
		email = request.POST['email']
		age = request.POST['age']
		gender = request.POST['gender']
		aptno = request.POST['aptno']
		street = request.POST['street']
		zip = request.POST['zip']
		username = request.POST['username']
		pwd = request.POST['pwd']	
		pwd2=request.POST['pwd2']
		priv=request.POST['priv']

	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)
	contact_no_check=1
	for c in contact_no:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not (len(contact_no) == 10):
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	cursor = connection.cursor()
	cursor.execute("SELECT * from customer where cust_id='"+username+"';")
	data = cursor.fetchone()
	connection.close()

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return render(request,'register.html')
	elif not email_check:
		messages.error(request, 'Invalid e-mail address!')
		return render(request,'register.html')
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return render(request,'register.html')
	elif data is not None:
		messages.error(request, 'The username already exists!')
		return render(request,'register.html')
	elif not (pwd==pwd2):
		messages.error(request,'Passwords do not match!')
		return render(request,'register.html')
	else:
		cursor = connection.cursor()
		try:
			cursor.execute("INSERT into customer values('"+username+"','"+name+"',"+age+",'"+gender+"','"+aptno
				+"','"+street+"','"+zip+"','"+contact_no+"',0,'"+priv+"','"+email+"');")
			
			user = User.objects.create_user(username, None, pwd)
			connection.commit()
			messages.success(request, 'Customer successfully registered.')
			return render(request,'home.html')
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('home'))

def logout(request):
	cursor=connection.cursor()
	if request.user.is_staff:
		try:
			cursor.execute("select order_id from orders where emp_id='"+request.user.username+"' and status=1;")
			olist=list(cursor.fetchall())
			print olist
			for i in range(len(olist)):
				x=olist[i][0]
				cursor.execute("delete from order_meals where order_id="+str(x)+";")
				cursor.execute("delete from orders where order_id="+str(x)+";")
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
	else:
		try:
			cursor.execute("select order_id from orders where cust_id='"+request.user.username+"' and status=1;")
			olist=list(cursor.fetchall())
			for i in range(len(olist)):
				x=olist[i][0]
				cursor.execute("delete from order_meals where order_id="+str(x)+";")
				cursor.execute("delete from orders where order_id="+str(x)+";")
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()

	auth.logout(request)
	messages.success(request, 'Successfully logged out.')
	return HttpResponseRedirect(reverse('home'))


def login(request):
	if request.POST:							
		username = request.POST['username']
		pwd = request.POST['pwd']

		cursor = connection.cursor()		
		cursor.execute("SELECT * from auth_user where username='"+username+"';")
		data = cursor.fetchone()
		connection.close()

		if data is not None:				
			username = data[4]
			user = auth.authenticate(username=username, password=pwd)			
			if user is not None:
				auth.login(request, user)									
				return HttpResponseRedirect(reverse('home'))
			else:																	
				messages.error(request, 'The username and/or password is incorrect!')
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		messages.error(request, 'The username does not exist!')	
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))	
	return render(request,"home.html")


def emp_det(request):
	query1="SELECT DISTINCT reports_to_id FROM employee WHERE role=3 or role=2;"
	cursor = connection.cursor()
	cursor.execute(query1)
	manager_list=list(cursor.fetchall())
	li=[]
	tup=cursor.fetchall()
	for m in manager_list:
		mgr=str(m[0])
		eidl=[]
		query2="SELECT * FROM employee where reports_to_id='"+mgr+"';"
		cursor.execute(query2)
		emp_list=list(cursor.fetchall())
		for i in range(len(emp_list)):
			emp_list[i]=list(emp_list[i])
		temp=[]
		temp.append(str(mgr))
		temp.append(emp_list)
		li.append(temp)
	li2=[]
	cursor.execute("SELECT out_id FROM outlet;")
	for i in list(cursor.fetchall()):
		li2.append(i[0])
	print li2
	return render(request,'emp_det.html',{'emp_det':li,'outlet_l':li2})

def edit_emp(request):
	if request.POST:
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		email = request.POST['email']
		contact_no1=request.POST['contact_no1']
		contact_no2=request.POST['contact_no2']
		age = request.POST['age']
		gender = request.POST['gender']
		apt_no = request.POST['apt_no']
		street = request.POST['street']
		zip = request.POST['zip']
		emp_id = request.POST['emp_id']
		salary = request.POST['salary']

	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)

	contact_no_check=1
	for c in contact_no1:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	for c in contact_no2:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not (len(contact_no1) == 10 and len(contact_no2) == 10):
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if not email_check:
		messages.error(request, 'Invalid e-mail address!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		cursor = connection.cursor()
		try:
			if name and email and contact_no1 and contact_no2 and age and gender and apt_no and street and zip and salary:
				print name
				cursor.execute("UPDATE employee set name='" + name + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set age='" + age + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set gender='" + gender + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set email='" + email + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set contact_no1='" + contact_no1 + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set contact_no2='" + contact_no2 + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set apt_no='" + apt_no + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set street='" + street + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set zip='" + zip + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set salary='" + salary + "' where emp_id='" + emp_id + "';")
				
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('emp_det'))


def delete_emp(request):
	if request.POST:
		emp_id=request.POST['emp_id']
	cursor = connection.cursor()
	cursor.execute("DELETE FROM employee where emp_id='"+emp_id+"';")
	cursor.execute("DELETE FROM auth_user where username='"+emp_id+"';")
	connection.close()

	return HttpResponseRedirect(reverse('emp_det'))

def add_emp(request):
	if request.POST:
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		email = request.POST['email']
		contact_no1=request.POST['contact_no1']
		contact_no2=request.POST['contact_no2']
		age = request.POST['age']
		gender = request.POST['gender']
		apt_no = request.POST['apt_no']
		street = request.POST['street']
		zip = request.POST['zip']
		emp_id = request.POST['emp_id']
		reports_to_id=request.POST['reports_to_id']
		outlet=request.POST['outlet']
		salary=request.POST['salary']

	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)

	cursor = connection.cursor()
	cursor.execute("SELECT * from employee where emp_id='"+emp_id+"';")
	data = cursor.fetchone()
	cursor.close()

	contact_no_check=1
	for c in contact_no1:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	for c in contact_no2:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not (len(contact_no1) == 10 and len(contact_no2) == 10):
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if not email_check:
		messages.error(request, 'Invalid e-mail address!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif data is not None:
		messages.error(request, 'Employee ID already exists!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		cursor = connection.cursor()
		try:
			if emp_id and outlet and reports_to_id and name and email and contact_no1 and contact_no2 and age and gender and apt_no and street and zip and salary:
				cursor.execute("INSERT INTO employee VALUES ('"+emp_id+"','"+name+"','"+age+"','"+gender+"',3,'"+apt_no+"','"+street+"','"+zip+"','"+salary+"','"+outlet+"','"+reports_to_id+"','"+email+"','"+contact_no1+"','"+contact_no2+"');")
				
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('emp_det'))

def add_mgr(request):
	if request.POST:
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		email = request.POST['email']
		contact_no1=request.POST['contact_no1']
		contact_no2=request.POST['contact_no2']
		age = request.POST['age']
		gender = request.POST['gender']
		apt_no = request.POST['apt_no']
		street = request.POST['street']
		zip = request.POST['zip']
		emp_id = request.POST['emp_id']
		pwd1=request.POST['pwd1']
		pwd2=request.POST['pwd2']
		outlet=request.POST['outlet']
		salary=request.POST['salary']

	cursor = connection.cursor()
	cursor.execute("SELECT * from employee where emp_id='"+emp_id+"';")
	data = cursor.fetchone()
	cursor.close()
	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)

	contact_no_check=1
	for c in contact_no1:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	for c in contact_no2:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not (len(contact_no1) == 10 and len(contact_no2) == 10):
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not email_check:
		messages.error(request, 'Invalid e-mail address!')
	elif not pwd1==pwd2:
		messages.error(request, 'Passwords do not match!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif data is not None:
		messages.error(request, 'Employee ID i.e. username already exists!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		cursor = connection.cursor()
		try:
			if emp_id and outlet and name and email and contact_no1 and contact_no2 and age and gender and apt_no and street and zip and salary:
				cursor.execute("INSERT INTO employee VALUES ('"+emp_id+"','"+name+"','"+age+"','"+gender+"',2,'"+apt_no+"','"+street+"','"+zip+"','"+salary+"','"+outlet+"','"+emp_id+"','"+email+"','"+contact_no1+"','"+contact_no2+"');")
				user = User.objects.create_user(emp_id, None, pwd1)
				user.is_staff=True 
				user.save()

			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('emp_det'))

def profile(request):
	cursor=connection.cursor()
	if request.user.is_staff:
		cursor.execute("SELECT * FROM employee WHERE emp_id='"+request.user.username+"';")
	else:
		cursor.execute("SELECT * FROM customer WHERE cust_id='"+request.user.username+"';")
	profile=list(list(cursor.fetchall())[0])
	return render(request,'profile.html',{'profile':profile})

def edit_profile_emp(request):
	if request.POST:
		print "afgfu"
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		email = request.POST['email']
		contact_no1=request.POST['contact_no1']
		contact_no2=request.POST['contact_no2']
		age = request.POST['age']
		gender = request.POST['gender']
		apt_no = request.POST['apt_no']
		street = request.POST['street']
		zip = request.POST['zip']
		emp_id = request.POST['emp_id']

	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)
	print "asdsds"
	contact_no_check=1
	for c in contact_no1:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	for c in contact_no2:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not (len(contact_no1) == 10 and len(contact_no2) == 10):
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if not email_check:
		messages.error(request, 'Invalid e-mail address!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		cursor = connection.cursor()
		try:
			if name and email and contact_no1 and contact_no2 and age and gender and apt_no and street and zip:
				cursor.execute("UPDATE employee set name='" + name + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set age='" + age + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set gender='" + gender + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set email='" + email + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set contact_no1='" + contact_no1 + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set contact_no2='" + contact_no2 + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set apt_no='" + apt_no + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set street='" + street + "' where emp_id='" + emp_id + "';")
				cursor.execute("UPDATE employee set zip='" + zip + "' where emp_id='" + emp_id + "';")				
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('profile'))


def edit_profile_cust(request):
	if request.POST:
		name = request.POST['name']							# Fetch the values entered by the admin in the registration form
		email = request.POST['email']
		contact_no=request.POST['contact_no']
		age = request.POST['age']
		gender = request.POST['gender']
		apt_no = request.POST['apt_no']
		street = request.POST['street']
		zip = request.POST['zip']
		cust_id = request.POST['cust_id']

	email_check = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)

	contact_no_check=1
	for c in contact_no:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			contact_no_check=0
			break
	if not len(contact_no) == 10:
		contact_no_check=0

	zip_check=1
	for c in zip:
		if c not in ['0','1','2','3','4','5','6','7','8','9']:
			zip_check=0
			break
	if not (len(zip) == 6):
		zip_check=0

	if not contact_no_check:
		messages.error(request, 'Invalid mobile number!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	if not email_check:
		messages.error(request, 'Invalid e-mail address!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	elif not zip_check:
		messages.error(request, 'Invalid zip code!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		cursor = connection.cursor()
		try:
			if name and email and contact_no and age and gender and apt_no and street and zip:
				cursor.execute("UPDATE customer set name='" + name + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set age='" + age + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set gender='" + gender + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set email='" + email + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set contact_no='" + contact_no1 + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set apt_no='" + apt_no + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set street='" + street + "' where cust_id='" + cust_id + "';")
				cursor.execute("UPDATE customer set zip='" + zip + "' where cust_id='" + cust_id + "';")				
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('profile'))

def refreshmodal(request):
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def offers(request):
	cursor=connection.cursor()
	cursor.execute("SELECT * FROM offer;")
	offer_list=list(cursor.fetchall())
	for i in range(len(offer_list)):
		offer_list[i]=list(offer_list[i])
	return render(request,'offers.html',{'offers':offer_list})

def delete_offer(request):
	cursor=connection.cursor()
	cursor.execute("DELETE FROM offer WHERE offer_id='"+request.GET['offer_id']+"';")
	return HttpResponseRedirect(reverse('offers'))

def edit_offer(request):
	if request.POST:
		offer_id=request.POST['offer_id']
		percentage=request.POST['percentage']
		min_amt=request.POST['min_amt']
	if offer_id and percentage and min_amt:
		cursor=connection.cursor()
		try:
			if offer_id and percentage and min_amt:
				cursor.execute("UPDATE offer set percentage=" + percentage + " where offer_id='" + offer_id + "';")
				cursor.execute("UPDATE offer set min_amt=" + min_amt + " where offer_id='" + offer_id + "';")
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('offers'))

def add_offer(request):
	if request.POST:
		offer_id=request.POST['offer_id']
		percentage=request.POST['percentage']
		min_amt=request.POST['min_amt']

	cursor=connection.cursor()
	cursor.execute("SELECT * FROM offer WHERE offer_id='"+offer_id+"';")
	data=cursor.fetchone()

	if data is not None:
		messages.error(request, 'The offer ID already exists!')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))		
	else:
		
		try:
			if offer_id and percentage and min_amt:
				q="INSERT INTO offer VALUES ('"+offer_id+"',"+percentage+","+min_amt+");"
				cursor.execute(q)
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
		connection.close()
		
		return HttpResponseRedirect(reverse('offers'))

def add_to_order(request):
	cursor=connection.cursor()
	dish_id=request.GET.get('dish_id')
	cursor.execute("select rate from menu where dish_id="+str(dish_id))
	rate=list(list(cursor.fetchall())[0])[0]
	print rate
	if request.user.is_staff:
		cursor.execute("select * from orders where cust_id='offline' and emp_id='"+request.user.username+"' and status=1;")
		data=cursor.fetchone()
		if data is None:
			try:
				cursor.execute("insert into orders (date,cust_id,emp_id,status,total) values (NOW(),'offline','"+request.user.username+"',1,0);")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()
		cursor.execute("select order_id from orders where cust_id='offline' and emp_id='"+request.user.username+"' and status=1;")
		order_id=list(cursor.fetchall())[0][0]
		q="select * from order_meals where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";"
		print q;
		cursor.execute(q)
		data2=cursor.fetchone()
		if data2 is not None:
			try:
				cursor.execute("update order_meals set units=units+1 where order_id="+str(order_id)+" and dish_id="+dish_id+";")
				cursor.execute("update orders set total=total+"+str(rate)+" where order_id="+str(order_id)+";")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()
		else:
			try:
				cursor.execute("insert into order_meals values ("+str(order_id)+","+str(dish_id)+",1)")
				cursor.execute("update orders set total=total+"+str(rate)+" where order_id="+str(order_id)+";")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()
	else:
		cursor.execute("select * from orders where cust_id='"+request.user.username+"' and status=1;")
		data=cursor.fetchone()
		if data is None:
			try:
				cursor.execute("insert into orders (date,cust_id,status,total) values (NOW(),'"+request.user.username+"',1,0);")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()

		cursor.execute("select * from orders where cust_id='"+request.user.username+"' and status=1;")
		order_id=list(cursor.fetchall())[0][0]
		q="select * from order_meals where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";"
		print q;
		cursor.execute(q)
		data2=cursor.fetchone()
		if data2 is not None:
			try:
				cursor.execute("update order_meals set units=units+1 where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";")
				cursor.execute("update orders set total=total+"+str(rate)+" where order_id="+str(order_id)+";")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()
		else:
			try:
				cursor.execute("insert into order_meals values ("+str(order_id)+","+str(dish_id)+",1)")
				cursor.execute("update orders set total=total+"+str(rate)+" where order_id="+str(order_id)+";")
				connection.commit()
			except Exception as e:
				print e
				connection.rollback()
	return HttpResponseRedirect(reverse('menu'))

def checkout(request):
	cursor=connection.cursor()
	if request.user.is_staff:
		cursor.execute("select order_id from orders where cust_id='offline' and emp_id='"+request.user.username+"' and status=1;")
		x=cursor.fetchone()
	else:
		cursor.execute("select * from orders where cust_id='"+request.user.username+"' and status=1;")
		x=cursor.fetchone()
	if x is not None:
		if request.user.is_staff:
			cursor.execute("select order_id from orders where cust_id='offline' and emp_id='"+request.user.username+"' and status=1;")
			order_id=list(cursor.fetchall())[0][0]
		else:
			cursor.execute("select * from orders where cust_id='"+request.user.username+"' and status=1;")
			order_id=list(cursor.fetchall())[0][0]
		cursor.execute("select * from orders where order_id="+str(order_id)+";")
		order_info=list(list(cursor.fetchall())[0])
		q="select menu.dish_id, menu.name, type, rate, units from menu, order_meals where menu.dish_id=order_meals.dish_id and order_meals.order_id="+str(order_id)+";"
		cursor.execute(q)
		dlist=list(cursor.fetchall())
		li=[]
		for i in dlist:
			li.append(list(i))
		li2=[]
		cursor.execute("SELECT out_id FROM outlet;")
		for i in list(cursor.fetchall()):
			li2.append(i[0])
		li3=[]
		cursor.execute("SELECT * FROM offer where min_amt<="+str(order_info[6])+";")
		for i in list(cursor.fetchall()):
			li3.append(list(i))
		return render(request, 'checkout.html', {'order':order_info,'meals':dlist,'outlets':li2,'offers':li3})
	else:
		messages.error(request, 'No items in the order!')
		return render(request, 'checkout.html')


def increment(request):
	dish_id=request.POST['dish_id']
	order_id=request.POST['order_id']
	rate=request.POST['rate']
	try:
		cursor=connection.cursor()
		cursor.execute("update orders set total=total+"+str(rate)+" where order_id="+str(order_id)+";")
		cursor.execute("update order_meals set units=units+1 where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";")
		connection.commit()
	except Exception as e:
		print e
		connection.rollback()
	return HttpResponseRedirect(reverse('checkout'))

def decrement(request):
	dish_id=request.POST['dish_id']
	order_id=request.POST['order_id']
	rate=request.POST['rate']
	nunits=request.POST['nunits']
	print str(nunits>1)
	if int(nunits)>1:
		try:
			cursor=connection.cursor()
			cursor.execute("update orders set total=total-"+str(rate)+" where order_id="+str(order_id)+";")
			cursor.execute("update order_meals set units=units-1 where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";")	
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()
	else: 
		try:
			cursor=connection.cursor()
			cursor.execute("update orders set total=total-"+str(rate)+" where order_id="+str(order_id)+";")
			cursor.execute("delete from order_meals where order_id="+str(order_id)+" and dish_id="+str(dish_id)+";")
			connection.commit()
		except Exception as e:
			print e
			connection.rollback()	
	return HttpResponseRedirect(reverse('checkout'))

def final(request):	
	order_id=request.POST['order_id']
	total=request.POST['total']
	total=int(total)
	offer_id=request.POST['offer']
	out_id=request.POST['outlet']
	cursor=connection.cursor()
	if not offer_id=='NONE':
		q="select percentage from offer where offer_id='"+str(offer_id)+"';"
		
		cursor.execute(q)
		per=int(list(cursor.fetchall())[0][0])
		f_total=int(total-(total*per/100.0))
	else:
		f_total=total
	try:
		q1="update orders set out_id='"+str(out_id)+"' where order_id="+str(order_id)+";"
		print q1
		q2="update orders set total="+str(f_total)+" where order_id="+str(order_id)+";"
		if request.user.is_staff:
			q3="update orders set status=3 where order_id="+str(order_id)+";"
		else:
			q3="update orders set status=2 where order_id="+str(order_id)+";"
		cursor.execute(q1)
		cursor.execute(q2)
		cursor.execute(q3)
		connection.commit()

	except Exception as e:
		print e
		connection.rollback()	

	if request.user.is_staff:
		return render(request,'home.html')
	else:
		l=[order_id,out_id,offer_id,f_total]
		return render(request,'payum.html',{'confirm':l})

def prev(request):
	cursor=connection.cursor()
	if request.user.is_staff:
		q="select outlet from employee where emp_id='"+request.user.username+"';"
		cursor.execute(q)
		out_id=list(cursor.fetchall())[0][0]
		q="select * from orders where out_id='"+out_id+"';"
		l=[]
		cursor.execute(q)
		temp=list(cursor.fetchall())
		for i in  range (len(temp)):
			l.append(list(temp[i]))
	else:
		q="select * from orders where cust_id='"+request.user.username+"';"
		cursor.execute(q)
		l=[]
		cursor.execute(q)
		temp=list(cursor.fetchall())
		for i in  range (len(temp)):
			l.append(list(temp[i]))
	l1=[]
	q="select order_id, menu.name, type, rate, units from menu, order_meals where menu.dish_id=order_meals.dish_id;"
	cursor.execute(q)
	temp=list(cursor.fetchall())
	for i in  range (len(temp)):
		l1.append(list(temp[i]))
	print l1
	return render (request, 'prev.html',{'history':l,'meals':l1})

def process(request):
	order_id=request.POST['order_id']
	q="update orders set status=3 where order_id="+str(order_id)+";"
	q1="update orders set emp_id='"+request.user.username+"' where order_id="+str(order_id)+";"
	try:
		cursor=connection.cursor()
		cursor.execute(q)
		cursor.execute(q1)
		connection.commit()
	except Exception as e:
		print e
		connection.rollback()
	return HttpResponseRedirect(reverse('prev'))







	












