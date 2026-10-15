# 修订记录独立抽审：来源、数字否定与练习资格

审查日期：2026-10-15（Asia/Shanghai）。**汇总：两批合计逐项文字抽审 69 条；抽审时结构复核覆盖 451 条。父侧最终已逐键确认初审 5 个问题全部退回 pending，见末节处置。最终全量结构检查与数量见 `quality-review-2026-10-15.md`。**这是**只读的文字来源审查**；未播放或实际听校原音频，不能据此判定哪份 ASR 等于原声。未改 `data/corrections/early.json`、`late.json` 或原始交流记录。`practice_ready` 仅按可作为练习文字的最低清晰度评估，不评价博主建议是否有效。

## 结果

对本轮快照 290 条修订（early 44 / late 246）做全部引用和位置检查，再分层逐项阅读 **53 条**（early 17 / late 36，其中 29 条 `practice_ready:true`）。包含本快照全部“数字或否定字符变动”筛选项，以及未改数字却仍存在独立来源歧义的“三次机会”。筛选会命中“美女”“遛狗”“唯一性”等词形，人工阅读后未将这些误判为数值或否定语义变化。

自动结构检查未发现原 turn 文本过期、无效来源 ID、引用正文与源不符、跨视频引用、所有证据均距 turn 超过 10 秒却未说明的情况。**这不能验证整句是否已可练习**：抽审发现 5 条 `practice_ready:true` 的剩余歧义，已先报父侧。两条涉及关键数字/否定范围，建议优先退回 pending；另外三条仍有残余不通顺的文字。

没有把模型自身口语重复当成必须删掉的错字；也没有将“两个模型一样”视为听校证明。本抽样未发现已改字中无证据更改数值或倒转否定的情况；主要风险是未改部分仍待核，却让整句进入练习。

## 快照边界

审查输入正在追加。本报告指下列固定 SHA 的快照，后加内容和后续修复应重新检查；表内下标均为 **0-based**。原 turn 直接取 `data/dialogue-rounds/`；证据直接读取 `data/alternate-transcripts/` 中被引 segment，并非信任修订内自行写的 `source_text`。

| 输入 | 修订数 | SHA-256 |
|---|---:|---|
| [early.json](../data/corrections/early.json) | 44 | `3de9b5e1991023b0fd2bcb481297c0be9ec272c4ad4168cf4e459a07f05324cf` |
| [late.json](../data/corrections/late.json) | 246 | `1842e4f7810a77c0c8b139644976b0eb1fe9b61809efaf551af6cac2d0fa6482` |

## 具体问题与建议

### F1：数字“三次”仍未交叉确认（优先）

- 位置：`late.json[207]`，`BV1BsuE63EhN-q006` / `turns[0]`，原 turn 210.56–215.04s。
- 修订后：`你给我三次机会我能猜中你啥星座我要猜中了你把你微信给我`，`practice_ready:true`。
- 引源：`BV1BsuE63EhN-sensevoice-w00008-s005`，207.58–214.00s：`…你给我三四7分，我能猜中你啥星座，我要猜中了`；另引 s006 覆盖给微信。
- 问题：修订原因已明确“三次机会独立稿误切仍由原稿保留”，却把整句设为可练习。星座等局部词有支持，次数并未被此独立来源确认。
- 建议：先 `practice_ready:false`，保留原“三次”及存疑说明；需要原片/直接看帧证据才认定次数，不能把“三四7分”猜成“三次机会”。

### F2：关键否定范围不清（优先）

- 位置：`late.json[204]`，`BV1BsuE63EhN-q004` / `turns[2]`，185.28–189.28s。
- 修订后：`我哪不发我就拍生活纪录就给自己看完了有时候给我爸看`，`practice_ready:true`。
- 引源：`BV1BsuE63EhN-sensevoice-w00007-s005`，185.28–190.80s，同样为 `我哪不发…完了有时候给我爸看…`。
- 问题：`完了`的局部词有源，但“我哪不发”仍可能影响发布与否的否定范围，不能因两份稿相同就认为已经听清。
- 建议：先 `practice_ready:false` 并注明句首待核；不能借别的视频的“我哪儿都不发”补这句，也不能自行补“儿/都”。

### F3：只修名词，句首残余乱码未解决

