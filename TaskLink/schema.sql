DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS link;

CREATE TABLE user (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE task (
  task_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  completed INTEGER,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE link (
  link_id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_task_id INTEGER NOT NULL,
  finish_task_id INTEGER NOT NULL,
  FOREIGN KEY (start_task_id) REFERENCES task (task_id),
  FOREIGN KEY (finish_task_id) REFERENCES task (task_id)
);