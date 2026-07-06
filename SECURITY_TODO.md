# Security TODO

This file records hardcoded sensitive configuration found in the current codebase.
Do not copy real secrets into this document.

## Current Findings

### Database

- `base/base.py`
  - Migrated MySQL host, port, username, password, database name, and charset to `config/config_loader.py`.
  - Values are now read from environment variables first, then `config/config.yaml`.
  - `config/config.yaml.example` contains placeholder values only.

### UI Test Accounts

- `test_case/test_shanghu.py`
  - Hardcoded merchant login username.
  - Hardcoded merchant login passwords for success and failure cases.
- `test_case/test_xinlian.py`
  - Hardcoded login username.
  - Hardcoded login password.
- `test_case/test_lhcz.py`
  - Hardcoded login username.
  - Hardcoded login password.
- `test_case/test_yichuang.py`
  - Hardcoded login username.
  - Hardcoded login password.

### API Tokens and Headers

- `test_case/test_api.py`
  - Hardcoded `Authorization` bearer token.
- `test_case/api.py`
  - Hardcoded ad preference header.
  - Hardcoded client authorization token.
- `test_case/test.py`
  - Commented historical API token and phone-number-related snippets.

### Local Environment Paths

- `test_case/config.json`
  - Hardcoded mini program project path.
  - Hardcoded WeChat DevTools CLI path.

## New Safe Configuration Files

- `config/config.yaml.example`
  - Placeholder-only example file.
  - Safe to commit.
- `config/config.yaml`
  - Local real configuration file.
  - Must not be committed.

## Recommended Migration Order

1. Keep existing tests unchanged while introducing config loading.
2. Database settings from `base/base.py` have been migrated to environment variables or `config/config.yaml`.
3. Move API tokens from API scripts to environment variables or `config/config.yaml`.
4. Move UI test accounts to environment variables or `config/config.yaml`.
5. Move mini program local paths from `test_case/config.json` to local-only config.

## Environment Variable Priority

`config/config_loader.py` supports reading environment variables first, then
falling back to `config/config.yaml`.

Examples:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_CHARSET`
- `SHANGHU_USERNAME`
- `SHANGHU_PASSWORD`
- `XINLIAN_USERNAME`
- `XINLIAN_PASSWORD`
- `LHCZ_USERNAME`
- `LHCZ_PASSWORD`
- `YICHUANG_USERNAME`
- `YICHUANG_PASSWORD`
- `API_AUTHORIZATION`
- `API_CLIENTAUTHORIZATION`
- `API_AD_PREFERENCE`
