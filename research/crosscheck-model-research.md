# 独立中文 ASR 交叉稿：SenseVoice Small

日期：2026-10-15（Asia/Shanghai）。此轮针对既有 682 条交流记录及讲解中的错字，增加与 Whisper 不同模型家族的机器证据，不覆盖旧稿，不依据上下文猜字，不把交叉识别称为听校。

## 一手来源与选择

SenseVoiceSmall 的官方说明将其描述为非自回归语音模型，发布模型支持普通话、粤语、英语、日语、韩语。官方也明确它本身不输出说话人身份；额外说话人模型不属于本次配置。[SenseVoice 官方代码与说明](https://github.com/QwenAudio/SenseVoice)

sherpa-onnx 提供 macOS arm64 与 Python 接口，可以在本机 CPU 执行导出的 int8 模型，避免引入完整 PyTorch 环境。[sherpa-onnx SenseVoice 支持范围](https://k2-fsa.github.io/sherpa/onnx/sense-voice/index.html)

本次选官方 `2024-07-17` 通用 SenseVoiceSmall int8 导出。文档中的 `2025-09-09` 版本是增加粤语训练的变体；本材料主要为普通话，没有仅因日期较新就更换版本。使用 `language=zh`、`use_itn=True`，后者允许模型输出标点及数字规范化，仍可能改变词形。[官方预训练模型及版本说明](https://k2-fsa.github.io/sherpa/onnx/sense-voice/pretrained.html)

接口使用 `OfflineRecognizer.from_sense_voice`、`accept_waveform` 与 `decode_stream`，输出文本、tokens 及 token 时间戳。分段时间来自模型估计，不是实际回听定位。[官方 Python 例程](https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/offline-sense-voice-ctc-decode-files.py)

## 固定模型与环境

- 原始模型包：`sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2`，直接来自 [k2-fsa 官方 release](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2)。未使用未经核实的镜像。
- GitHub asset ID：`288366523`；包大小 `163002883` 字节；GitHub API 公布的 SHA-256 与本地复核均为 `7d1efa2138a65b0b488df37f8b89e3d91a60676e416f515b952358d83dfd347e`。
- ONNX：`model.int8.onnx`，`239233841` 字节；SHA-256 `c71f0ce00bec95b07744e116345e33d8cbbe08cef896382cf907bf4b51a2cd51`。
- token 表 SHA-256：`f449eb28dc567533d7fa59be34e2abca8784f771850c78a47fb731a31429a1dc`。
- 本机隔离环境：Python `3.12.14`、`sherpa-onnx==1.13.8`、`sherpa-onnx-core==1.13.8`、`numpy==2.5.4`；另装 `opencc-python-reimplemented==0.1.7` 供父任务比较繁简字，不改本轮原始输出。
- 单模型进程使用 CPU、2 线程、贪心 CTC 解码、中文、ITN 开启。首集验证后采用 2 个模型进程，各 2 线程；分别处理不重叠的集数分区。
- 环境目录约 85 MiB，解包模型目录约 242 MiB；重复压缩包仅用于校验，之后可删除。模型与运行环境在本轮全部比较结束前保留。

## 小段与完整首集实测

种子视频已有的本地 WAV 片段，不重新下载媒体：

| 原片范围 | 输入秒数 | 模型执行秒数 | 结果边界 |
|---|---:|---:|---|
| 00:00–00:30 | 30 | 2.693 | 旁白较连贯，边界处仍截词 |
| 00:28–00:58 | 30 | 2.507 | 能读出小模型缺漏的开场，但轻声短答与专名仍错 |
| 00:40–01:00 | 20 | 1.031 | 现场主句更完整，仍有“拍照讲”“于小慧”等待核词形 |

完整第 1 集 `BV1vj6yBDE5r`：解码音轨 `684.825` 秒；25 个窗口；ASR 执行 `44.317` 秒，包含转换与输出的总时间 `46.719` 秒；207 个规范段落；总 RTF 约 `0.068`。这是本机实测，不是官方性能数据，也不代表中文正确率。

例如 02:48–02:52 附近，新窗口识别出“正常冰还是少冰”，而旧 Whisper 出现“正常面/少边”；但相邻重叠窗口中的 SenseVoice 自身仍有“正常面”输出。该例支持增加候选证据，不支持自动认定任一模型正确。

据首集实测，继续完整 18 集交叉转写；双进程耗时取决于 CPU 共享与音频内容，不以单集 RTF 保证固定完成时间。逐集进度、散列与实际耗时写 `crosscheck-run-progress.json`，每集完成后即可独立使用。

## 音轨、窗口与时间映射

复用此前保留的 18 个原始 m4a，不重复下载原媒体。macOS `afconvert` 逐集转换 16 kHz、单声道、16 bit PCM，转换后的整轨 WAV 仅临时使用。

长音频按最多 30 秒窗口、28 秒步进执行，即相邻窗口重叠 2 秒。窗口使用原音轨的绝对采样偏移，保存 `source_start/source_end`、原输出文本、tokens、相对 token 时间及加偏移后的绝对时间。每个窗口先以临时文件写入，再原子替换，可在中断后凭原音轨与模型散列恢复。

规范 `segments` 按句末标点、超过 0.7 秒停顿或最多 40 字切分；ID 采用 `BV…-sensevoice-w00001-s001`，不与 Whisper、字幕或短段 probe 的 ID 混用。每段记录其窗口与 token 索引，因此可以追到未经上下文改写的 token 序列。

CTC 时间在样本中约以 60 ms 为格点。本次段落结束时间取末 token 发射时间加 120 ms，并限制在窗口内，**只是估计**。既有直接看帧核对的字幕采样区间不因此被覆盖。保留全部窗口与段落，重叠区可能重复、截词或不一致；不能直接串接成无重叠正文，也不能将模型一致率当正确率。

## 恢复与检查入口

私有 `cross-validation/launch_sensevoice.py` 协调两个集数分区，`run_sensevoice.py` 按窗口缓存恢复；同一集不会由两个进程同时写入。重新启动前先确认旧工作进程已退出。已完成源文件的 SHA-256 匹配时直接复用；未完成窗口先核对模型、原音轨散列和起止偏移。进度与最终源 JSON 均采用临时文件加原子替换，供并行比较任务稳定读取。

私有 `validate_sensevoice.py` 独立检查原音轨 SHA、全轨窗口首尾、token 数量与相对/绝对时间映射、段落引用索引、正文与 token 子串相等、全局 ID 唯一性。检查不判断语音内容准确率；运行环境的完整固定依赖保存在私有 `requirements-lock.txt`。原媒体、旧稿及看帧证据继续保留。

## 产物与限制

新文件仅写 `data/alternate-transcripts/BV…-sensevoice-crosscheck.json`，采用原子写入，包含稳定 ID、绝对时间、正文、窗口与 token 原始证据；旧原稿、交流记录及网页由各自负责者维护。

全部标记 `listening_verified:false`、说话人未验证。原片有音乐、混响、压低的现场声、交叠说话以及镜头外文字，独立模型同样会错字、漏句或切错边界。文字的可读性改善不是实际听校；父任务还需结合已有直接看帧证据和原片核对，分歧继续明确保留。

## 全量运行实测与来源验收

截至 `2026-10-15T17:16:56+08:00`，18 条原始音轨全部完成独立识别，唯一原片时长合计 `27814.298` 秒（约 7 小时 44 分钟）。共保留 `1002` 个重叠窗口、`8486` 个 token 派生段落和 `164637` 个 tokens；这些计数包含重叠区重复候选，不等于新增交流轮数或识别正确句数。18 份新来源 JSON 合计 `12460218` 字节。

各工作进程的 ASR 时间相加为 `2123.79` 秒，按唯一原片时长折算 RTF 约 `0.07636`，其中包含重叠窗口的重复推理。首集探针完成后，第 2–18 集双进程批次观测墙钟时间约 `20.17` 分钟；从首集开始到末集完成约 `21.83` 分钟，后者包含探针和编排间隙。逐集耗时见 `crosscheck-run-progress.json`，这些是本机任务实测，不能当作通用性能或准确率保证。

18 份来源的最终检查：原 m4a SHA、模型与 token 表 SHA、全轨窗口首尾覆盖、token 与相对/绝对时间对应、段落索引与正文逐 token 相等、全局稳定 ID，以及输出散列与进度记录的一致性全部通过；0 个结构错误、0 个长于 20 秒的估计段落警告。该检查验证的是来源和映射，未进行真实音频听校。全部 `listening_verified` 仍为 `false`。

完成时两个工作进程均已正常退出，临时整轨 WAV 目录为空。私有交叉验证目录占用约 495 MiB，其中环境约 85 MiB、解包模型约 242 MiB、重复校验压缩包约 155 MiB、窗口缓存约 8 MiB。18 个原 m4a 合计 `228215703` 字节，未重下、未删；旧稿、字幕帧证据及模型环境均继续保留，供本轮后续比较使用。
