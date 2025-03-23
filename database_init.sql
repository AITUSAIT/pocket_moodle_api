-- public."admin" определение

-- Drop table

-- DROP TABLE "admin";


CREATE TABLE "admin" (
  user_id int8 NOT NULL,
  "name" varchar(255) NULL,
  status varchar(50) NULL,
  CONSTRAINT admin_pkey PRIMARY KEY (user_id)
);


-- public.courses определение

-- Drop table

-- DROP TABLE courses;


CREATE TABLE courses (
  id serial4 NOT NULL,
  course_id int8 NULL,
  "name" varchar(255) NULL,
  teacher_name varchar(255) NULL,
  CONSTRAINT user_courses_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX unique_courses_id ON public.courses USING btree (course_id);


-- public.courses_contents определение

-- Drop table

-- DROP TABLE courses_contents;


CREATE TABLE courses_contents (
  id int8 NULL,
  "name" varchar NULL,
  "section" int4 NULL,
  course_id int8 NULL
);


-- public.courses_contents_modules определение

-- Drop table

-- DROP TABLE courses_contents_modules;


CREATE TABLE courses_contents_modules (
  id int8 NULL,
  url varchar NULL,
  "name" varchar NULL,
  modplural varchar NULL,
  modname varchar NULL,
  courses_contents_id int8 NULL
);


-- public.courses_contents_modules_files определение

-- Drop table

-- DROP TABLE courses_contents_modules_files;


CREATE TABLE courses_contents_modules_files (
  filename varchar NULL,
  filesize int8 NULL,
  fileurl varchar NULL,
  timecreated int8 NULL,
  timemodified int8 NULL,
  mimetype varchar NULL,
  bytes bytea NULL,
  courses_contents_modules_id int8 NULL,
  id serial4 NOT NULL
);


-- public.courses_contents_modules_urls определение

-- Drop table

-- DROP TABLE courses_contents_modules_urls;


CREATE TABLE courses_contents_modules_urls (
  "name" varchar NULL,
  url varchar NULL,
  courses_contents_modules_id int8 NULL,
  id serial4 NOT NULL
);


-- public.courses_user_pair определение

-- Drop table

-- DROP TABLE courses_user_pair;


CREATE TABLE courses_user_pair (
  user_id int8 NULL,
  course_id int8 NULL,
  active bool NULL,
  CONSTRAINT unique_user_course UNIQUE (user_id, course_id)
);


-- public.deadlines определение

-- Drop table

-- DROP TABLE deadlines;


CREATE TABLE deadlines (
  assign_id int4 NULL,
  id int4 NOT NULL,
  "name" varchar(255) NULL,
  course_id int4 NULL
);
CREATE UNIQUE INDEX unique_deadlines_id ON public.deadlines USING btree (id);


-- public.deadlines_user_pair определение

-- Drop table

-- DROP TABLE deadlines_user_pair;


CREATE TABLE deadlines_user_pair (
  user_id int8 NULL,
  id int8 NULL,
  submitted bool NULL,
  graded bool NULL,
  status jsonb NULL,
  due timestamp NULL
);


-- public.grades определение

-- Drop table

-- DROP TABLE grades;


CREATE TABLE grades (
  id serial4 NOT NULL,
  "name" varchar(255) NULL,
  percentage varchar(10) NULL,
  course_id int4 NULL,
  user_id int8 NULL,
  grade_id int8 NULL
);


-- public.moodle_news определение

-- Drop table

-- DROP TABLE moodle_news;

CREATE TABLE moodle_news (
  id serial4 NOT NULL,
  CONSTRAINT moodle_news_pkey PRIMARY KEY (id)
);


-- public.servers определение

-- Drop table

-- DROP TABLE servers;


CREATE TABLE servers (
  "token" varchar(255) NULL,
  "name" varchar(255) NULL,
  proxy_list jsonb NULL
);


-- public.user_notification определение

-- Drop table

-- DROP TABLE user_notification;


CREATE TABLE user_notification (
  user_id int8 NOT NULL,
  status bool NULL,
  is_newbie_requested bool NULL,
  is_update_requested bool NULL,
  is_end_date bool NULL,
  error_check_token bool NULL DEFAULT false,
  CONSTRAINT user_notification_pk PRIMARY KEY (user_id)
);


-- public.user_settings_app определение

-- Drop table

-- DROP TABLE user_settings_app;


CREATE TABLE user_settings_app (
  user_id int8 NOT NULL,
  status bool NULL,
  notification_grade bool NULL,
  notification_deadline bool NULL,
  CONSTRAINT user_settings_app_pk PRIMARY KEY (user_id)
);


-- public.user_settings_bot определение

-- Drop table

-- DROP TABLE user_settings_bot;


CREATE TABLE user_settings_bot (
  user_id int8 NOT NULL,
  status bool NULL,
  notification_grade bool NULL,
  notification_deadline bool NULL,
  CONSTRAINT user_settings_bot_pk PRIMARY KEY (user_id)
);


-- public.users определение

-- Drop table

-- DROP TABLE users;


CREATE TABLE users (
  user_id int8 NOT NULL,
  api_token varchar(255) NULL,
  register_date timestamp NULL,
  mail varchar NULL,
  last_active timestamp NULL,
  moodle_id int4 NULL,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);


-- public.users_groups определение

-- Drop table

-- DROP TABLE users_groups;


CREATE TABLE users_groups (
  id serial4 NOT NULL,
  group_tg_id int8 NULL,
  group_name varchar(255) NULL,
  CONSTRAINT users_groups_pkey PRIMARY KEY (id)
);


-- public.user_to_group определение

-- Drop table

-- DROP TABLE user_to_group;


CREATE TABLE user_to_group (
  user_id int8 NULL,
  group_id int8 NULL,
  CONSTRAINT user_to_group_group_id_fkey FOREIGN KEY (group_id) REFERENCES users_groups(id) ON DELETE CASCADE,
  CONSTRAINT user_to_group_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

