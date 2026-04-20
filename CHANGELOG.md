# Changelog


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0

### Added
- Initial release of the Fitbit custom component.
- Derived from the official Home Assistant core Fitbit integration.
- Included `log_body_measurements` unified action to easily log both weight and body fat percentage.
- Implemented smart automated profile fetching for demographics (age, height, gender) to calculate body fat percentage when only raw impedance and weight are provided.
- Restructured as a standalone HACS-compliant repository with full configuration support and required dependencies.
- Updated `fitbit-web-api` dependency to 2.15.0 for improved compatibility.
