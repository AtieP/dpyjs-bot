CREATE TABLE infractions(
    id SERIAL PRIMARY KEY,
    moderator_id BIGINT NOT NULL,
    bad_actor_id BIGINT NOT NULL,
    action VARCHAR(8) NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    reason VARCHAR(512)
)
