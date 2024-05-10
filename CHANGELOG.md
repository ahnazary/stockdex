# Changelog

## 0.5.0

### Added

-- `data_source` in the `TickerFactory` class to specify the source of the data.
-- `WrongSecurityType` exception class to raise an exception when the security type is not valid.

### Fixed

- Bug with `isin` field in all classes.

### Changed

- Removed `nasdaq` module as the website keeps changing its structure.
- Instead of `Ticker` class, `TickerFactory` class is used to create `Ticker` objects.

## 0.4.0

### Added

- More methods for fetching data from `NASDAQ` website.
- More methods for fetching data from `JustETF` website.
- Separate module for yahoo finance web related functions.

### Fixed

- Bug with `security_type` field in all classes.

### Changed

- `Ticker` class now accepts `isin` and `security_type` as arguments.
