create table menu(dish_id int primary key auto_increment, name varchar(20), cuisine varchar(20), type varchar(10), rate decimal(5,2));
create table employee(emp_id varchar(30) primary key, name varchar(30), age int, gender varchar(10), role int, apt_no varchar (100), street varchar (100), zip varchar(50), salary int, outlet varchar(20), reports_to_id varchar(30), email varchar(50));
create table customer(cust_id varchar(30) primary key, name varchar(30), age int, gender varchar(10), apt_no varchar (100), street varchar (100), zip varchar(50), contact_no varchar(20), num_order int default 0, special_priv varchar(50), email varchar(50));
alter table employee add foreign key (reports_to_id) references employee(emp_id);
insert into employee values ('main','Proprietor','35','Female',1,'45','Malviya Nagar','Varanasi','221009',0,'outlet_hg','main','proprietor.sd@gmail.com');

create table employee_phone(emp_id varchar(30) references employee(emp_id), contact_no varchar(10));
alter table employee_phone add primary key (emp_id, contact_no);

create table outlet (out_id varchar(20) primary key, apt_no varchar(20), street varchar(30), zip varchar(6), contact varchar (10));

create table order(order_id int primary key auto_increment, date datetime, cust_id varchar(30) foreign key fk1 references customer(cust_id), emp_id varchar(30) foreign key fk2 references employee(emp_id) , out_id varchar(20) foreign key fk3 references outlet(out_id), status int, total int);







