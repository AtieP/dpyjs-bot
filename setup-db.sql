CREATE TABLE member_joins (
	join_id SERIAL,
	user_id BIGINT NOT NULL,
	join_date TIMESTAMPTZ NOT NULL
);

CREATE TABLE member_removes (
	leave_id SERIAL,
	user_id BIGINT NOT NULL,
	leave_date TIMESTAMPTZ NOT NULL
);

CREATE TABLE infractions (
	infraction_id SERIAL,
	moderator_id BIGINT NOT NULL,
	infractor_id BIGINT NOT NULL,
	action_type VARCHAR(8) NOT NULL,
	reason VARCHAR(512),
	hidden BOOL NOT NULL,
	inserted_at TIMESTAMPTZ NOT NULL,
	expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE user_bots (
	owner_id BIGINT NOT NULL,
	bot_id BIGINT NOT NULL,
	description VARCHAR(2000) NOT NULL,
	accepted BOOL NOT NULL,
	reviewed BOOL NOT NULL,
	user_bot_id SERIAL
);

commit;