- 位置：`late.json[18]`，`BV1bXJF6iEXn-q008` / `turns[2]`，579.08–591.16s。
- 修订后仍开头 `把你回家吃预制菜…`，`practice_ready:true`。
- 同引源 `BV1bXJF6iEXn-sensevoice-w00021-s007`，579.08–580.82s，为 `反正你回家吃预制菜，你看`。
- 建议：先 false；可由负责者复核是否采用这个同位的明确候选词，须保留机器交叉稿属性。不能仅因“预制菜/气色/现炒”修正就认定整条通过。

### F4：姓名词形修正未消除前半句歧义

- 位置：`late.json[42]`，`BV1bXJF6iEXn-q026` / `turns[0]`，1453.64–1457.84s。
- 修订后 `你有点像大S还有女儿像谁像熊黛林`，仍 `practice_ready:true`。
- 引源 `BV1bXJF6iEXn-sensevoice-w00053-s001`，1456.18–1458.64s，仅为 `像谁像熊黛林，有人说我像`。
- 建议：姓名改字可留；“还有女儿”未由本引用澄清，先 false。不得自行改成“有点儿”等自然句子。

### F5：借物回复的句界和主语仍不清

- 位置：`late.json[196]`，`BV1BsuE63EhN-q001` / `turns[0]`，30.36–43.12s。
- 修订后保留 `…手机关机了把你借我充好了然后…`，`practice_ready:true`。
- 引源 `BV1BsuE63EhN-sensevoice-w00002-s003`，34.48–39.82s：`…手机关机了，完，你借我，我充好了，然后…`；s002 支持充电宝。
- 建议：先 false，或明确核对句界/口语连词后再判断整句。不能将一个物品词修对等同于整条无残余歧义。

## 偏移与保守处理的正例

`early.json[12]` 的 `BV1kJP5z6EDw-q003 / turns[0]` 为 80.08–82.08s，现场独立源在 84.60–86.40s（段间空隙 2.52 秒），另引讲解 241.40–244.40s，已不是同一时刻。该修订明确 `time_alignment_uncertain:true` 且 `practice_ready:false`，处理保守；讲解复述可用于词形候选，不能证明它就是该现场时间的逐字原话。

同样，500万→480万、一个月、十分钟、三分钟与新增“三个”的抽样均找到同位数字证据；“还不饿”“你没遇到我”等没有凭语境反转否定。残余词形未解决却已 false 的条目，未作为错误列出。

## 逐项抽样清单

下表每项均对照原 turn、修订内容与列出的独立 segment；“有源”仅表示来源文字支持所改词形，并不等同真实音频正确率。`true/false` 为审查快照值，后续修改可能已不同。

