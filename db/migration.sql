CREATE DATABASE zoombot; 

CREATE TABLE public.users (
  id BIGSERIAL NOT NULL,
  redirect_hash character varying(1000),
  telegram_id bigint NOT NULL PRIMARY KEY,
  telegram_username character varying(1000)
);

CREATE TABLE public.meetings (
  id BIGSERIAL NOT NULL PRIMARY KEY,
  name character varying(1000) NOT NULL,
  link character varying(1000)  NOT NULL,
  user_telegram_id bigint NOT NULL,
  CONSTRAINT fk_user FOREIGN KEY(user_telegram_id) REFERENCES public.users(telegram_id)
  ON DELETE CASCADE
);

ALTER TABLE public.users ADD COLUMN zoom_access_token character varying(1000);