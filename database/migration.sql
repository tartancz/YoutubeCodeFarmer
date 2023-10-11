CREATE TABLE "token"
(
    "id"            integer PRIMARY KEY,
    "refresh_token" varchar                             NOT NULL,
    "token"         varchar                             NOT NULL,
    "expires_in"    integer                             NOT NULL,
    "created"       timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE "yt_channel"
(
    "channel_id"  nvarchar PRIMARY KEY,
    "video_count" integer NULL
);

CREATE TABLE "video"
(
    "video_id"         nvarchar PRIMARY KEY,
    "yt_channel_id"    nvarchar REFERENCES yt_channel (channel_id) NOT NULL,
    "publish_time"     datetime                                    NOT NULL,
    "skipped_finding"  bool                                        NOT NULL,
    "contain_discount" bool                                        NULL
);

CREATE TABLE "discount"
(
    "id"                  integer PRIMARY KEY,
    "video_id"            integer REFERENCES video (video_id) NOT NULL,
    "code"                nvarchar                            NOT NULL,
    "frame"               int                                 NOT NULL,
    "was_right"           bool                                NOT NULL,
    "activated_by_me"     bool                                NOT NULL,
    "how_long_to_process" NUMERIC(8, 2)                       NOT NULL
);