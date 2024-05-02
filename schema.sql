--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1 (Debian 16.1-1.pgdg120+1)
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Issue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Issue" (
    id integer NOT NULL,
    repo_id integer NOT NULL,
    user_id integer NOT NULL,
    title text NOT NULL,
    content text NOT NULL
);


ALTER TABLE public."Issue" OWNER TO postgres;

--
-- Name: Issue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Issue_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Issue_id_seq" OWNER TO postgres;

--
-- Name: Issue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Issue_id_seq" OWNED BY public."Issue".id;


--
-- Name: PullRequest; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."PullRequest" (
    id integer NOT NULL,
    user_id integer NOT NULL,
    repo_id integer NOT NULL,
    title text NOT NULL,
    from_branch text NOT NULL,
    into_branch text NOT NULL,
    approved boolean DEFAULT false NOT NULL
);


ALTER TABLE public."PullRequest" OWNER TO postgres;

--
-- Name: PullRequest_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."PullRequest_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."PullRequest_id_seq" OWNER TO postgres;

--
-- Name: PullRequest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."PullRequest_id_seq" OWNED BY public."PullRequest".id;


--
-- Name: Repository; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Repository" (
    id integer NOT NULL,
    public boolean NOT NULL,
    user_id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public."Repository" OWNER TO postgres;

--
-- Name: Repository_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Repository_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Repository_id_seq" OWNER TO postgres;

--
-- Name: Repository_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Repository_id_seq" OWNED BY public."Repository".id;


--
-- Name: User; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."User" (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL
);


ALTER TABLE public."User" OWNER TO postgres;

--
-- Name: User_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."User_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."User_id_seq" OWNER TO postgres;

--
-- Name: User_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."User_id_seq" OWNED BY public."User".id;


--
-- Name: Issue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Issue" ALTER COLUMN id SET DEFAULT nextval('public."Issue_id_seq"'::regclass);


--
-- Name: PullRequest id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PullRequest" ALTER COLUMN id SET DEFAULT nextval('public."PullRequest_id_seq"'::regclass);


--
-- Name: Repository id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Repository" ALTER COLUMN id SET DEFAULT nextval('public."Repository_id_seq"'::regclass);


--
-- Name: User id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User" ALTER COLUMN id SET DEFAULT nextval('public."User_id_seq"'::regclass);


--
-- Name: Issue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Issue_id_seq"', 1, true);


--
-- Name: PullRequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."PullRequest_id_seq"', 1, true);


--
-- Name: Repository_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Repository_id_seq"', 1, true);


--
-- Name: User_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."User_id_seq"', 1, true);


--
-- Name: Issue Issue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Issue"
    ADD CONSTRAINT "Issue_pkey" PRIMARY KEY (id);


--
-- Name: PullRequest PullRequest_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PullRequest"
    ADD CONSTRAINT "PullRequest_pkey" PRIMARY KEY (id);


--
-- Name: Repository Repository_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Repository"
    ADD CONSTRAINT "Repository_pkey" PRIMARY KEY (id);


--
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- Name: Repository_user_id_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX "Repository_user_id_name_idx" ON public."Repository" USING btree (user_id, name);


--
-- Name: branches; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX branches ON public."PullRequest" USING btree (repo_id, from_branch, into_branch);


--
-- Name: username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX username ON public."User" USING btree (username);


--
-- Name: Issue issue_repo_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Issue"
    ADD CONSTRAINT issue_repo_fk FOREIGN KEY (repo_id) REFERENCES public."Repository"(id);


--
-- Name: Issue issue_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Issue"
    ADD CONSTRAINT issue_user_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- Name: PullRequest pullrequest_repo_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PullRequest"
    ADD CONSTRAINT pullrequest_repo_fk FOREIGN KEY (repo_id) REFERENCES public."Repository"(id);


--
-- Name: PullRequest pullrequest_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."PullRequest"
    ADD CONSTRAINT pullrequest_user_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- Name: Repository repo_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Repository"
    ADD CONSTRAINT repo_name_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- PostgreSQL database dump complete
--

