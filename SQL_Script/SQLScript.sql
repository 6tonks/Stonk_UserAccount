create table Address
(
	addressID bigint auto_increment
		primary key,
	countryCode mediumtext null,
	zipCode mediumtext null,
	state mediumtext null,
	city mediumtext null,
	firstLine mediumtext null,
	secondLine mediumtext null
);

create table Token
(
	userID bigint not null
		primary key,
	token text null,
	expireDateTime datetime null
);

create table User
(
	userID bigint auto_increment
		primary key,
	pwHash text null,
	nameLast text null,
	nameFirst text null,
	email varchar(256) null,
	addressID bigint null,
	constraint User_email_uindex
		unique (email)
);

