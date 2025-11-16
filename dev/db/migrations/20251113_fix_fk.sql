-- DROP
ALTER TABLE [token_sets] DROP CONSTRAINT token_sets_ibfk_1;
ALTER TABLE [token_sets] DROP CONSTRAINT token_sets_ibfk_2;
ALTER TABLE [token_sets] DROP CONSTRAINT token_sets_ibfk_3;
ALTER TABLE [token_sets] DROP CONSTRAINT token_sets_ibfk_4;
ALTER TABLE [auths] DROP CONSTRAINT auths_ibfk_1;
ALTER TABLE [auths] DROP CONSTRAINT auths_ibfk_2;
ALTER TABLE [sessions] DROP CONSTRAINT sessions_ibfk_1;
ALTER TABLE [redirect_uris] DROP CONSTRAINT redirect_uris_ibfk_1;
ALTER TABLE [oidc_authorizations] DROP CONSTRAINT oidc_authorizations_ibfk_1;
ALTER TABLE [oidc_authorizations] DROP CONSTRAINT oidc_authorizations_ibfk_2;
ALTER TABLE [oidc_authorizations] DROP CONSTRAINT oidc_authorizations_ibfk_3;
ALTER TABLE [discords] DROP CONSTRAINT discords_ibfk_1;
ALTER TABLE [user_role] DROP CONSTRAINT user_role_ibfk_1;
ALTER TABLE [user_role] DROP CONSTRAINT user_role_ibfk_2;
ALTER TABLE [user_app] DROP CONSTRAINT user_app_ibfk_1;
ALTER TABLE [user_app] DROP CONSTRAINT user_app_ibfk_2;
-- ADD
ALTER TABLE [token_sets]
ADD CONSTRAINT token_sets_ibfk_1 FOREIGN KEY ([access_token_id]) REFERENCES [access_tokens]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [token_sets]
ADD CONSTRAINT token_sets_ibfk_2 FOREIGN KEY ([refresh_token_id]) REFERENCES [refresh_tokens]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [token_sets]
ADD CONSTRAINT token_sets_ibfk_3 FOREIGN KEY ([id_token_id]) REFERENCES [id_tokens]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [auths]
ADD CONSTRAINT auths_ibfk_1 FOREIGN KEY ([auth_user_id]) REFERENCES [users]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [sessions]
ADD CONSTRAINT sessions_ibfk_1 FOREIGN KEY ([user_id]) REFERENCES [users]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [redirect_uris]
ADD CONSTRAINT redirect_uris_ibfk_1 FOREIGN KEY ([app_id]) REFERENCES [apps]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [auths]
ADD CONSTRAINT auths_ibfk_2 FOREIGN KEY ([app_id]) REFERENCES [apps]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [oidc_authorizations]
ADD CONSTRAINT oidc_authorizations_ibfk_1 FOREIGN KEY ([auth_id]) REFERENCES [auths]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [oidc_authorizations]
ADD CONSTRAINT oidc_authorizations_ibfk_2 FOREIGN KEY ([consent_id]) REFERENCES [consents]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [oidc_authorizations]
ADD CONSTRAINT oidc_authorizations_ibfk_3 FOREIGN KEY ([code_id]) REFERENCES [code]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [token_sets]
ADD CONSTRAINT token_sets_ibfk_4 FOREIGN KEY ([oidc_authorization_id]) REFERENCES [oidc_authorizations]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [discords]
ADD CONSTRAINT discords_ibfk_1 FOREIGN KEY ([user_id]) REFERENCES [users]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [user_role]
ADD CONSTRAINT user_role_ibfk_1 FOREIGN KEY ([user_id]) REFERENCES [users]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [user_role]
ADD CONSTRAINT user_role_ibfk_2 FOREIGN KEY ([role_id]) REFERENCES [roles]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [user_app]
ADD CONSTRAINT user_app_ibfk_1 FOREIGN KEY ([app_id]) REFERENCES [apps]([id]) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE [user_app]
ADD CONSTRAINT user_app_ibfk_2 FOREIGN KEY ([user_id]) REFERENCES [users]([id]) ON DELETE CASCADE ON UPDATE CASCADE;