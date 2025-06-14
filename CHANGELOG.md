# beaconRx - CHANGELOG

notable changes will be documented.

this project adheres to [semantic versioning](https://semver.org/spec/v2.0.0.html).

## 2025-06-14

## v0.0.5

- add: added debug argument to show compact hardware string, for inspection purpose. ;;;
- doc: minor error corrections in 'README.md'. ;;;

## v0.0.4

- sec: added input sanitization of username and passkey. only 0-9, a-z, A-Z allowed. ;;;
- sec: added extensive error handling. ;;;
- mod: refactored process info message; better formatting and clarity. ;;;
- mod: added possibility to call help with '-h' argument and refined cli help message for better clarity. ;;;
- mod: removed trivial sha256 pre hashing function. ;;;
- doc: added default header to 'CHANGELOG.md'. ;;;
- doc: minor correction work on changelog formatting. ;;;
- doc: minor changes to 'README.md' licensing section heading, for better clarification. ;;;
- doc: added/fixed missing copyright info in 'LICENSE'. ;;;

## 2025-06-13

- doc: fixed missing 'initial commit' entry at the beginning of this changelog. ;;;
- doc: fixed errors in the 'COPYRIGHT CONTEXT & LICENSE' part of the 'README.md'. ;;;

## v0.0.1

- add: added username and passkey entry via cli arguments using argparse. ;;;
- add: 'requirements.txt'. ;;;
- add: added first draft of fingerprinting script; 'beaconRx_fingerprint.py'. implemented basic hardware component reading, string concatenation, sha-256 hashing + pbkdf2 hashing; fingerprinting is now working. ;;;
- add: added '.gitignore' file. ;;;
- add: established basic project boilerplate ;;;
- add: apache 2.0 license; file: 'LICENSE' ;;;
- add: 'README.md' ;;;
- add: initial commit. ;;;