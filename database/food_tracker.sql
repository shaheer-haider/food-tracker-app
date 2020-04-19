
create table food (
id integer primary key autoincrement,
name text not null unique,
protein integer not null,
carbohydrates integer not null,
fat integer not null,
calories integer not null
);

--create table date (
--dates text unique
--);

--create table date_wise_food (
--    food_id text  not null,
--    food_date text not null
--);