| 修订下标 | round / section[index] | ready | 实际引用与估计秒数 | 审读记录 |
|---|---|---|---|---|
| early[0] | `BV1vj6yBDE5r-q001` / `commentary[0]` | false | `BV1vj6yBDE5r-sensevoice-w00005-s007` 125.26–129.16s | “跪舔”有独立源；其余长段未因此认定全句清晰，false 合理。 |
| early[1] | `BV1vj6yBDE5r-q002` / `turns[0]` | false | `BV1vj6yBDE5r-sensevoice-w00007-s001` 168.06–171.60s | “正常冰/少冰”在所引窗口存在；模型重叠窗口自身有分歧，保持 false。 |
| early[2] | `BV1vj6yBDE5r-q003` / `turns[1]` | false | `BV1vj6yBDE5r-sensevoice-w00012-s005` 318.92–319.76s<br>`BV1vj6yBDE5r-sensevoice-w00012-s008` 327.68–331.34s | 现场“还不饿”与讲解复述分开可见，未反转否定。 |
| early[3] | `BV1vj6yBDE5r-q004` / `commentary[0]` | false | `BV1vj6yBDE5r-sensevoice-w00016-s008` 442.26–443.76s | 电影座位“坐”有源。 |
| early[4] | `BV1vj6yBDE5r-q005` / `commentary[0]` | false | `BV1vj6yBDE5r-sensevoice-w00019-s005` 524.46–528.96s | “坐第几排”同位置有源；未据此判断关系或同意。 |
| early[5] | `BV1vj6yBDE5r-q006` / `commentary[0]` | false | `BV1vj6yBDE5r-sensevoice-w00023-s001` 616.00–621.70s<br>`BV1vj6yBDE5r-sensevoice-w00023-s002` 621.70–626.14s | 接受度/牵有源；“两三秒”未改，false 合理。 |
| early[6] | `BV14gFYzREk4-q002` / `turns[0]` | false | `BV14gFYzREk4-sensevoice-w00011-s004` 291.16–292.72s | “咱俩”有对应现场模型源；未补造回答。 |
| early[8] | `BV14gFYzREk4-q004` / `commentary[1]` | false | `BV14gFYzREk4-sensevoice-w00018-s006` 499.40–505.40s | 心里话词形有源；否定未变。 |
| early[10] | `BV14gFYzREk4-q006` / `turns[2]` | false | `BV14gFYzREk4-sensevoice-w00021-s003` 569.72–572.24s | 绅士有源；未删除前句“不用”。 |
| early[11] | `BV14gFYzREk4-q008` / `turns[3]` | false | `BV14gFYzREk4-sensevoice-w00024-s007` 663.44–667.82s | 私人影院两次有源；其余歧义未以修词消除。 |
| early[12] | `BV1kJP5z6EDw-q003` / `turns[0]` | false | `BV1kJP5z6EDw-sensevoice-w00004-s001` 84.60–86.40s<br>`BV1kJP5z6EDw-sensevoice-w00009-s004` 241.40–244.40s | 现场估计偏移 2.52 秒；另引 159.32 秒后的讲解。已标 timing uncertain 且 false，不可当同一时刻原声。 |
| early[13] | `BV1kJP5z6EDw-q003` / `commentary[0]` | false | `BV1kJP5z6EDw-sensevoice-w00009-s004` 241.40–244.40s<br>`BV1kJP5z6EDw-sensevoice-w00009-s005` 244.40–249.98s | 正人君子/旭哥均在讲解对应时间有源。 |
| early[14] | `BV1kJP5z6EDw-q007` / `turns[1]` | false | `BV1kJP5z6EDw-sensevoice-w00014-s002` 366.88–370.48s | 家长里短有源；不是/否定关系保留。 |
| early[20] | `BV1kJP5z6EDw-q015` / `turns[1]` | false | `BV1kJP5z6EDw-sensevoice-w00024-s001` 644.12–646.58s | 主动约我有源；不能/疑问保留。 |
| early[27] | `BV1upQdBiEN1-q001` / `turns[1]` | false | `BV1upQdBiEN1-sensevoice-w00002-s006` 43.66–49.96s | 练瑜伽/穿有源；false 保守。 |
| early[34] | `BV1upQdBiEN1-q008` / `turns[0]` | false | `BV1upQdBiEN1-sensevoice-w00017-s003` 459.58–463.12s<br>`BV1upQdBiEN1-sensevoice-w00017-s004` 463.24–464.80s | “廉价”有源，改变含义的修订已留为 false。 |
| early[43] | `BV1upQdBiEN1-q019` / `turns[2]` | false | `BV1upQdBiEN1-sensevoice-w00036-s001` 980.36–980.48s<br>`BV1upQdBiEN1-sensevoice-w00036-s002` 981.32–982.52s | 我+跟朋友逛街来自相邻同窗两段；偏移对应。 |
| late[0] | `BV1bXJF6iEXn-q001` / `turns[0]` | true | `BV1bXJF6iEXn-sensevoice-w00002-s010` 49.24–50.92s | 占用/一分钟有源；数字 1 未变。 |
| late[3] | `BV1bXJF6iEXn-q002` / `turns[1]` | true | `BV1bXJF6iEXn-sensevoice-w00006-s006` 157.88–161.48s | 不让你白拍有完整模型句支持，非凭上下文删否定。 |
| late[7] | `BV1bXJF6iEXn-q004` / `turns[0]` | true | `BV1bXJF6iEXn-sensevoice-w00012-s001` 308.30–312.20s | 新增“发”在完整“头发”中有源；窗口其他乱码未复制。 |
| late[12] | `BV1bXJF6iEXn-q005` / `turns[3]` | true | `BV1bXJF6iEXn-sensevoice-w00014-s002` 365.80–368.92s<br>`BV1bXJF6iEXn-sensevoice-w00014-s003` 368.92–374.98s | 美颜/春熙路支持；SenseVoice“每不”处仅视作模型分歧，未自动照抄。 |
| late[13] | `BV1bXJF6iEXn-q006` / `turns[3]` | false | `BV1bXJF6iEXn-sensevoice-w00017-s007` 474.40–475.12s | 仅末尾网曝有源；前半不清且已 false，适当。 |
| late[14] | `BV1bXJF6iEXn-q007` / `commentary[1]` | true | `BV1bXJF6iEXn-sensevoice-w00019-s002` 506.10–511.32s | 藏着掖着/猥琐有源；字符“一”变化属于词形，并非数量改写。 |
| late[18] | `BV1bXJF6iEXn-q008` / `turns[2]` | true | `BV1bXJF6iEXn-sensevoice-w00021-s007` 579.08–580.82s<br>`BV1bXJF6iEXn-sensevoice-w00021-s008` 581.42–585.74s<br>`BV1bXJF6iEXn-sensevoice-w00021-s009` 585.68–590.00s | F3：句首“把你回家”残留；局部修词不足以通过整句练习。 |
| late[20] | `BV1bXJF6iEXn-q012` / `turns[2]` | true | `BV1bXJF6iEXn-sensevoice-w00025-s004` 682.98–687.42s | 打个分有源；1–10 范围一致。口语重复不直接视作错字。 |
| late[23] | `BV1bXJF6iEXn-q014` / `turns[6]` | true | `BV1bXJF6iEXn-sensevoice-w00029-s005` 797.68–805.12s | 美女有源；“没”在错误词“没你”中，不是句子否定词被删。 |
| late[35] | `BV1bXJF6iEXn-q022` / `turns[4]` | true | `BV1bXJF6iEXn-sensevoice-w00047-s006` 1303.48–1306.30s | 遛狗有源；“六”是同音误字，不是更改数量。 |
| late[42] | `BV1bXJF6iEXn-q026` / `turns[0]` | true | `BV1bXJF6iEXn-sensevoice-w00053-s001` 1456.18–1458.64s | F4：“还有女儿像谁”未解决，证据只覆盖姓名。 |
| late[54] | `BV1bXJF6iEXn-q029` / `commentary[0]` | true | `BV1bXJF6iEXn-sensevoice-w00055-s009` 1538.10–1540.74s | 你俩/踩雷有源；一脸→俩为词形校正，非数量改写。 |
| late[62] | `BV1bXJF6iEXn-q033` / `turns[1]` | false | `BV1bXJF6iEXn-sensevoice-w00059-s007` 1642.90–1651.24s<br>`BV1bXJF6iEXn-sensevoice-w00060-s001` 1652.18–1655.36s | 500万→480万有对应数字源；长句另有乱码，已 false。 |
| late[65] | `BV1bXJF6iEXn-q035` / `turns[2]` | false | `BV1bXJF6iEXn-sensevoice-w00062-s001` 1708.12–1713.76s | 表没在独立稿中存在；整句不清且 false，未把机器疑问当已听清。 |
| late[83] | `BV1sFj26mEu1-q002` / `turns[0]` | true | `BV1sFj26mEu1-sensevoice-w00003-s001` 57.20–62.12s | 哪儿都不发有完整同位句支持；须区分这是原话记录，不验证是否真的未发布。 |
| late[88] | `BV1sFj26mEu1-q008` / `commentary[0]` | true | `BV1sFj26mEu1-sensevoice-w00011-s007` 301.42–309.10s | 素未谋面/萍水相逢有源；“未”是成语词形。 |
| late[95] | `BV1sFj26mEu1-q016` / `commentary[1]` | true | `BV1sFj26mEu1-sensevoice-w00036-s003` 985.82–986.96s<br>`BV1sFj26mEu1-sensevoice-w00036-s004` 986.96–993.62s<br>`BV1sFj26mEu1-sensevoice-w00036-s005` 993.68–998.48s<br>`BV1sFj26mEu1-sensevoice-w00036-s006` 998.54–1006.10s | 唯一性/惯犯/独一无二有源；未改变其余“从来没有/不是”。 |
| late[124] | `BV1tVKf6cE5G-q001` / `turns[0]` | true | `BV1tVKf6cE5G-sensevoice-w00002-s002` 31.90–34.12s<br>`BV1tVKf6cE5G-sensevoice-w00002-s003` 34.24–37.36s | 帮我个忙和后半拍照请求均在同位源中。 |
| late[130] | `BV1tVKf6cE5G-q005` / `commentary[0]` | false | `BV1tVKf6cE5G-sensevoice-w00010-s001` 252.00–255.96s<br>`BV1tVKf6cE5G-sensevoice-w00010-s002` 255.96–257.94s<br>`BV1tVKf6cE5G-sensevoice-w00010-s003` 257.94–261.96s<br>`BV1tVKf6cE5G-sensevoice-w00010-s004` 261.90–268.14s | 拍照/放弃吧有源；三种价值未变，false 保持。 |
| late[161] | `BV1VrMt6tEEx-q010` / `commentary[1]` | true | `BV1VrMt6tEEx-sensevoice-w00019-s001` 504.00–508.98s | 你没遇到我有同位独立稿，支持修复否定；未凭常识补“不”。 |
| late[170] | `BV1VrMt6tEEx-q015` / `commentary[1]` | false | `BV1VrMt6tEEx-sensevoice-w00025-s006` 687.00–690.96s<br>`BV1VrMt6tEEx-sensevoice-w00025-s007` 691.14–694.20s<br>`BV1VrMt6tEEx-sensevoice-w00025-s008` 694.20–699.54s | 用不好使有源；其余“启示”等仍不清，false 合理。 |
| late[181] | `BV1VrMt6tEEx-q024` / `commentary[0]` | false | `BV1VrMt6tEEx-sensevoice-w00040-s004` 1102.38–1110.24s<br>`BV1VrMt6tEEx-sensevoice-w00040-s005` 1110.30–1116.36s<br>`BV1VrMt6tEEx-sensevoice-w00040-s006` 1116.30–1119.60s | 字里行间/当放屁/下三路有源；末尾仍存疑，false 合理。 |
| late[188] | `BV1VrMt6tEEx-q027` / `turns[2]` | true | `BV1VrMt6tEEx-sensevoice-w00046-s004` 1270.74–1276.92s<br>`BV1VrMt6tEEx-sensevoice-w00046-s005` 1278.42–1284.54s | 一多月→一个月有独立原句支持；数量/单位连带复核通过。 |
| late[189] | `BV1VrMt6tEEx-q028` / `turns[2]` | true | `BV1VrMt6tEEx-sensevoice-w00048-s002` 1322.42–1325.00s | 陷进去有独立原句；一群→进去非数字更改。 |
| late[191] | `BV1VrMt6tEEx-q030` / `commentary[1]` | true | `BV1VrMt6tEEx-sensevoice-w00051-s002` 1402.70–1406.00s | 正儿八经有源；八在固定词形中，不是数量。 |
| late[193] | `BV1VrMt6tEEx-q032` / `turns[2]` | true | `BV1VrMt6tEEx-sensevoice-w00052-s005` 1437.18–1444.26s | 观察项：多少千克有源；“压力”两稿同样存在，未听音不能擅改成哑铃。 |
| late[196] | `BV1BsuE63EhN-q001` / `turns[0]` | true | `BV1BsuE63EhN-sensevoice-w00002-s002` 30.58–32.80s<br>`BV1BsuE63EhN-sensevoice-w00002-s003` 34.48–39.82s | F5：“把你借我充好了”残留，需核句界或先 false。 |
| late[197] | `BV1BsuE63EhN-q001` / `turns[2]` | true | `BV1BsuE63EhN-sensevoice-w00002-s006` 47.08–52.60s | 充电/十分钟有源，未改时长。 |
| late[198] | `BV1BsuE63EhN-q002` / `commentary[0]` | true | `BV1BsuE63EhN-sensevoice-w00003-s001` 56.30–59.60s | 依旧有源；一就→依旧为词形。 |
| late[204] | `BV1BsuE63EhN-q004` / `turns[2]` | true | `BV1BsuE63EhN-sensevoice-w00007-s005` 185.28–190.80s | F2：两稿“我哪不发”否定范围不清，先 false。 |
| late[207] | `BV1BsuE63EhN-q006` / `turns[0]` | true | `BV1BsuE63EhN-sensevoice-w00008-s005` 207.58–214.00s<br>`BV1BsuE63EhN-sensevoice-w00008-s006` 213.94–215.68s | F1：三次机会仅原稿保留，所引“三四7分”未独立确认数字，先 false。 |
| late[213] | `BV1BsuE63EhN-q010` / `turns[1]` | true | `BV1BsuE63EhN-sensevoice-w00017-s001` 448.06–452.68s | 默字有同位源；口吃式重复仍保留，不擅自删掉。 |
| late[214] | `BV1BsuE63EhN-q011` / `turns[1]` | true | `BV1BsuE63EhN-sensevoice-w00017-s003` 454.78–459.70s | 三分钟和付出型人格均有同位源；非对真实人格作诊断。 |
| late[217] | `BV1BsuE63EhN-q013` / `commentary[0]` | false | `BV1BsuE63EhN-sensevoice-w00018-s008` 493.16–495.68s<br>`BV1BsuE63EhN-sensevoice-w00019-s002` 508.68–510.78s | 教给/意犹未尽有源；三秒未改变；另有未清文本，false 合理。 |
| late[234] | `BV1BsuE63EhN-q027` / `commentary[0]` | true | `BV1BsuE63EhN-sensevoice-w00044-s002` 1207.00–1212.94s<br>`BV1BsuE63EhN-sensevoice-w00044-s004` 1213.60–1219.66s<br>`BV1BsuE63EhN-sensevoice-w00044-s007` 1229.20–1230.58s | 玷污/七情六欲/镜面原理支持；开头“死尿屁”尚未在本次所引片段解决，建议补核，勿认整段校尽。 |
| late[237] | `BV1BsuE63EhN-q029` / `turns[0]` | true | `BV1BsuE63EhN-sensevoice-w00045-s005` 1242.74–1245.80s | 新增数字“三个”有明确独立原句；未凭提问习惯补数字。 |

