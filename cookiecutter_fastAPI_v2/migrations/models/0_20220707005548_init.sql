-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "role" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL,
    "description" TEXT,
    "is_admin" BOOL NOT NULL  DEFAULT False,
    "permission" JSONB NOT NULL
);
COMMENT ON COLUMN "role"."created_at" IS '创建时间';
COMMENT ON COLUMN "role"."updated_at" IS '更新时间';
COMMENT ON COLUMN "role"."id" IS 'id';
COMMENT ON COLUMN "role"."name" IS '角色名';
COMMENT ON COLUMN "role"."description" IS '角色详情';
COMMENT ON COLUMN "role"."is_admin" IS '是否管理员';
COMMENT ON COLUMN "role"."permission" IS '权限';
COMMENT ON TABLE "role" IS 'Role ';
CREATE TABLE IF NOT EXISTS "user" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(64) NOT NULL UNIQUE,
    "password" VARCHAR(128)
);
COMMENT ON COLUMN "user"."created_at" IS '创建时间';
COMMENT ON COLUMN "user"."updated_at" IS '更新时间';
COMMENT ON COLUMN "user"."id" IS 'id';
COMMENT ON COLUMN "user"."username" IS '用户名';
COMMENT ON COLUMN "user"."password" IS '密码hash';
COMMENT ON TABLE "user" IS 'User';
CREATE TABLE IF NOT EXISTS "token" (
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL  PRIMARY KEY,
    "source" VARCHAR(32) NOT NULL,
    "expire_at" TIMESTAMPTZ,
    "is_delete" BOOL NOT NULL  DEFAULT False,
    "permission" JSONB NOT NULL,
    "created_by_id" INT REFERENCES "user" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "token"."created_at" IS '创建时间';
COMMENT ON COLUMN "token"."updated_at" IS '更新时间';
COMMENT ON COLUMN "token"."id" IS 'uuid';
COMMENT ON COLUMN "token"."source" IS 'token来源';
COMMENT ON COLUMN "token"."expire_at" IS '过期时间';
COMMENT ON COLUMN "token"."is_delete" IS '是否失效';
COMMENT ON COLUMN "token"."permission" IS '权限';
COMMENT ON COLUMN "token"."created_by_id" IS '创建人';
COMMENT ON COLUMN "token"."user_id" IS '用户';
CREATE TABLE IF NOT EXISTS "user_role" (
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "user_role" IS '权限';
