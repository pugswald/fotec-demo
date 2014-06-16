pragma foreign_keys=on;

drop table if exists transactions;
drop table if exists cards;
drop table if exists users;
create table users (
    id integer primary key autoincrement,
    name text not null,
    device text not null UNIQUE,
    passhash text not null
);
create table cards (
    id integer primary key autoincrement,
    user_id integer references users(id),
    name text not null,
    bank text not null,
    network text not null,
    last_four text not null
);
create table transactions (
    id integer primary key autoincrement,
    card_id integer references cards(id),
    merchant text not null,
    amount real not null,
    approval text not null,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