## 增量复核：451 条引用结构、额外 16 条文字审读

复核时间：`2026-10-15T17:29:20+08:00`。输入已增量和重排，**修订数组下标仅对所在快照有效**；定位和后续修复必须用 `round_id + section + turn_index`，不得拿初审的数组下标直接修改新版。

- `early.json`：44 条；SHA-256 `3de9b5e1991023b0fd2bcb481297c0be9ec272c4ad4168cf4e459a07f05324cf`。
- `late.json`：407 条；SHA-256 `d9e4aa1f8367cc05736edcf4d8d81494ac9c7b45af9eb750aa37749ffac23dc8`。

451 条结构检查仍为 0 个引用/原文/偏移错误，稳定修订键无重复。对新增第 10、16、18 集再逐项阅读 16 条，累计 **69 条**；此前 53 条的初审表保留原快照值。本轮未新增必须改字的结论，已 false 的数字/残句分歧未被自动升级为可练习。

初审问题在本增量快照中的状态：

| 问题 | 稳定定位 | 现值 | 状态 |
|---|---|---|---|
| F1 | `BV1BsuE63EhN-q006 / turns[0]` | ready=false | 已按建议保留次数存疑；不认定三次已听清 |
| F2 | `BV1BsuE63EhN-q004 / turns[2]` | ready=false | 已按建议保留否定范围待核 |
| F3 | `BV1bXJF6iEXn-q008 / turns[2]` | ready=false | 已按建议阻止残句进入练习 |
| F4 | `BV1bXJF6iEXn-q026 / turns[0]` | ready=true | 仍建议 false；“还有女儿”未解决 |
| F5 | `BV1BsuE63EhN-q001 / turns[0]` | ready=true | 仍建议 false；“把你借我充好了”未解决 |

