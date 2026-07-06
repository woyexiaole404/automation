# Security TODO

This file records hardcoded sensitive configuration found in the current codebase.
Do not copy real secrets into this document.

## Current Findings

### Database

- `base/base.py`
  - Hardcoded MySQL host.
  - Hardcoded MySQL username.
  - Hardcoded MySQL password.
  - Hardcoded database name.

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
2. Move database settings from `base/base.py` to environment variables or `config/config.yaml`.
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
- `API_AUTHORIZATION`
- `API_CLIENTAUTHORIZATION`
- `API_AD_PREFERENCE`
