# beaconRx
RxUID System

## beaconRx_fingerprint.py

## PROTOTYPING / WORK IN PROGRESS (⚠️)

This software is a work in progress and currently in its prototyping phase. It is not intended for production use. Errors may occur, features may change, and documentation may be fragmented or incomplete. During the prototyping phase, all support inquiries about this software will be ignored.

### Overview

The `beaconRx_fingerprint.py` program generates a unique hardware fingerprint for the system it runs on. This fingerprint is based on various hardware components such as CPU, GPU, RAM, storage, motherboard, BIOS, and display information.

### Usage

To use the program, run it with the following command-line arguments:
```bash
python beaconRx_fingerprint.py --username <username> --passkey <passkey>
```
Replace `<username>` and `<passkey>` with your desired values.

### How it Works

1. The program collects detailed information about the system's hardware configuration.
2. It generates a compact hardware string by concatenating the hardware information without spaces.
3. The username and passkey provided as command-line arguments are added to the beginning of the hardware string.
4. The program applies two secure hashing stages to the salted hardware string:
   * SHA-256 hashing
   * PBKDF2 key stretching with 100,000 iterations using the username and passkey as salt
5. The program displays the collected hardware information, the compact hardware string, and the results of the hashing stages.

### Output

The program outputs the following:
* System hardware configuration information
* Compact hardware string (including username and passkey)
* SHA-256 hash of the salted hardware string
* PBKDF2 hash (with 100,000 iterations) of the SHA-256 hash

This hardware fingerprinting method provides a unique identifier for the system, making it suitable for various applications such as system identification or verification.

## COPYRIGHT, CONTEXT, LICENSE & LIMMITATIONS

Copyright 2025 - Robin Winkelmann | robinRx | rx-inference

This repository, its software and all other associated material is licensed under Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
See the [LICENSE](https://github.com/rx-inference/beaconRx/blob/main/LICENSE) in the root of this project for details.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.