# 2023级 预防医学 药理学 期中

> 来源：[考试| 23预防 药理期中](https://mp.weixin.qq.com/s?__biz=Mzk0MjQzMzk4Nw==&mid=2247487590&idx=1&sn=3493e8885bb6b375ea2e2ab903350c85&chksm=c2c263caf5b5eadc8530577218d05a097b1361c9cb8ca5715841c16587e445aa24d5bc65070a)（2025-11-26，B1休息区（fdsy药理学合集））· 原文声明：仅供学习交流，严禁商用  
> 正本：[`bank/exams/23-prev-midterm.yaml`](../../bank/exams/23-prev-midterm.yaml) · 原始回忆：[`bank/raw/23-prev-midterm.md`](../../bank/raw/23-prev-midterm.md)

| 题型 | 分值 |
|---|---|
| 问答题 | 2分×8 |
| 名词解释 | — |
| 多选题 | — |
| 单选题 | — |

**回忆者备注**：tips：英语不多，会考名称和机制

## 问答题

**1. 病例**
　（1）普萘洛尔用于治疗有支气管哮喘病史的高血压患者为什么出现了异常症状
　（2）使用β受体阻断药治疗高血压的注意事项

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：β受体阻断药 · 病例：哮喘患者用普萘洛尔（23预防）〕
普萘洛尔为非选择性β受体阻断药，阻断支气管平滑肌β₂受体，使支气管收缩、气道阻力增加，诱发或加重哮喘发作。
注意事项：支气管哮喘、严重心动过缓、重度房室传导阻滞、急性心衰患者禁用；如必须使用选β₁选择性药物（美托洛尔）并谨慎；从小剂量开始；长期用药不可突然停药，应逐渐减量；糖尿病患者注意掩盖低血糖。

**解析**

病例要点：非选择性 β 阻断药阻断支气管 β₂ 受体诱发哮喘；注意事项按禁忌、选药、剂量、停药、合并症写。

**知识点**：[β受体阻断药](../../knowledge/cards/beta_blockers.md)、[平喘药](../../knowledge/cards/antiasthma.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-001`）

</details>

---

**2. 比较地西泮和苯巴比妥的药理作用机制的差异，比较两者治疗失眠的作用特点**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：地西泮 vs 苯巴比妥〕
| 维度 | 地西泮（苯二氮䓬类） | 苯巴比妥（巴比妥类） |
|---|---|---|
| 作用位点 | GABA_A受体BZ结合位点 | GABA_A受体巴比妥结合位点 |
| 机制 | 增强GABA作用，**增加Cl⁻通道开放频率**；无GABA时无作用 | **延长Cl⁻通道开放时间**；大剂量可直接开放Cl⁻通道；抑制谷氨酸 |
| 量效 | 小剂量抗焦虑→镇静催眠→抗惊厥，大剂量**不产生麻醉** | 镇静→催眠→抗惊厥→麻醉→延髓麻痹 |
| 睡眠结构 | 缩短REM作用弱，延长NREM第2期 | 显著缩短REM，停药反跳多梦 |
| 安全性 | 治疗指数高，呼吸抑制轻 | 安全范围窄，过量呼吸抑制致死 |
| 肝药酶 | 诱导弱 | **强诱导剂**，耐受快 |
| 依赖性 | 较轻 | 较重 |
| 中毒解救 | **氟马西尼** | 无特异拮抗药；碱化尿液（碳酸氢钠）、对症 |
| 治疗失眠 | 首选之一（现更多用Z类药） | 已不作催眠首选 |

**解析**

机制差异的关键词：“开放频率” vs “开放时间”；治疗失眠比较睡眠结构、安全性、依赖性、肝药酶诱导。

**知识点**：[镇静催眠药（BZ/巴比妥/新型）](../../knowledge/cards/sedative_hypnotics.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-002`）

</details>

---

## 名词解释

**3. pKa的中文及含义**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：pKa 与离子障（尿液 pH 影响排泄）〕
**标准答案**

**pKa**：弱酸或弱碱性药物在溶液中50%解离时的pH值。**离子障**：非解离型药物脂溶性高可跨膜，解离型药物难以跨膜而被限制在膜一侧的现象。

**评分要点**

- Henderson–Hasselbalch：弱酸 10^(pH−pKa) = [A⁻]/[HA]；弱碱 10^(pKa−pH) = [BH⁺]/[B]
- 弱酸性药在碱性环境中解离多 → 跨膜少
- 碱化尿液 → 弱酸性药物解离增加、肾小管重吸收减少 → 排泄加快（阿司匹林、苯巴比妥中毒用碳酸氢钠）
- 弱碱性药物则酸化尿液加速排泄

**知识点**：[pKa 与离子障（尿液 pH 影响排泄）](../../knowledge/cards/pKa_ion_trapping.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-003`）

</details>

---

**4. 肝肠循环**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：肝肠循环〕
**标准答案**

经胆汁排入肠道的药物，部分在小肠被重吸收（结合型经水解后）经门静脉返回肝脏，再进入体循环的过程。

**评分要点**

- 胆汁排泄 → 肠道重吸收 → 门静脉回肝
- 使药物作用时间延长（如洋地黄毒苷）
- 阻断肝肠循环可加速排泄：考来烯胺用于洋地黄毒苷中毒

**知识点**：[肝肠循环](../../knowledge/cards/enterohepatic.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-004`）

</details>

---

**5. potency**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：效价强度〕
**标准答案**

产生一定效应（通常为50%最大效应）所需的药物剂量或浓度。所需剂量越小，效价强度越大。

**评分要点**

- 达到等效所需的剂量
- 剂量越小效价越高
- 主要反映与受体的亲和力
- 与效能不一定平行：如环戊噻嗪效价强于氢氯噻嗪，但两者利尿效能相同

**知识点**：[效价强度](../../knowledge/cards/potency.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-005`）

</details>

---

**6. first pass effect**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：首过消除（首过效应）〕
**标准答案**

口服药物经胃肠道吸收后，经门静脉入肝；在首次通过**肠壁和肝脏**时部分被代谢灭活，使进入体循环的有效药量减少，称首过消除（首过效应）。

**评分要点**

- 口服给药
- 部位：肠黏膜和肝脏
- 结果：进入体循环药量减少、生物利用度降低
- 首过效应强的药：硝酸甘油、吗啡、利多卡因、普萘洛尔
- 避免：舌下、直肠、注射、吸入等给药

**知识点**：[首过消除（首过效应）](../../knowledge/cards/first_pass.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-006`）

</details>

---

**7. agonist**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：激动药〕
**标准答案**

对受体既有**亲和力**又有**内在活性**的药物，能与受体结合并激活受体产生效应。

**评分要点**

- 亲和力 + 内在活性（α=1）
- 完全激动药：如吗啡
- 部分激动药：亲和力强、内在活性弱（0<α<1），如丁丙诺啡、喷他佐辛

**知识点**：[激动药](../../knowledge/cards/agonist.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-007`）

</details>

---

**8. t1/2**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：消除半衰期〕
**标准答案**

血浆药物浓度下降一半所需的时间（t₁/₂）。一级动力学下 t₁/₂ = 0.693/ke，为恒定值。

**评分要点**

意义：
- 反映药物消除快慢，是确定给药间隔的依据
- 预测达稳态时间：恒速恒量给药约4~5个t₁/₂
- 预测消除时间：停药约5个t₁/₂后体内药量剩约3%（1/32）
- 肝肾功能不全时t₁/₂延长，应调整剂量
- 一级动力学消除约需5个t₁/₂基本消除完毕

**知识点**：[消除半衰期](../../knowledge/cards/half_life.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-008`）

</details>

---

## 多选题

**9. 人工冬眠合剂**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

氯丙嗪 + 异丙嗪 + 哌替啶

**知识点**：[抗精神病药](../../knowledge/cards/antipsychotics.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-009`）

</details>

---

**10. 氯丙嗪作用**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

抗精神病、镇吐、调节体温、阻断α受体、阻断M受体、影响内分泌

**知识点**：[抗精神病药](../../knowledge/cards/antipsychotics.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-010`）

</details>

---

**11. 主动转运特点**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

逆浓度梯度；耗能；需载体；有饱和性；有竞争性抑制

**知识点**：[跨膜转运（被动/主动/膜动）](../../knowledge/cards/transport.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-011`）

</details>

---

## 单选题

**12. 计算表观分布容积**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

Vd = 体内药量/血药浓度（D/C₀）

**知识点**：[表观分布容积](../../knowledge/cards/vd.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-012`）

</details>

---

**13. 碱性尿液，弱酸性药物**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

解离增多，重吸收减少，排泄加快

**知识点**：[pKa 与离子障（尿液 pH 影响排泄）](../../knowledge/cards/pKa_ion_trapping.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-013`）

</details>

---

**14. pD2**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

pD₂ = −lgKD，亲和力指数，越大亲和力越大

**知识点**：[亲和力：KD 与 pD2](../../knowledge/cards/affinity_KD.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-014`）

</details>

---

**15. 非竞争性拮抗药对量效曲线的影响**

> 题目完整度：仅题干（无选项）

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

激动药量效曲线右移，最大效应降低

**知识点**：[竞争性拮抗药](../../knowledge/cards/competitive_antagonist.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 23-prev-midterm-015`）

</details>

---

*本页由 `python tools/bank.py docs` 生成，请勿手改。*