| 增量快照下标 | round / section[index] | ready | 实际引用与估计秒数 | 审读记录 |
|---|---|---|---|---|
| late[0] | `BV1CjV16KEHe-q002` / `commentary[0]` | false | `BV1CjV16KEHe-sensevoice-w00005-s006` 131.80–138.28s<br>`BV1CjV16KEHe-sensevoice-w00006-s002` 145.04–147.50s<br>`BV1CjV16KEHe-sensevoice-w00006-s004` 150.32–154.10s<br>`BV1CjV16KEHe-sensevoice-w00006-s005` 154.16–156.02s<br>`BV1CjV16KEHe-sensevoice-w00006-s007` 164.30–169.16s | 变着法/没起作用/纯享版/旭哥/礼品均有源；“实实物者”等残留，false 恰当。 |
| late[1] | `BV1CjV16KEHe-q003` / `commentary[0]` | false | `BV1CjV16KEHe-sensevoice-w00010-s007` 268.44–274.86s | 拐弯抹角/借口有源；后半仍有机器乱码，false 恰当。 |
| late[36] | `BV1CjV16KEHe-q020` / `turns[2]` | false | `BV1CjV16KEHe-sensevoice-w00053-s007` 1479.46–1479.94s | 邂逅有源，但独立段只到“男”，未确认“男友”全词，false 恰当。 |
| late[70] | `BV1CjV16KEHe-q044` / `turns[1]` | true | `BV1CjV16KEHe-sensevoice-w00087-s006` 2421.92–2430.50s<br>`BV1CjV16KEHe-sensevoice-w00087-s007` 2431.22–2438.00s<br>`BV1CjV16KEHe-sensevoice-w00088-s002` 2438.40–2441.64s | 矜持在前两引源明确，末引“矜此”仍有模型词形错；保持原始证据。 |
| late[71] | `BV1CjV16KEHe-q045` / `turns[5]` | false | `BV1CjV16KEHe-sensevoice-w00090-s003` 2496.68–2499.80s<br>`BV1CjV16KEHe-sensevoice-w00090-s006` 2503.88–2507.18s | 冷有源；“喜欢的人就很乐”“爱人”等仍未清，false 恰当。 |
| late[318] | `BV1gb8M6nENB-q001` / `turns[0]` | true | `BV1gb8M6nENB-sensevoice-w00002-s003` 32.20–37.42s | 话费与完整热点请求有源，未变更“没”。 |
| late[324] | `BV1gb8M6nENB-q005` / `commentary[2]` | true | `BV1gb8M6nENB-sensevoice-w00007-s005` 184.32–190.20s | 八九不离十/水瓶座有源；固定词形修订，非新造生日数值。 |
| late[340] | `BV1gb8M6nENB-q017` / `turns[5]` | true | `BV1gb8M6nENB-sensevoice-w00031-s005` 852.54–856.80s | 狠狠探索有源；没有将两个“很”简单当口吃删去。 |
| late[341] | `BV1gb8M6nENB-q018` / `turns[1]` | false | `BV1gb8M6nENB-sensevoice-w00032-s001` 868.12–873.46s | 意料之中/多无聊/有心栽花有源；成语后半仍乱码，已 false，没有凭熟悉成语补全。 |
| late[358] | `BV1gb8M6nENB-q032` / `turns[3]` | true | `BV1gb8M6nENB-sensevoice-w00047-s007` 1309.90–1314.64s | 咱俩去看电影有同位源，未凭约会场景猜人称。 |
| late[359] | `BV1gb8M6nENB-q033` / `turns[2]` | false | `BV1gb8M6nENB-sensevoice-w00048-s004` 1326.44–1331.36s | 上吊/不许变/100年有源；后半原“十个”和模型“1个”仍分歧，已 false。 |
| late[361] | `BV1P5he6SEys-q002` / `commentary[1]` | true | `BV1P5he6SEys-sensevoice-w00010-s001` 252.24–259.20s | 话里面有同位源；长讲解未被改写成新建议。 |
| late[374] | `BV1P5he6SEys-q008` / `turns[2]` | true | `BV1P5he6SEys-sensevoice-w00018-s007` 502.22–506.00s | 幼师/幼儿园有同位源，“六二元”为词形误识别。 |
| late[385] | `BV1P5he6SEys-q013` / `commentary[0]` | true | `BV1P5he6SEys-sensevoice-w00033-s001` 896.06–903.80s | 冷读有源；未据词形修订推定读心有效。 |
| late[387] | `BV1P5he6SEys-q013` / `turns[0]` | false | `BV1P5he6SEys-sensevoice-w00032-s005` 881.56–885.16s<br>`BV1P5he6SEys-sensevoice-w00032-s006` 885.10–888.16s | 高冷/开始有源；模型“生人勿尽”同样存疑，false 保守，没有凭常识自动修成“生人勿近”。 |
| late[406] | `BV1P5he6SEys-q028` / `turns[2]` | true | `BV1P5he6SEys-sensevoice-w00052-s001` 1428.30–1432.98s | 海参有同位源，其余菜名和语气未动。 |

## 父侧最终处置

2026-10-15：后9集最终修订文件为452项。父侧逐键重新读取 F1–F5，上述5项的 `practice_ready` 均为 `false`，不能据这些局部修字把整句或整题提升为优先练习。抽样表保留初审快照值供追溯；初审数不是最终全量修订数。另将第10集 q021 的编辑标题从“耳环喜欢哪个名字”改为“喜欢哪个明星？”，保留 `original_title` 与同位来源 ID；人物回答仍待核。全量引用与最终题库数字见 `quality-review-2026-10-15.md`。
