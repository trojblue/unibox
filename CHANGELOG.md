# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [0.8.1](https://github.com/trojblue/unibox/releases/tag/0.8.1) - 2025-02-22

<small>[Compare with 0.8.0](https://github.com/trojblue/unibox/compare/0.8.0...0.8.1)</small>

## [0.8.0](https://github.com/trojblue/unibox/releases/tag/0.8.0) - 2025-02-22

<small>[Compare with 0.7.0](https://github.com/trojblue/unibox/compare/0.7.0...0.8.0)</small>

### Features

- adding dataset-card generation tool ([a410353](https://github.com/trojblue/unibox/commit/a41035348046e828477676c59e16cb5647bcf82e) by yada).

### Bug Fixes

- modifying file protect config ([b26b632](https://github.com/trojblue/unibox/commit/b26b6326f2861365cdd98b96ca8469cf9b12176a) by yada).
- local or s3 backends: prevent overwriting important system files ([39867dc](https://github.com/trojblue/unibox/commit/39867dc762a750f884679e742c96a0f2191808d6) by yada).
- s3 backend: variable unbound when specifying path ([7e97559](https://github.com/trojblue/unibox/commit/7e975597c1771c9e257fa125b27acf2498735271) by yada).
- ub.ls(): working on both huggingface model repo and datasets ([70b070e](https://github.com/trojblue/unibox/commit/70b070e73028d8e38bde4429e7fd94a7a74123ad) by yada).
- huggingface dataset: using proper saves() to work (and update) huggingface repo ([7d382af](https://github.com/trojblue/unibox/commit/7d382afa95592f237665c4806d6c51b47422bed6) by yada).
- huggingface dataset: shortcircuit to download directly instead of double save ([c0ef5e0](https://github.com/trojblue/unibox/commit/c0ef5e0b866504c78f05f4be92ae7dcf76644b37) by yada).
- broken s3 loading | broken: huggingface loading after backend downloads ([36aaae2](https://github.com/trojblue/unibox/commit/36aaae27f473dd8b37a93ef9681e4ac7707a1336) by yada).
- hf backends loading | broken: s3 loading ([fbf3240](https://github.com/trojblue/unibox/commit/fbf3240dbcae892bfa5d58ff4138f7b731e8f5ab) by yada).
- use correct testing script ([1984a08](https://github.com/trojblue/unibox/commit/1984a088099e3d3782b0010636a1839d57197486) by yada).
- missing credentials / dependencies for  test cases ([672330a](https://github.com/trojblue/unibox/commit/672330a0c5d6c5b9f0eb684153524de3223bb42b) by yada).

### Code Refactoring

- allow loading from huggingface datasets as a file ([aa3dc50](https://github.com/trojblue/unibox/commit/aa3dc50f369a1eb68d6c36b9341c0a49d824bfe8) by yada).
- let loader handle huggingface loads ([400f7e1](https://github.com/trojblue/unibox/commit/400f7e1059fb5a43f1b29d031bef2a89e9acaa16) by yada).

## [0.7.0](https://github.com/trojblue/unibox/releases/tag/0.7.0) - 2025-02-20

<small>[Compare with 0.6.0](https://github.com/trojblue/unibox/compare/0.6.0...0.7.0)</small>

### Features

- adding dataset split control when using ub.saves("hf://org/dataset_repo") ([20735f9](https://github.com/trojblue/unibox/commit/20735f9c04336544664bd6961b827bca70c15a9f) by yada).
- adding toml / yaml loaders ([3955e49](https://github.com/trojblue/unibox/commit/3955e49ef5cbe09ad6207872ddde58f4a711384d) by yada).

### Bug Fixes

- missing type checks after update ([f001f15](https://github.com/trojblue/unibox/commit/f001f159086d627d50c02be64a01c312650eb9a0) by yada).
- s3 backend: missing arguments for ls ([7c1d8e5](https://github.com/trojblue/unibox/commit/7c1d8e59bd90c768698525d0ab52bcb34c5a3f1f) by yada).
- incorrect huggingface data upload behavior when using datasets ([bc5d773](https://github.com/trojblue/unibox/commit/bc5d77399fefca518e971e9f0da590e7875757ee) by yada).

## [0.6.0](https://github.com/trojblue/unibox/releases/tag/0.6.0) - 2025-02-13

<small>[Compare with 0.5.2](https://github.com/trojblue/unibox/compare/0.5.2...0.6.0)</small>

### Features

- adding improved huggingface dataset (with hfapi / hf datasets mixed backend) ([96486d2](https://github.com/trojblue/unibox/commit/96486d243c4a5e2aba2a6060e7b758a39c949e94) by yada).

## [0.5.2](https://github.com/trojblue/unibox/releases/tag/0.5.2) - 2025-02-05

### Features
- Add LLM API utility ([b0bc83d](https://github.com/trojblue/unibox/commit/b0bc83d8ddab4e73e976fc357e811d2e1c4d6fed) by openhands-agent)

### Bug Fixes
- HuggingFace URI loading incorrectly ([ef8c9757f95](https://github.com/trojblue/unibox/commit/ef8c9757f95b00b9a9243cb114d5f4ff008e636a) by openhands-agent)
- gallery() to handle None values and display images properly ([6f2cb39](https://github.com/trojblue/unibox/commit/6f2cb399b7f40de346f1e694810447469e1269ff) by openhands-agent)


<small>[Compare with 0.5.1](https://github.com/trojblue/unibox/compare/0.5.1...0.5.2)</small>

## [0.5.1](https://github.com/trojblue/unibox/releases/tag/0.5.1) - 2025-01-28

<small>[Compare with 0.5.0](https://github.com/trojblue/unibox/compare/0.5.0...0.5.1)</small>

## [0.5.0](https://github.com/trojblue/unibox/releases/tag/0.5.0) - 2025-01-04

<small>[Compare with v0.4.13](https://github.com/trojblue/unibox/compare/v0.4.13...0.5.0)</small>

### Features

- adding back ub.peeks() support ([ac76e3a](https://github.com/trojblue/unibox/commit/ac76e3ae5d5a234fa3665cfec98a5dfce7688b98) by yada).
- adding proper colorized logger ([9e0d758](https://github.com/trojblue/unibox/commit/9e0d7584c9b23b46f5d8ec35b1fcf87e5c5c8807) by yada).
- adding basic huggingface upload tools ([f412a18](https://github.com/trojblue/unibox/commit/f412a184cfd2bb36969dd79d6b24395a1b49f353) by yada).
- adding huggingface storage backend ([4c93076](https://github.com/trojblue/unibox/commit/4c930763e962984a292dd8be39b285c60a1e8bd3) by yada).
- adding basic test suite and txt loader ([bc16177](https://github.com/trojblue/unibox/commit/bc16177939e6462df38c8b59c6ff671ed88c31b0) by yada).
- adding basic working loader and tests ([aa65789](https://github.com/trojblue/unibox/commit/aa657895d3b48272228dfcb884834f372370c982) by yada).
- adding skeleton loader classes ([a1e299f](https://github.com/trojblue/unibox/commit/a1e299f2b1b2635451f94d581d984d85373665e1) by yada).

### Bug Fixes

- adding colorama dep ([1a9dbe4](https://github.com/trojblue/unibox/commit/1a9dbe45a0dd8183ec20dc47aaaf8bd561ef4720) by trojblue).
- missing init in code ([2799f19](https://github.com/trojblue/unibox/commit/2799f190f04ccabc8039085fb6efd1bed1dd5886) by yada).
- huggingface uploading an datasets object; s3 incorrect uri passed in ([e5bb8d2](https://github.com/trojblue/unibox/commit/e5bb8d2ea3673954f6e717fd1003197118e915b5) by yada).
- adding colorlog dependency ([a746230](https://github.com/trojblue/unibox/commit/a7462307a4307ef942f4539f4024b88012efafc1) by yada).
- adding datasets dependency ([071e5cc](https://github.com/trojblue/unibox/commit/071e5ccf86027a85a03f29650b338e707b4de73b) by yada).
- color control characters getting written to logs ([ecf1781](https://github.com/trojblue/unibox/commit/ecf1781d07305c86fb5685cd641d502c3f96f433) by yada).
- image_loader: properly handling image loaders ([cf5e535](https://github.com/trojblue/unibox/commit/cf5e535a431ad7f3f1fed49e431fef3312fd23fb) by yada).
- double write penalty at ub.saves() ([ec07b9b](https://github.com/trojblue/unibox/commit/ec07b9b188aeb1de946885824db8071e85e8e6c8) by yada).
- adding convert to rgb when using gallery ([0e5826d](https://github.com/trojblue/unibox/commit/0e5826d247120f26f06a8d54c337d4ee3b5ebcc7) by yada).

### Code Refactoring

- remoivng old files ([5e59240](https://github.com/trojblue/unibox/commit/5e592405d7c5cfbff9558f1b1ea6a5b1b4f0ab4a) by yada).
- adding project template ([fd95d45](https://github.com/trojblue/unibox/commit/fd95d45f19091c2b06d77e92bbf71add53ce75bb) by yada).

## [v0.4.13](https://github.com/trojblue/unibox/releases/tag/v0.4.13) - 2024-11-17

<small>[Compare with v0.4.12](https://github.com/trojblue/unibox/compare/v0.4.12...v0.4.13)</small>

### Features

- adding ub.label_gallery() tool for data labelling ([0fdac23](https://github.com/trojblue/unibox/commit/0fdac23b882a2c3c616d68291b4f66c9c92ffda3) by yada).

## [v0.4.12](https://github.com/trojblue/unibox/releases/tag/v0.4.12) - 2024-09-30

<small>[Compare with v0.4.11](https://github.com/trojblue/unibox/compare/v0.4.11...v0.4.12)</small>

### Features

- allowing human-readable date in presigns() expiration ([1381b9a](https://github.com/trojblue/unibox/commit/1381b9aa810d342b5a53fe8df86a537baf44bc6d) by yada).

## [v0.4.11](https://github.com/trojblue/unibox/releases/tag/v0.4.11) - 2024-09-30

<small>[Compare with v0.4.10](https://github.com/trojblue/unibox/compare/v0.4.10...v0.4.11)</small>

### Features

- s3_client: adding generate_presigned_uri function; removing unused code ([ccfcbc8](https://github.com/trojblue/unibox/commit/ccfcbc8e3087c2adde77c59e26b7553ca63a05b8) by yada).

## [v0.4.10](https://github.com/trojblue/unibox/releases/tag/v0.4.10) - 2024-07-22

<small>[Compare with v0.4.9](https://github.com/trojblue/unibox/compare/v0.4.9...v0.4.10)</small>

### Bug Fixes

- further ipython import fix ([faac26f](https://github.com/trojblue/unibox/commit/faac26fe0341a3a5d838a01f88378d0edaf683e5) by yada).

## [v0.4.9](https://github.com/trojblue/unibox/releases/tag/v0.4.9) - 2024-07-22

<small>[Compare with v0.4.8](https://github.com/trojblue/unibox/compare/v0.4.8...v0.4.9)</small>

### Bug Fixes

- missing ipython dependency when calling ub.peeks() ([989b471](https://github.com/trojblue/unibox/commit/989b47141d5e1cd1d9a40900c79e2b18599da89a) by yada).

## [v0.4.8](https://github.com/trojblue/unibox/releases/tag/v0.4.8) - 2024-07-18

<small>[Compare with v0.4.7](https://github.com/trojblue/unibox/compare/v0.4.7...v0.4.8)</small>

### Bug Fixes

- concurrent_loads: fixing load order ([74ac31f](https://github.com/trojblue/unibox/commit/74ac31f0b06c273a4ff8487ad596f408470bccf6) by yada).

## [v0.4.7](https://github.com/trojblue/unibox/releases/tag/v0.4.7) - 2024-07-18

<small>[Compare with v0.4.6](https://github.com/trojblue/unibox/compare/v0.4.6...v0.4.7)</small>

### Features

- ub.gallery(): adding notebook gallery ([4f577a3](https://github.com/trojblue/unibox/commit/4f577a36f391ce22229da255dd2d3002024359d3) by yada).
- adding ub.ls() wrapper for shorter ub.traverses() ([e991c05](https://github.com/trojblue/unibox/commit/e991c0572846c1877dd6276b82f4ca69762512ee) by yada).
- uni_peeker: adding peek_df functionality ([ed78393](https://github.com/trojblue/unibox/commit/ed7839335227a196a83e176f0e6cbbcbeb282e37) by yada).
- adding concurrent_loads() function ([c3201d3](https://github.com/trojblue/unibox/commit/c3201d3a72baba49b3ef0f27548bd8664a734a4d) by yada).

### Bug Fixes

- ub.loads: tempfile naming error on windows ([1d454d5](https://github.com/trojblue/unibox/commit/1d454d5a0eda5bfad161019055d9e2fff1bb0573) by yada).

## [v0.4.6](https://github.com/trojblue/unibox/releases/tag/v0.4.6) - 2024-06-28

<small>[Compare with v0.4.5](https://github.com/trojblue/unibox/compare/v0.4.5...v0.4.6)</small>

### Bug Fixes

- UniSaver: replace NaN with null if saving to dict or jsonl ([5babfb8](https://github.com/trojblue/unibox/commit/5babfb81174f189869ae3c24d34d5a3e0bf5c2b4) by yada).

## [v0.4.5](https://github.com/trojblue/unibox/releases/tag/v0.4.5) - 2024-06-28

<small>[Compare with v0.4.4](https://github.com/trojblue/unibox/compare/v0.4.4...v0.4.5)</small>

### Bug Fixes

- adding graceful handling for errors when a line is unbale to be read ([0965249](https://github.com/trojblue/unibox/commit/09652499a6a0cf2f84dc4f98b4a8e23695180c41) by yada).

## [v0.4.4](https://github.com/trojblue/unibox/releases/tag/v0.4.4) - 2024-06-14

<small>[Compare with v0.4.3](https://github.com/trojblue/unibox/compare/v0.4.3...v0.4.4)</small>

### Bug Fixes

- ub.saves(); a bug where ub.saves(list[str]) won't correctly save ([3849e63](https://github.com/trojblue/unibox/commit/3849e63f7493309899a5dd178e94066cc5d19358) by yada).

## [v0.4.3](https://github.com/trojblue/unibox/releases/tag/v0.4.3) - 2024-06-13

<small>[Compare with v0.4.2](https://github.com/trojblue/unibox/compare/v0.4.2...v0.4.3)</small>

### Features

- add ability to save various formatted image files as png file ([8142695](https://github.com/trojblue/unibox/commit/8142695ef26433daed162780e5acc24c885d53fc) by yada).

### Bug Fixes

- resolved bug that prevents loading files from url ([c9cb709](https://github.com/trojblue/unibox/commit/c9cb7098479b0f854561bf2c6178ff16ab89cef6) by yada).

## [v0.4.2](https://github.com/trojblue/unibox/releases/tag/v0.4.2) - 2024-05-30

<small>[Compare with v0.4.1](https://github.com/trojblue/unibox/compare/v0.4.1...v0.4.2)</small>

### Features

- extend include_extensions at ub.traverses() to take more than extensions ([593b69c](https://github.com/trojblue/unibox/commit/593b69c2027181fc683a80b0c396b2dc0e53b7cd) by yada).

## [v0.4.1](https://github.com/trojblue/unibox/releases/tag/v0.4.1) - 2024-05-18

<small>[Compare with v0.4.0](https://github.com/trojblue/unibox/compare/v0.4.0...v0.4.1)</small>

### Bug Fixes

- ub.traverses(): traversing a s3 directory will not return the dir itself ([f0d85db](https://github.com/trojblue/unibox/commit/f0d85db8483ed17340d88d4bce17c94f9642734d) by yada).

## [v0.4.0](https://github.com/trojblue/unibox/releases/tag/v0.4.0) - 2024-05-08

<small>[Compare with v0.3.20](https://github.com/trojblue/unibox/compare/v0.3.20...v0.4.0)</small>

### Bug Fixes

- resizer hangs when handling large number of images to be resized ([9627894](https://github.com/trojblue/unibox/commit/96278949d0cb92084a2ee422c655fb5976fb3f27) by yada).

## [v0.3.20](https://github.com/trojblue/unibox/releases/tag/v0.3.20) - 2024-03-13

<small>[Compare with v0.3.19](https://github.com/trojblue/unibox/compare/v0.3.19...v0.3.20)</small>

### Features

- adding load feather support on uniloader ([fee98ff](https://github.com/trojblue/unibox/commit/fee98ff031e65a1caf0481ed40e1d11ae72e7112) by yada).

## [v0.3.19](https://github.com/trojblue/unibox/releases/tag/v0.3.19) - 2024-03-09

<small>[Compare with v0.3.18](https://github.com/trojblue/unibox/compare/v0.3.18...v0.3.19)</small>

### Bug Fixes

- incorrect behavior signature on ub.loads() on s3 uri ([ca00b40](https://github.com/trojblue/unibox/commit/ca00b4021dbeccf4c1fa3d04f3e2888d60c34647) by yada).

## [v0.3.18](https://github.com/trojblue/unibox/releases/tag/v0.3.18) - 2024-03-06

<small>[Compare with v0.3.17](https://github.com/trojblue/unibox/compare/v0.3.17...v0.3.18)</small>

## [v0.3.17](https://github.com/trojblue/unibox/releases/tag/v0.3.17) - 2024-03-06

<small>[Compare with v0.3.16](https://github.com/trojblue/unibox/compare/v0.3.16...v0.3.17)</small>

### Bug Fixes

- unclosed image at uniresizer ([b554630](https://github.com/trojblue/unibox/commit/b55463069f757aa63e62c2556116c2497a9c5e59) by yada).

## [v0.3.16](https://github.com/trojblue/unibox/releases/tag/v0.3.16) - 2024-03-05

<small>[Compare with v0.3.15](https://github.com/trojblue/unibox/compare/v0.3.15...v0.3.16)</small>

### Bug Fixes

- adding back max_workers in uni_resizer ([7c533f6](https://github.com/trojblue/unibox/commit/7c533f6760d4e4d7a6cd62d06a29ed4751de70da) by yada).

## [v0.3.15](https://github.com/trojblue/unibox/releases/tag/v0.3.15) - 2024-02-12

<small>[Compare with v0.3.14](https://github.com/trojblue/unibox/compare/v0.3.14...v0.3.15)</small>

### Features

- adding debug_print argument to unibox.traverses() ([66d1c02](https://github.com/trojblue/unibox/commit/66d1c0260ccf9d1f6bc3ad2abbc33fb1001ff52d) by yada).

## [v0.3.14](https://github.com/trojblue/unibox/releases/tag/v0.3.14) - 2023-12-18

<small>[Compare with v0.3.13](https://github.com/trojblue/unibox/compare/v0.3.13...v0.3.14)</small>

### Bug Fixes

- using unibox.loads() with s3 ([2ba1a57](https://github.com/trojblue/unibox/commit/2ba1a57e86e641f9dd64367315f61c032d1691ae) by yada).

## [v0.3.13](https://github.com/trojblue/unibox/releases/tag/v0.3.13) - 2023-12-14

<small>[Compare with v0.3.12](https://github.com/trojblue/unibox/compare/v0.3.12...v0.3.13)</small>

### Bug Fixes

- include ipykernel version to avoid tqdm issues ([a081b70](https://github.com/trojblue/unibox/commit/a081b70a4df1fd26eed97929248bb03a57a18b3c) by yada).
- traverses() with folder: incomplete s3 uri ([3b4d25b](https://github.com/trojblue/unibox/commit/3b4d25be0b10182035071db29fe47939e16bf29e) by yada).
- adding unit for traverse s3 ([c7d00d7](https://github.com/trojblue/unibox/commit/c7d00d7a345bf606a5642be00de1a0e7f6ef9e96) by yada).

## [v0.3.12](https://github.com/trojblue/unibox/releases/tag/v0.3.12) - 2023-12-12

<small>[Compare with v0.3.11](https://github.com/trojblue/unibox/compare/v0.3.11...v0.3.12)</small>

### Bug Fixes

- traverses(s3): allowing traverses() to return dir info ([0af5fdb](https://github.com/trojblue/unibox/commit/0af5fdbfcaf5c2bc461d36e0f2411f746357655b) by yada).

## [v0.3.11](https://github.com/trojblue/unibox/releases/tag/v0.3.11) - 2023-12-11

<small>[Compare with v0.3.10](https://github.com/trojblue/unibox/compare/v0.3.10...v0.3.11)</small>

### Features

- unibox.peeks(): adding list peek support & proper command use ([c346f99](https://github.com/trojblue/unibox/commit/c346f9984dea68928654dba036e968de728619ec) by yada).

## [v0.3.10](https://github.com/trojblue/unibox/releases/tag/v0.3.10) - 2023-12-11

<small>[Compare with v0.3.9](https://github.com/trojblue/unibox/compare/v0.3.9...v0.3.10)</small>

### Features

- adding support for s3 dir in unibox.traverses() ([b90a97a](https://github.com/trojblue/unibox/commit/b90a97ae80404a175e60c8e5756e14bab7727330) by yada).
- adding unipeeker and unibox.peeks() method for previewing data ([7b7a7cd](https://github.com/trojblue/unibox/commit/7b7a7cdffa0de719acd7ee58976055210b3f71b9) by yada).
- adding traverse() in s3 client ([3d786b3](https://github.com/trojblue/unibox/commit/3d786b3972866366b352d604250fde06f8e0bd25) by yada).

## [v0.3.9](https://github.com/trojblue/unibox/releases/tag/v0.3.9) - 2023-12-10

<small>[Compare with v0.3.8](https://github.com/trojblue/unibox/compare/v0.3.8...v0.3.9)</small>

### Bug Fixes

- unibox.loads(): add ability to properly load files from url ([32c5593](https://github.com/trojblue/unibox/commit/32c55931e6e8f9264b458a7ad8d37bac39e96cf5) by yada).

## [v0.3.8](https://github.com/trojblue/unibox/releases/tag/v0.3.8) - 2023-11-21

<small>[Compare with v0.3.6](https://github.com/trojblue/unibox/compare/v0.3.6...v0.3.8)</small>

### Features

- support saving string as a txt file ([5748e96](https://github.com/trojblue/unibox/commit/5748e96c9fcf3ea2a861b18294a1233709a1b59f) by yada).
- adding url support for unibox.loads() ([9cc351b](https://github.com/trojblue/unibox/commit/9cc351ba2abab90aa6c1f44900810d857846f69e) by yada).

## [v0.3.6](https://github.com/trojblue/unibox/releases/tag/v0.3.6) - 2023-11-12

<small>[Compare with v0.3.5](https://github.com/trojblue/unibox/compare/v0.3.5...v0.3.6)</small>

### Features

- support s3 uri in unibox.saves() ([7e0db63](https://github.com/trojblue/unibox/commit/7e0db63c2fec35a976bddd3f3f2faa6cb7bd08ab) by yada).
- support s3 uri in unibox.loads() ([7850ed4](https://github.com/trojblue/unibox/commit/7850ed4d4aba9f6aab5dd39363398c74e00e09cf) by yada).

### Bug Fixes

- incorrect filename when using unibox.saves() on s3 ([27a4121](https://github.com/trojblue/unibox/commit/27a41214f4e0e2d9403b0ec486391b8e7d75bcca) by yada).

## [v0.3.5](https://github.com/trojblue/unibox/releases/tag/v0.3.5) - 2023-11-02

<small>[Compare with v0.3.4](https://github.com/trojblue/unibox/compare/v0.3.4...v0.3.5)</small>

### Features

- s3client | bump version to 0.3.5 ([a0db95a](https://github.com/trojblue/unibox/commit/a0db95a47d1d85f3ebcc1d65074dd983a3d3c42f) by yada).

## [v0.3.4](https://github.com/trojblue/unibox/releases/tag/v0.3.4) - 2023-11-01

<small>[Compare with v0.3.3](https://github.com/trojblue/unibox/compare/v0.3.3...v0.3.4)</small>

### Bug Fixes

- merges at __init__.py ([ca658ed](https://github.com/trojblue/unibox/commit/ca658ed1e26b1b5087e7dcfaa658f7e8cca4cc8d) by yada).

## [v0.3.3](https://github.com/trojblue/unibox/releases/tag/v0.3.3) - 2023-11-01

<small>[Compare with v0.3.2](https://github.com/trojblue/unibox/compare/v0.3.2...v0.3.3)</small>

## [v0.3.2](https://github.com/trojblue/unibox/releases/tag/v0.3.2) - 2023-11-01

<small>[Compare with v0.3.1](https://github.com/trojblue/unibox/compare/v0.3.1...v0.3.2)</small>

### Features

- UniMerger: unibox.merges(data1, data2) ([d156e29](https://github.com/trojblue/unibox/commit/d156e29360981e631c7f3ce1a5ddf2729e1e72d7) by yada).

## [v0.3.1](https://github.com/trojblue/unibox/releases/tag/v0.3.1) - 2023-09-17

<small>[Compare with v0.3.0](https://github.com/trojblue/unibox/compare/v0.3.0...v0.3.1)</small>

## [v0.3.0](https://github.com/trojblue/unibox/releases/tag/v0.3.0) - 2023-09-03

<small>[Compare with v0.2.14](https://github.com/trojblue/unibox/compare/v0.2.14...v0.3.0)</small>

### Features

- image resizer: adding debug prints ([bcb55df](https://github.com/trojblue/unibox/commit/bcb55dfc1ba060ebddb4758cbf6c775d67d75801) by yada).
- image resizer: adding ability to skip existing images ([c745646](https://github.com/trojblue/unibox/commit/c745646bd4ab16f79dded643f6e75ea9ad00ec35) by yada).
- adding resizer-next ([2ee732c](https://github.com/trojblue/unibox/commit/2ee732c369d95c2b5ba45e003a57b33060b0e3f4) by yada).

### Bug Fixes

- find existing images and remove them from jobs list ([4ba16d9](https://github.com/trojblue/unibox/commit/4ba16d9e0e09e53712b22059d30177c45252ef3e) by yada).
- adding lower() to suffix before doing checks ([cc17d5c](https://github.com/trojblue/unibox/commit/cc17d5c2fabec10cecb6208dd169db30c54a2064) by yada).

## [v0.2.14](https://github.com/trojblue/unibox/releases/tag/v0.2.14) - 2023-09-02

<small>[Compare with v0.2.13](https://github.com/trojblue/unibox/compare/v0.2.13...v0.2.14)</small>

### Features

- adding traverses() method for unibox ([fe997a2](https://github.com/trojblue/unibox/commit/fe997a29f6e32308dc340120adabea003de34308) by yada).

## [v0.2.13](https://github.com/trojblue/unibox/releases/tag/v0.2.13) - 2023-08-26

<small>[Compare with v0.2.12](https://github.com/trojblue/unibox/compare/v0.2.12...v0.2.13)</small>

## [v0.2.12](https://github.com/trojblue/unibox/releases/tag/v0.2.12) - 2023-08-23

<small>[Compare with v0.2.11](https://github.com/trojblue/unibox/compare/v0.2.11...v0.2.12)</small>

### Features

- adding wip file renameer ([148280c](https://github.com/trojblue/unibox/commit/148280c956a7a4acbf55d0aceddd692f2f34317b) by yada).

## [v0.2.11](https://github.com/trojblue/unibox/releases/tag/v0.2.11) - 2023-08-21

<small>[Compare with v0.2.10](https://github.com/trojblue/unibox/compare/v0.2.10...v0.2.11)</small>

### Bug Fixes

- typing alias issue in python38 ([6179f3e](https://github.com/trojblue/unibox/commit/6179f3e84cd84e15ce8416f12cdba1316a73d175) by yada).

## [v0.2.10](https://github.com/trojblue/unibox/releases/tag/v0.2.10) - 2023-08-20

<small>[Compare with v0.2.9](https://github.com/trojblue/unibox/compare/v0.2.9...v0.2.10)</small>

### Features

- reducing minimum  python dependency from 3.10 to 3.8 ([bcf96e6](https://github.com/trojblue/unibox/commit/bcf96e67a5285c5b0d729a291d781241ac1ead0b) by yada).

## [v0.2.9](https://github.com/trojblue/unibox/releases/tag/v0.2.9) - 2023-08-19

<small>[Compare with v0.2.8](https://github.com/trojblue/unibox/compare/v0.2.8...v0.2.9)</small>

## [v0.2.8](https://github.com/trojblue/unibox/releases/tag/v0.2.8) - 2023-08-18

<small>[Compare with v0.2.7](https://github.com/trojblue/unibox/compare/v0.2.7...v0.2.8)</small>

## [v0.2.7](https://github.com/trojblue/unibox/releases/tag/v0.2.7) - 2023-08-17

<small>[Compare with v0.2.6](https://github.com/trojblue/unibox/compare/v0.2.6...v0.2.7)</small>

## [v0.2.6](https://github.com/trojblue/unibox/releases/tag/v0.2.6) - 2023-08-15

<small>[Compare with v0.2.5](https://github.com/trojblue/unibox/compare/v0.2.5...v0.2.6)</small>

## [v0.2.5](https://github.com/trojblue/unibox/releases/tag/v0.2.5) - 2023-08-15

<small>[Compare with v0.2.3](https://github.com/trojblue/unibox/compare/v0.2.3...v0.2.5)</small>

### Features

- updating UniTraverser for stateful calls and filepath store ([0e385e9](https://github.com/trojblue/unibox/commit/0e385e92016c6f26c57acf121d90b8cefd700e44) by yada).
- adding UniTraverser class: code that traverses trhough directory ([2e6ebff](https://github.com/trojblue/unibox/commit/2e6ebff631885303ce73347dfe6626c5a75f87c8) by yada).

## [v0.2.3](https://github.com/trojblue/unibox/releases/tag/v0.2.3) - 2023-08-14

<small>[Compare with v0.2.2](https://github.com/trojblue/unibox/compare/v0.2.2...v0.2.3)</small>

### Features

- remove pandas / pyarrow dep version ([fe83df4](https://github.com/trojblue/unibox/commit/fe83df4602547aa8538c4008eb5f9c708c185662) by yada).

## [v0.2.2](https://github.com/trojblue/unibox/releases/tag/v0.2.2) - 2023-08-13

<small>[Compare with v0.1.4.3](https://github.com/trojblue/unibox/compare/v0.1.4.3...v0.2.2)</small>

### Features

- adding unisaver ([62d2eb2](https://github.com/trojblue/unibox/commit/62d2eb29c19f16cbec8944208bd66ffcf601dae6) by yada).
- adding UniSaver and unibox.saves() method; bump version number to 0.2.0 ([4eec7b2](https://github.com/trojblue/unibox/commit/4eec7b2a885ace831cd52484e6f2bd9096379e7d) by yada).

## [v0.1.4.3](https://github.com/trojblue/unibox/releases/tag/v0.1.4.3) - 2023-07-16

<small>[Compare with v0.1.4](https://github.com/trojblue/unibox/compare/v0.1.4...v0.1.4.3)</small>

### Features

- updating loads() for jsonl files ([ccf54f3](https://github.com/trojblue/unibox/commit/ccf54f309fb50e762bc29216fec6b2f1b93e7536) by yada).

## [v0.1.4](https://github.com/trojblue/unibox/releases/tag/v0.1.4) - 2023-07-14

<small>[Compare with v0.1.3.5](https://github.com/trojblue/unibox/compare/v0.1.3.5...v0.1.4)</small>

### Features

- optimizing UniLoader class for csv & parquet ([383215f](https://github.com/trojblue/unibox/commit/383215f39eef5fd84cdf742b3966bc5ce2a17966) by yada).

## [v0.1.3.5](https://github.com/trojblue/unibox/releases/tag/v0.1.3.5) - 2023-07-14

<small>[Compare with v0.1.3.4](https://github.com/trojblue/unibox/compare/v0.1.3.4...v0.1.3.5)</small>

### Features

- adding file mover; update image resizer ([4d46099](https://github.com/trojblue/unibox/commit/4d46099d3fbe37f1e5cb3d5d4ae475f6b16cf433) by yada).

## [v0.1.3.4](https://github.com/trojblue/unibox/releases/tag/v0.1.3.4) - 2023-07-10

<small>[Compare with v0.1.3.3](https://github.com/trojblue/unibox/compare/v0.1.3.3...v0.1.3.4)</small>

### Features

- using ProcessPool instead of ThreadPool; before: 80it/s -> now: 105it/s ([0180ad1](https://github.com/trojblue/unibox/commit/0180ad1b3d15bb487da7eab255d4a397df341ecd) by yada).

## [v0.1.3.3](https://github.com/trojblue/unibox/releases/tag/v0.1.3.3) - 2023-07-10

<small>[Compare with v0.1.3.2](https://github.com/trojblue/unibox/compare/v0.1.3.2...v0.1.3.3)</small>

### Bug Fixes

- missing _resize ([4d5fa90](https://github.com/trojblue/unibox/commit/4d5fa9011ce42cbf65b289f446b3631aff6d6777) by yada).

## [v0.1.3.2](https://github.com/trojblue/unibox/releases/tag/v0.1.3.2) - 2023-07-10

<small>[Compare with v0.1.3](https://github.com/trojblue/unibox/compare/v0.1.3...v0.1.3.2)</small>

### Features

- updating version number ([3c25239](https://github.com/trojblue/unibox/commit/3c25239bc96e3718579ac9ca2189138404927ea4) by yada).

### Bug Fixes

- not resizing image when min_size > actual size ([85acf5d](https://github.com/trojblue/unibox/commit/85acf5db56bb23b255d195594d5d91b6f82d8c92) by yada).

## [v0.1.3](https://github.com/trojblue/unibox/releases/tag/v0.1.3) - 2023-07-10

<small>[Compare with 0.1.21](https://github.com/trojblue/unibox/compare/0.1.21...v0.1.3)</small>

### Features

- updating cli & click requirement version ([cd324bd](https://github.com/trojblue/unibox/commit/cd324bdad77ae65c15b2ea99884607162ba2e0cf) by yada).
- adding image resizer; refactor dir ([8586022](https://github.com/trojblue/unibox/commit/8586022c4eb98e2fce754d3f3d1935ff779cd07b) by yada).

## [0.1.21](https://github.com/trojblue/unibox/releases/tag/0.1.21) - 2023-07-06

<small>[Compare with v0.1.2.1](https://github.com/trojblue/unibox/compare/v0.1.2.1...0.1.21)</small>

## [v0.1.2.1](https://github.com/trojblue/unibox/releases/tag/v0.1.2.1) - 2023-07-06

<small>[Compare with v0.1.2](https://github.com/trojblue/unibox/compare/v0.1.2...v0.1.2.1)</small>

## [v0.1.2](https://github.com/trojblue/unibox/releases/tag/v0.1.2) - 2023-07-06

<small>[Compare with v0.1](https://github.com/trojblue/unibox/compare/v0.1...v0.1.2)</small>

### Bug Fixes

- update version number ([d5dc53a](https://github.com/trojblue/unibox/commit/d5dc53a126ec8cef2158aab4a4eb10f312a23aa4) by yada).

## [v0.1](https://github.com/trojblue/unibox/releases/tag/v0.1) - 2023-07-06

<small>[Compare with first commit](https://github.com/trojblue/unibox/compare/53031b4e33f8b62104ad2b139ff709005b3f4f25...v0.1)</small>

### Features

- adding pipeline logger & loader ([56043e4](https://github.com/trojblue/unibox/commit/56043e427a8f0aa641f96b7e0dcf229e39e5c456) by yada).
- adding basic functionality ([42d83cb](https://github.com/trojblue/unibox/commit/42d83cb9fd208fd76a07f9a98a2cd26c5eb1f367) by yada).

## [v0.5.0](https://github.com/trojblue/unibox/releases/tag/v0.5.0) - 2025-01-04

<small>[Compare with v0.4.13](https://github.com/trojblue/unibox/compare/v0.4.13...v0.5.0)</small>

### Features

- adding proper colorized logger ([9e0d758](https://github.com/trojblue/unibox/commit/9e0d7584c9b23b46f5d8ec35b1fcf87e5c5c8807) by yada).
- adding basic huggingface upload tools ([f412a18](https://github.com/trojblue/unibox/commit/f412a184cfd2bb36969dd79d6b24395a1b49f353) by yada).
- adding huggingface storage backend ([4c93076](https://github.com/trojblue/unibox/commit/4c930763e962984a292dd8be39b285c60a1e8bd3) by yada).
- adding basic test suite and txt loader ([bc16177](https://github.com/trojblue/unibox/commit/bc16177939e6462df38c8b59c6ff671ed88c31b0) by yada).
- adding basic working loader and tests ([aa65789](https://github.com/trojblue/unibox/commit/aa657895d3b48272228dfcb884834f372370c982) by yada).
- adding skeleton loader classes ([a1e299f](https://github.com/trojblue/unibox/commit/a1e299f2b1b2635451f94d581d984d85373665e1) by yada).

### Bug Fixes

- huggingface uploading an datasets object; s3 incorrect uri passed in ([e5bb8d2](https://github.com/trojblue/unibox/commit/e5bb8d2ea3673954f6e717fd1003197118e915b5) by yada).
- adding colorlog dependency ([a746230](https://github.com/trojblue/unibox/commit/a7462307a4307ef942f4539f4024b88012efafc1) by yada).
- adding datasets dependency ([071e5cc](https://github.com/trojblue/unibox/commit/071e5ccf86027a85a03f29650b338e707b4de73b) by yada).
- color control characters getting written to logs ([ecf1781](https://github.com/trojblue/unibox/commit/ecf1781d07305c86fb5685cd641d502c3f96f433) by yada).
- image_loader: properly handling image loaders ([cf5e535](https://github.com/trojblue/unibox/commit/cf5e535a431ad7f3f1fed49e431fef3312fd23fb) by yada).
- double write penalty at ub.saves() ([ec07b9b](https://github.com/trojblue/unibox/commit/ec07b9b188aeb1de946885824db8071e85e8e6c8) by yada).
- adding convert to rgb when using gallery ([0e5826d](https://github.com/trojblue/unibox/commit/0e5826d247120f26f06a8d54c337d4ee3b5ebcc7) by yada).

### Code Refactoring

- remoivng old files ([5e59240](https://github.com/trojblue/unibox/commit/5e592405d7c5cfbff9558f1b1ea6a5b1b4f0ab4a) by yada).
- adding project template ([fd95d45](https://github.com/trojblue/unibox/commit/fd95d45f19091c2b06d77e92bbf71add53ce75bb) by yada).

## [v0.4.13](https://github.com/trojblue/unibox/releases/tag/v0.4.13) - 2024-11-17

<small>[Compare with v0.4.12](https://github.com/trojblue/unibox/compare/v0.4.12...v0.4.13)</small>

### Features

- adding ub.label_gallery() tool for data labelling ([0fdac23](https://github.com/trojblue/unibox/commit/0fdac23b882a2c3c616d68291b4f66c9c92ffda3) by yada).

## [v0.4.12](https://github.com/trojblue/unibox/releases/tag/v0.4.12) - 2024-09-30

<small>[Compare with v0.4.11](https://github.com/trojblue/unibox/compare/v0.4.11...v0.4.12)</small>

### Features

- allowing human-readable date in presigns() expiration ([1381b9a](https://github.com/trojblue/unibox/commit/1381b9aa810d342b5a53fe8df86a537baf44bc6d) by yada).

## [v0.4.11](https://github.com/trojblue/unibox/releases/tag/v0.4.11) - 2024-09-30

<small>[Compare with v0.4.10](https://github.com/trojblue/unibox/compare/v0.4.10...v0.4.11)</small>

### Features

- s3_client: adding generate_presigned_uri function; removing unused code ([ccfcbc8](https://github.com/trojblue/unibox/commit/ccfcbc8e3087c2adde77c59e26b7553ca63a05b8) by yada).

## [v0.4.10](https://github.com/trojblue/unibox/releases/tag/v0.4.10) - 2024-07-22

<small>[Compare with v0.4.9](https://github.com/trojblue/unibox/compare/v0.4.9...v0.4.10)</small>

### Bug Fixes

- further ipython import fix ([faac26f](https://github.com/trojblue/unibox/commit/faac26fe0341a3a5d838a01f88378d0edaf683e5) by yada).

## [v0.4.9](https://github.com/trojblue/unibox/releases/tag/v0.4.9) - 2024-07-22

<small>[Compare with v0.4.8](https://github.com/trojblue/unibox/compare/v0.4.8...v0.4.9)</small>

### Bug Fixes

- missing ipython dependency when calling ub.peeks() ([989b471](https://github.com/trojblue/unibox/commit/989b47141d5e1cd1d9a40900c79e2b18599da89a) by yada).

## [v0.4.8](https://github.com/trojblue/unibox/releases/tag/v0.4.8) - 2024-07-18

<small>[Compare with v0.4.7](https://github.com/trojblue/unibox/compare/v0.4.7...v0.4.8)</small>

### Bug Fixes

- concurrent_loads: fixing load order ([74ac31f](https://github.com/trojblue/unibox/commit/74ac31f0b06c273a4ff8487ad596f408470bccf6) by yada).

## [v0.4.7](https://github.com/trojblue/unibox/releases/tag/v0.4.7) - 2024-07-18

<small>[Compare with v0.4.6](https://github.com/trojblue/unibox/compare/v0.4.6...v0.4.7)</small>

### Features

- ub.gallery(): adding notebook gallery ([4f577a3](https://github.com/trojblue/unibox/commit/4f577a36f391ce22229da255dd2d3002024359d3) by yada).
- adding ub.ls() wrapper for shorter ub.traverses() ([e991c05](https://github.com/trojblue/unibox/commit/e991c0572846c1877dd6276b82f4ca69762512ee) by yada).
- uni_peeker: adding peek_df functionality ([ed78393](https://github.com/trojblue/unibox/commit/ed7839335227a196a83e176f0e6cbbcbeb282e37) by yada).
- adding concurrent_loads() function ([c3201d3](https://github.com/trojblue/unibox/commit/c3201d3a72baba49b3ef0f27548bd8664a734a4d) by yada).

### Bug Fixes

- ub.loads: tempfile naming error on windows ([1d454d5](https://github.com/trojblue/unibox/commit/1d454d5a0eda5bfad161019055d9e2fff1bb0573) by yada).

## [v0.4.6](https://github.com/trojblue/unibox/releases/tag/v0.4.6) - 2024-06-28

<small>[Compare with v0.4.5](https://github.com/trojblue/unibox/compare/v0.4.5...v0.4.6)</small>

### Bug Fixes

- UniSaver: replace NaN with null if saving to dict or jsonl ([5babfb8](https://github.com/trojblue/unibox/commit/5babfb81174f189869ae3c24d34d5a3e0bf5c2b4) by yada).

## [v0.4.5](https://github.com/trojblue/unibox/releases/tag/v0.4.5) - 2024-06-28

<small>[Compare with v0.4.4](https://github.com/trojblue/unibox/compare/v0.4.4...v0.4.5)</small>

### Bug Fixes

- adding graceful handling for errors when a line is unbale to be read ([0965249](https://github.com/trojblue/unibox/commit/09652499a6a0cf2f84dc4f98b4a8e23695180c41) by yada).

## [v0.4.4](https://github.com/trojblue/unibox/releases/tag/v0.4.4) - 2024-06-14

<small>[Compare with v0.4.3](https://github.com/trojblue/unibox/compare/v0.4.3...v0.4.4)</small>

### Bug Fixes

- ub.saves(); a bug where ub.saves(list[str]) won't correctly save ([3849e63](https://github.com/trojblue/unibox/commit/3849e63f7493309899a5dd178e94066cc5d19358) by yada).

## [v0.4.3](https://github.com/trojblue/unibox/releases/tag/v0.4.3) - 2024-06-13

<small>[Compare with v0.4.2](https://github.com/trojblue/unibox/compare/v0.4.2...v0.4.3)</small>

### Features

- add ability to save various formatted image files as png file ([8142695](https://github.com/trojblue/unibox/commit/8142695ef26433daed162780e5acc24c885d53fc) by yada).

### Bug Fixes

- resolved bug that prevents loading files from url ([c9cb709](https://github.com/trojblue/unibox/commit/c9cb7098479b0f854561bf2c6178ff16ab89cef6) by yada).

## [v0.4.2](https://github.com/trojblue/unibox/releases/tag/v0.4.2) - 2024-05-30

<small>[Compare with v0.4.1](https://github.com/trojblue/unibox/compare/v0.4.1...v0.4.2)</small>

### Features

- extend include_extensions at ub.traverses() to take more than extensions ([593b69c](https://github.com/trojblue/unibox/commit/593b69c2027181fc683a80b0c396b2dc0e53b7cd) by yada).

## [v0.4.1](https://github.com/trojblue/unibox/releases/tag/v0.4.1) - 2024-05-18

<small>[Compare with v0.4.0](https://github.com/trojblue/unibox/compare/v0.4.0...v0.4.1)</small>

### Bug Fixes

- ub.traverses(): traversing a s3 directory will not return the dir itself ([f0d85db](https://github.com/trojblue/unibox/commit/f0d85db8483ed17340d88d4bce17c94f9642734d) by yada).

## [v0.4.0](https://github.com/trojblue/unibox/releases/tag/v0.4.0) - 2024-05-08

<small>[Compare with v0.3.20](https://github.com/trojblue/unibox/compare/v0.3.20...v0.4.0)</small>

### Bug Fixes

- resizer hangs when handling large number of images to be resized ([9627894](https://github.com/trojblue/unibox/commit/96278949d0cb92084a2ee422c655fb5976fb3f27) by yada).

## [v0.3.20](https://github.com/trojblue/unibox/releases/tag/v0.3.20) - 2024-03-13

<small>[Compare with v0.3.19](https://github.com/trojblue/unibox/compare/v0.3.19...v0.3.20)</small>

### Features

- adding load feather support on uniloader ([fee98ff](https://github.com/trojblue/unibox/commit/fee98ff031e65a1caf0481ed40e1d11ae72e7112) by yada).

## [v0.3.19](https://github.com/trojblue/unibox/releases/tag/v0.3.19) - 2024-03-09

<small>[Compare with v0.3.18](https://github.com/trojblue/unibox/compare/v0.3.18...v0.3.19)</small>

### Bug Fixes

- incorrect behavior signature on ub.loads() on s3 uri ([ca00b40](https://github.com/trojblue/unibox/commit/ca00b4021dbeccf4c1fa3d04f3e2888d60c34647) by yada).

## [v0.3.18](https://github.com/trojblue/unibox/releases/tag/v0.3.18) - 2024-03-06

<small>[Compare with v0.3.17](https://github.com/trojblue/unibox/compare/v0.3.17...v0.3.18)</small>

## [v0.3.17](https://github.com/trojblue/unibox/releases/tag/v0.3.17) - 2024-03-06

<small>[Compare with v0.3.16](https://github.com/trojblue/unibox/compare/v0.3.16...v0.3.17)</small>

### Bug Fixes

- unclosed image at uniresizer ([b554630](https://github.com/trojblue/unibox/commit/b55463069f757aa63e62c2556116c2497a9c5e59) by yada).

## [v0.3.16](https://github.com/trojblue/unibox/releases/tag/v0.3.16) - 2024-03-05

<small>[Compare with v0.3.15](https://github.com/trojblue/unibox/compare/v0.3.15...v0.3.16)</small>

### Bug Fixes

- adding back max_workers in uni_resizer ([7c533f6](https://github.com/trojblue/unibox/commit/7c533f6760d4e4d7a6cd62d06a29ed4751de70da) by yada).

## [v0.3.15](https://github.com/trojblue/unibox/releases/tag/v0.3.15) - 2024-02-12

<small>[Compare with v0.3.14](https://github.com/trojblue/unibox/compare/v0.3.14...v0.3.15)</small>

### Features

- adding debug_print argument to unibox.traverses() ([66d1c02](https://github.com/trojblue/unibox/commit/66d1c0260ccf9d1f6bc3ad2abbc33fb1001ff52d) by yada).

## [v0.3.14](https://github.com/trojblue/unibox/releases/tag/v0.3.14) - 2023-12-18

<small>[Compare with v0.3.13](https://github.com/trojblue/unibox/compare/v0.3.13...v0.3.14)</small>

### Bug Fixes

- using unibox.loads() with s3 ([2ba1a57](https://github.com/trojblue/unibox/commit/2ba1a57e86e641f9dd64367315f61c032d1691ae) by yada).

## [v0.3.13](https://github.com/trojblue/unibox/releases/tag/v0.3.13) - 2023-12-14

<small>[Compare with v0.3.12](https://github.com/trojblue/unibox/compare/v0.3.12...v0.3.13)</small>

### Bug Fixes

- include ipykernel version to avoid tqdm issues ([a081b70](https://github.com/trojblue/unibox/commit/a081b70a4df1fd26eed97929248bb03a57a18b3c) by yada).
- traverses() with folder: incomplete s3 uri ([3b4d25b](https://github.com/trojblue/unibox/commit/3b4d25be0b10182035071db29fe47939e16bf29e) by yada).
- adding unit for traverse s3 ([c7d00d7](https://github.com/trojblue/unibox/commit/c7d00d7a345bf606a5642be00de1a0e7f6ef9e96) by yada).

## [v0.3.12](https://github.com/trojblue/unibox/releases/tag/v0.3.12) - 2023-12-12

<small>[Compare with v0.3.11](https://github.com/trojblue/unibox/compare/v0.3.11...v0.3.12)</small>

### Bug Fixes

- traverses(s3): allowing traverses() to return dir info ([0af5fdb](https://github.com/trojblue/unibox/commit/0af5fdbfcaf5c2bc461d36e0f2411f746357655b) by yada).

## [v0.3.11](https://github.com/trojblue/unibox/releases/tag/v0.3.11) - 2023-12-11

<small>[Compare with v0.3.10](https://github.com/trojblue/unibox/compare/v0.3.10...v0.3.11)</small>

### Features

- unibox.peeks(): adding list peek support & proper command use ([c346f99](https://github.com/trojblue/unibox/commit/c346f9984dea68928654dba036e968de728619ec) by yada).

## [v0.3.10](https://github.com/trojblue/unibox/releases/tag/v0.3.10) - 2023-12-11

<small>[Compare with v0.3.9](https://github.com/trojblue/unibox/compare/v0.3.9...v0.3.10)</small>

### Features

- adding support for s3 dir in unibox.traverses() ([b90a97a](https://github.com/trojblue/unibox/commit/b90a97ae80404a175e60c8e5756e14bab7727330) by yada).
- adding unipeeker and unibox.peeks() method for previewing data ([7b7a7cd](https://github.com/trojblue/unibox/commit/7b7a7cdffa0de719acd7ee58976055210b3f71b9) by yada).
- adding traverse() in s3 client ([3d786b3](https://github.com/trojblue/unibox/commit/3d786b3972866366b352d604250fde06f8e0bd25) by yada).

## [v0.3.9](https://github.com/trojblue/unibox/releases/tag/v0.3.9) - 2023-12-10

<small>[Compare with v0.3.8](https://github.com/trojblue/unibox/compare/v0.3.8...v0.3.9)</small>

### Bug Fixes

- unibox.loads(): add ability to properly load files from url ([32c5593](https://github.com/trojblue/unibox/commit/32c55931e6e8f9264b458a7ad8d37bac39e96cf5) by yada).

## [v0.3.8](https://github.com/trojblue/unibox/releases/tag/v0.3.8) - 2023-11-21

<small>[Compare with v0.3.6](https://github.com/trojblue/unibox/compare/v0.3.6...v0.3.8)</small>

### Features

- support saving string as a txt file ([5748e96](https://github.com/trojblue/unibox/commit/5748e96c9fcf3ea2a861b18294a1233709a1b59f) by yada).
- adding url support for unibox.loads() ([9cc351b](https://github.com/trojblue/unibox/commit/9cc351ba2abab90aa6c1f44900810d857846f69e) by yada).

## [v0.3.6](https://github.com/trojblue/unibox/releases/tag/v0.3.6) - 2023-11-12

<small>[Compare with v0.3.5](https://github.com/trojblue/unibox/compare/v0.3.5...v0.3.6)</small>

### Features

- support s3 uri in unibox.saves() ([7e0db63](https://github.com/trojblue/unibox/commit/7e0db63c2fec35a976bddd3f3f2faa6cb7bd08ab) by yada).
- support s3 uri in unibox.loads() ([7850ed4](https://github.com/trojblue/unibox/commit/7850ed4d4aba9f6aab5dd39363398c74e00e09cf) by yada).

### Bug Fixes

- incorrect filename when using unibox.saves() on s3 ([27a4121](https://github.com/trojblue/unibox/commit/27a41214f4e0e2d9403b0ec486391b8e7d75bcca) by yada).

## [v0.3.5](https://github.com/trojblue/unibox/releases/tag/v0.3.5) - 2023-11-02

<small>[Compare with v0.3.4](https://github.com/trojblue/unibox/compare/v0.3.4...v0.3.5)</small>

### Features

- s3client | bump version to 0.3.5 ([a0db95a](https://github.com/trojblue/unibox/commit/a0db95a47d1d85f3ebcc1d65074dd983a3d3c42f) by yada).

## [v0.3.4](https://github.com/trojblue/unibox/releases/tag/v0.3.4) - 2023-11-01

<small>[Compare with v0.3.3](https://github.com/trojblue/unibox/compare/v0.3.3...v0.3.4)</small>

### Bug Fixes

- merges at __init__.py ([ca658ed](https://github.com/trojblue/unibox/commit/ca658ed1e26b1b5087e7dcfaa658f7e8cca4cc8d) by yada).

## [v0.3.3](https://github.com/trojblue/unibox/releases/tag/v0.3.3) - 2023-11-01

<small>[Compare with v0.3.2](https://github.com/trojblue/unibox/compare/v0.3.2...v0.3.3)</small>

## [v0.3.2](https://github.com/trojblue/unibox/releases/tag/v0.3.2) - 2023-11-01

<small>[Compare with v0.3.1](https://github.com/trojblue/unibox/compare/v0.3.1...v0.3.2)</small>

### Features

- UniMerger: unibox.merges(data1, data2) ([d156e29](https://github.com/trojblue/unibox/commit/d156e29360981e631c7f3ce1a5ddf2729e1e72d7) by yada).

## [v0.3.1](https://github.com/trojblue/unibox/releases/tag/v0.3.1) - 2023-09-17

<small>[Compare with v0.3.0](https://github.com/trojblue/unibox/compare/v0.3.0...v0.3.1)</small>

## [v0.3.0](https://github.com/trojblue/unibox/releases/tag/v0.3.0) - 2023-09-03

<small>[Compare with v0.2.14](https://github.com/trojblue/unibox/compare/v0.2.14...v0.3.0)</small>

### Features

- image resizer: adding debug prints ([bcb55df](https://github.com/trojblue/unibox/commit/bcb55dfc1ba060ebddb4758cbf6c775d67d75801) by yada).
- image resizer: adding ability to skip existing images ([c745646](https://github.com/trojblue/unibox/commit/c745646bd4ab16f79dded643f6e75ea9ad00ec35) by yada).
- adding resizer-next ([2ee732c](https://github.com/trojblue/unibox/commit/2ee732c369d95c2b5ba45e003a57b33060b0e3f4) by yada).

### Bug Fixes

- find existing images and remove them from jobs list ([4ba16d9](https://github.com/trojblue/unibox/commit/4ba16d9e0e09e53712b22059d30177c45252ef3e) by yada).
- adding lower() to suffix before doing checks ([cc17d5c](https://github.com/trojblue/unibox/commit/cc17d5c2fabec10cecb6208dd169db30c54a2064) by yada).

## [v0.2.14](https://github.com/trojblue/unibox/releases/tag/v0.2.14) - 2023-09-02

<small>[Compare with v0.2.13](https://github.com/trojblue/unibox/compare/v0.2.13...v0.2.14)</small>

### Features

- adding traverses() method for unibox ([fe997a2](https://github.com/trojblue/unibox/commit/fe997a29f6e32308dc340120adabea003de34308) by yada).

## [v0.2.13](https://github.com/trojblue/unibox/releases/tag/v0.2.13) - 2023-08-26

<small>[Compare with v0.2.12](https://github.com/trojblue/unibox/compare/v0.2.12...v0.2.13)</small>

## [v0.2.12](https://github.com/trojblue/unibox/releases/tag/v0.2.12) - 2023-08-23

<small>[Compare with v0.2.11](https://github.com/trojblue/unibox/compare/v0.2.11...v0.2.12)</small>

### Features

- adding wip file renameer ([148280c](https://github.com/trojblue/unibox/commit/148280c956a7a4acbf55d0aceddd692f2f34317b) by yada).

## [v0.2.11](https://github.com/trojblue/unibox/releases/tag/v0.2.11) - 2023-08-21

<small>[Compare with v0.2.10](https://github.com/trojblue/unibox/compare/v0.2.10...v0.2.11)</small>

### Bug Fixes

- typing alias issue in python38 ([6179f3e](https://github.com/trojblue/unibox/commit/6179f3e84cd84e15ce8416f12cdba1316a73d175) by yada).

## [v0.2.10](https://github.com/trojblue/unibox/releases/tag/v0.2.10) - 2023-08-20

<small>[Compare with v0.2.9](https://github.com/trojblue/unibox/compare/v0.2.9...v0.2.10)</small>

### Features

- reducing minimum  python dependency from 3.10 to 3.8 ([bcf96e6](https://github.com/trojblue/unibox/commit/bcf96e67a5285c5b0d729a291d781241ac1ead0b) by yada).

## [v0.2.9](https://github.com/trojblue/unibox/releases/tag/v0.2.9) - 2023-08-19

<small>[Compare with v0.2.8](https://github.com/trojblue/unibox/compare/v0.2.8...v0.2.9)</small>

## [v0.2.8](https://github.com/trojblue/unibox/releases/tag/v0.2.8) - 2023-08-18

<small>[Compare with v0.2.7](https://github.com/trojblue/unibox/compare/v0.2.7...v0.2.8)</small>

## [v0.2.7](https://github.com/trojblue/unibox/releases/tag/v0.2.7) - 2023-08-17

<small>[Compare with v0.2.6](https://github.com/trojblue/unibox/compare/v0.2.6...v0.2.7)</small>

## [v0.2.6](https://github.com/trojblue/unibox/releases/tag/v0.2.6) - 2023-08-15

<small>[Compare with v0.2.5](https://github.com/trojblue/unibox/compare/v0.2.5...v0.2.6)</small>

## [v0.2.5](https://github.com/trojblue/unibox/releases/tag/v0.2.5) - 2023-08-15

<small>[Compare with v0.2.3](https://github.com/trojblue/unibox/compare/v0.2.3...v0.2.5)</small>

### Features

- updating UniTraverser for stateful calls and filepath store ([0e385e9](https://github.com/trojblue/unibox/commit/0e385e92016c6f26c57acf121d90b8cefd700e44) by yada).
- adding UniTraverser class: code that traverses trhough directory ([2e6ebff](https://github.com/trojblue/unibox/commit/2e6ebff631885303ce73347dfe6626c5a75f87c8) by yada).

## [v0.2.3](https://github.com/trojblue/unibox/releases/tag/v0.2.3) - 2023-08-14

<small>[Compare with v0.2.2](https://github.com/trojblue/unibox/compare/v0.2.2...v0.2.3)</small>

### Features

- remove pandas / pyarrow dep version ([fe83df4](https://github.com/trojblue/unibox/commit/fe83df4602547aa8538c4008eb5f9c708c185662) by yada).

## [v0.2.2](https://github.com/trojblue/unibox/releases/tag/v0.2.2) - 2023-08-13

<small>[Compare with v0.1.4.3](https://github.com/trojblue/unibox/compare/v0.1.4.3...v0.2.2)</small>

### Features

- adding unisaver ([62d2eb2](https://github.com/trojblue/unibox/commit/62d2eb29c19f16cbec8944208bd66ffcf601dae6) by yada).
- adding UniSaver and unibox.saves() method; bump version number to 0.2.0 ([4eec7b2](https://github.com/trojblue/unibox/commit/4eec7b2a885ace831cd52484e6f2bd9096379e7d) by yada).

## [v0.1.4.3](https://github.com/trojblue/unibox/releases/tag/v0.1.4.3) - 2023-07-16

<small>[Compare with v0.1.4](https://github.com/trojblue/unibox/compare/v0.1.4...v0.1.4.3)</small>

### Features

- updating loads() for jsonl files ([ccf54f3](https://github.com/trojblue/unibox/commit/ccf54f309fb50e762bc29216fec6b2f1b93e7536) by yada).

## [v0.1.4](https://github.com/trojblue/unibox/releases/tag/v0.1.4) - 2023-07-14

<small>[Compare with v0.1.3.5](https://github.com/trojblue/unibox/compare/v0.1.3.5...v0.1.4)</small>

### Features

- optimizing UniLoader class for csv & parquet ([383215f](https://github.com/trojblue/unibox/commit/383215f39eef5fd84cdf742b3966bc5ce2a17966) by yada).

## [v0.1.3.5](https://github.com/trojblue/unibox/releases/tag/v0.1.3.5) - 2023-07-14

<small>[Compare with v0.1.3.4](https://github.com/trojblue/unibox/compare/v0.1.3.4...v0.1.3.5)</small>

### Features

- adding file mover; update image resizer ([4d46099](https://github.com/trojblue/unibox/commit/4d46099d3fbe37f1e5cb3d5d4ae475f6b16cf433) by yada).

## [v0.1.3.4](https://github.com/trojblue/unibox/releases/tag/v0.1.3.4) - 2023-07-10

<small>[Compare with v0.1.3.3](https://github.com/trojblue/unibox/compare/v0.1.3.3...v0.1.3.4)</small>

### Features

- using ProcessPool instead of ThreadPool; before: 80it/s -> now: 105it/s ([0180ad1](https://github.com/trojblue/unibox/commit/0180ad1b3d15bb487da7eab255d4a397df341ecd) by yada).

## [v0.1.3.3](https://github.com/trojblue/unibox/releases/tag/v0.1.3.3) - 2023-07-10

<small>[Compare with v0.1.3.2](https://github.com/trojblue/unibox/compare/v0.1.3.2...v0.1.3.3)</small>

### Bug Fixes

- missing _resize ([4d5fa90](https://github.com/trojblue/unibox/commit/4d5fa9011ce42cbf65b289f446b3631aff6d6777) by yada).

## [v0.1.3.2](https://github.com/trojblue/unibox/releases/tag/v0.1.3.2) - 2023-07-10

<small>[Compare with v0.1.3](https://github.com/trojblue/unibox/compare/v0.1.3...v0.1.3.2)</small>

### Features

- updating version number ([3c25239](https://github.com/trojblue/unibox/commit/3c25239bc96e3718579ac9ca2189138404927ea4) by yada).

### Bug Fixes

- not resizing image when min_size > actual size ([85acf5d](https://github.com/trojblue/unibox/commit/85acf5db56bb23b255d195594d5d91b6f82d8c92) by yada).

## [v0.1.3](https://github.com/trojblue/unibox/releases/tag/v0.1.3) - 2023-07-10

<small>[Compare with 0.1.21](https://github.com/trojblue/unibox/compare/0.1.21...v0.1.3)</small>

### Features

- updating cli & click requirement version ([cd324bd](https://github.com/trojblue/unibox/commit/cd324bdad77ae65c15b2ea99884607162ba2e0cf) by yada).
- adding image resizer; refactor dir ([8586022](https://github.com/trojblue/unibox/commit/8586022c4eb98e2fce754d3f3d1935ff779cd07b) by yada).

## [0.1.21](https://github.com/trojblue/unibox/releases/tag/0.1.21) - 2023-07-06

<small>[Compare with v0.1.2.1](https://github.com/trojblue/unibox/compare/v0.1.2.1...0.1.21)</small>

## [v0.1.2.1](https://github.com/trojblue/unibox/releases/tag/v0.1.2.1) - 2023-07-06

<small>[Compare with v0.1.2](https://github.com/trojblue/unibox/compare/v0.1.2...v0.1.2.1)</small>

## [v0.1.2](https://github.com/trojblue/unibox/releases/tag/v0.1.2) - 2023-07-06

<small>[Compare with v0.1](https://github.com/trojblue/unibox/compare/v0.1...v0.1.2)</small>

### Bug Fixes

- update version number ([d5dc53a](https://github.com/trojblue/unibox/commit/d5dc53a126ec8cef2158aab4a4eb10f312a23aa4) by yada).

## [v0.1](https://github.com/trojblue/unibox/releases/tag/v0.1) - 2023-07-06

<small>[Compare with first commit](https://github.com/trojblue/unibox/compare/53031b4e33f8b62104ad2b139ff709005b3f4f25...v0.1)</small>

### Features

- adding pipeline logger & loader ([56043e4](https://github.com/trojblue/unibox/commit/56043e427a8f0aa641f96b7e0dcf229e39e5c456) by yada).
- adding basic functionality ([42d83cb](https://github.com/trojblue/unibox/commit/42d83cb9fd208fd76a07f9a98a2cd26c5eb1f367) by yada).
