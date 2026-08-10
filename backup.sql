--
-- PostgreSQL database dump
--

\restrict cNe8ZI3W62TYGCNIvaturGUo0fihMsfRwFBYf3cCRBi8oZCwduB7DDGpFj4Mimw

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: completion_levels; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.completion_levels AS ENUM (
    'Not Started',
    'In Progress',
    'Completed',
    'Needs Further Work'
);


--
-- Name: priority_levels; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.priority_levels AS ENUM (
    'Low',
    'Medium',
    'High'
);


--
-- Name: subtask_completion_levels; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.subtask_completion_levels AS ENUM (
    'Not Started',
    'In Progress',
    'Completed',
    'Needs Further Work'
);


--
-- Name: subtask_priority_levels; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.subtask_priority_levels AS ENUM (
    'Low',
    'Medium',
    'High'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: subtask; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subtask (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    description character varying(200),
    due_date date,
    completion_level public.subtask_completion_levels,
    set_priority public.subtask_priority_levels NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    user_id integer,
    duration integer,
    duration_seconds integer,
    task_id integer NOT NULL,
    tokens integer DEFAULT 1 NOT NULL
);


--
-- Name: subtask_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subtask_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subtask_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subtask_id_seq OWNED BY public.subtask.id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    description character varying(200),
    due_date date,
    completion_level public.completion_levels,
    set_priority public.priority_levels NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    user_id integer,
    tokens integer DEFAULT 1 NOT NULL
);


--
-- Name: task_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_id_seq OWNED BY public.task.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(200) NOT NULL,
    sprint_tokens_limit integer DEFAULT 40 NOT NULL,
    token_duration integer DEFAULT 10 NOT NULL
);


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: subtask id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subtask ALTER COLUMN id SET DEFAULT nextval('public.subtask_id_seq'::regclass);


--
-- Name: task id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task ALTER COLUMN id SET DEFAULT nextval('public.task_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: subtask; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subtask (id, title, description, due_date, completion_level, set_priority, start_time, end_time, user_id, duration, duration_seconds, task_id, tokens) FROM stdin;
\.


--
-- Data for Name: task; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task (id, title, description, due_date, completion_level, set_priority, start_time, end_time, user_id, tokens) FROM stdin;
1	rats	rats	2026-07-24	In Progress	Medium	02:07:00	\N	\N	1
2	sugar	sugar	2026-07-24	In Progress	Medium	02:40:00	\N	\N	1
4	cameron1	cameron1	2027-05-09	In Progress	Medium	09:20:00	\N	2	1
9	killer queen	awek m[pw	\N	In Progress	Low	\N	\N	1	1
3	admin 99	dsfdfsfd	\N	Not Started	High	\N	\N	1	1
8	kind statements	kind statements 62	2026-08-09	In Progress	High	17:00:00	17:10:00	1	1
5	admin task 2	sfsfnl	2026-08-06	In Progress	Low	10:00:00	10:10:00	1	1
6	slid 55	suicide 3	2026-08-07	Not Started	High	13:00:00	13:10:00	1	1
7	admin 4	admin 4	2026-08-06	In Progress	High	16:00:00	16:10:00	1	1
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, username, password_hash, sprint_tokens_limit, token_duration) FROM stdin;
1	admin	scrypt:32768:8:1$hZ8bv3dTXXZGhbVq$623dae1f26bf4e945d1058202b5fc8ec7407690ea37f356c5cce30a68801941db495fd70ed8d62aeb77b0166afa6ff4a95947350f878ba4a24e9f851c5f3d4e2	40	10
2	cameron	scrypt:32768:8:1$zUEl4BBJj1jU5PsC$4a30ee43fe9dd6340bde889c8c3d45e25cbcd4330a30021940d0af3342975327d0b1ce03d1ddeb668df6626c488ec94c8c1cfb041a7aec42ae891b634200d04a	40	10
3	user	scrypt:32768:8:1$2mCILnn5sLhDidYd$29c328403c62ff964c2bc4bfc62c516d60e44ee1081cb025fd0035a73a4001ef24544d6b935d708ceb23db4f98f67ff3d708202156ca17ae6c9b79838d1fe4db	40	10
4	adam	scrypt:32768:8:1$ewPkusWRqtMiLtur$59ddf892c0bfb64322e35c564c250f9890cb009ec809e1043469dca4e63615cd37bf0ce55f2d9c5abe09b08a56d174463a9e196b7744b627f660f63e3c33631e	40	10
\.


--
-- Name: subtask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.subtask_id_seq', 1, false);


--
-- Name: task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_id_seq', 9, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_id_seq', 4, true);


--
-- Name: subtask subtask_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subtask
    ADD CONSTRAINT subtask_pkey PRIMARY KEY (id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: subtask subtask_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subtask
    ADD CONSTRAINT subtask_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.task(id);


--
-- Name: subtask subtask_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subtask
    ADD CONSTRAINT subtask_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: task task_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- PostgreSQL database dump complete
--

\unrestrict cNe8ZI3W62TYGCNIvaturGUo0fihMsfRwFBYf3cCRBi8oZCwduB7DDGpFj4Mimw

