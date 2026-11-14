# 2021级 临床医学（八年制） 药理学 缓考

> 来源：[考试| 21临八 药理（缓）](https://mp.weixin.qq.com/s?__biz=Mzk0MjQzMzk4Nw==&mid=2247486632&idx=1&sn=77383d842a1646c184752d33194e7256&chksm=c2c27f04f5b5f61245e55fe2a155ce45873f8a93ad8b38ea61286f6247a81e2e5aaf4aff7a47)（2025-02-13，B1休息区（fdsy药理学合集））· 原文声明：仅供学习交流，严禁商用  
> 正本：[`bank/exams/21-lin8-makeup.yaml`](../../bank/exams/21-lin8-makeup.yaml) · 原始回忆：[`bank/raw/21-lin8-makeup.md`](../../bank/raw/21-lin8-makeup.md)

| 题型 | 分值 |
|---|---|
| 名词解释 | — |
| 问答题 | — |

## 名词解释

**1. agonist**

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

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-001`）

</details>

---

**2. competitive antagonist**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：竞争性拮抗药〕
**标准答案**

能与激动药**可逆性竞争**同一受体的拮抗药。

**评分要点**

- 与激动药竞争同一受体，结合可逆
- 使激动药量效曲线**平行右移**
- **最大效应不变**（增加激动药浓度可完全克服）
- 拮抗强度用 pA₂ 表示
- 例：阿托品拮抗乙酰胆碱

**解析**

英文名解：中文名 + 定义 + 曲线特点（平行右移、最大效应不变）。

**知识点**：[竞争性拮抗药](../../knowledge/cards/competitive_antagonist.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-002`）

</details>

---

**3. 半衰期**

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

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-003`）

</details>

---

**4. steady state concentration**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：稳态血药浓度〕
**标准答案**

恒速恒量多次给药（或恒速静滴）时，经4~5个t₁/₂，单位时间内进入体内的药量与消除量达到平衡，血药浓度在一定范围内稳定波动，此时的血药浓度称稳态血药浓度（坪值）。

**评分要点**

- 恒速恒量给药
- 约4~5个t₁/₂达到
- 达稳态时间只取决于t₁/₂，与剂量、给药间隔无关
- 稳态平均浓度与给药速率（剂量/间隔）成正比
- 缩短达稳态时间：首剂给负荷量

**知识点**：[稳态血药浓度](../../knowledge/cards/css.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-004`）

</details>

---

**5. apparent volume of distribution**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：表观分布容积〕
**标准答案**

体内药物按血浆药物浓度均匀分布时所需的理论体液容积，Vd = A/C（体内药量/血药浓度）。

**评分要点**

- 并非真实生理容积
- 推测药物分布范围：Vd≈5 L（70 kg）主要在血浆；10~20 L 在细胞外液；≈40 L 分布全身体液；远大于体液量提示组织中浓集
- 计算达到期望血药浓度所需剂量
- Vd 越大，药物排泄越慢

**知识点**：[表观分布容积](../../knowledge/cards/vd.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-005`）

</details>

---

## 问答题

**6. ARB降压机制；ACEI引发无痰性干咳机制**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：RAAS 抑制药（ACEI/ARB） · ARB（氯沙坦、缬沙坦）〕
选择性阻断AT₁受体，拮抗AngⅡ的缩血管、促醛固酮分泌和促增生作用（无论AngⅡ经ACE或糜酶途径生成均可阻断）；不影响缓激肽降解，故**不引起干咳**和血管神经性水肿；AT₁阻断后AngⅡ反馈增多可激动AT₂受体，产生舒血管、抗增生作用。

〔引自知识卡：ACEI 致干咳机制〕
**标准答案**

ACEI（如卡托普利、依那普利）抑制激肽酶Ⅱ（即ACE），使缓激肽、P物质降解减少而在肺内蓄积，刺激呼吸道感受器（并促进PG合成），引起刺激性**无痰干咳**。

**评分要点**

- ACE = 激肽酶Ⅱ
- 缓激肽、P物质蓄积
- 前列腺素合成增加
- 处理：换用ARB（缬沙坦/氯沙坦），因其不影响缓激肽代谢

**解析**

ARB 降压与 ACEI 干咳两问各自独立作答。

**知识点**：[RAAS 抑制药（ACEI/ARB）](../../knowledge/cards/raas.md)、[ACEI 致干咳机制](../../knowledge/cards/acei_cough.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-006`）

</details>

---

**7. 硝苯地平抗心绞痛机制**

> 题目完整度：仅考点

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：钙通道阻滞药 · 硝苯地平抗心绞痛机制〕
① 扩张冠状动脉、解除冠脉痉挛，增加心肌供血（对**变异型心绞痛**效果最好，为首选之一）；② 扩张外周小动脉，降低后负荷和心肌耗氧；③ 减少Ca²⁺内流，防止缺血心肌细胞钙超载，保护心肌；④ 抑制血小板聚集。缺点：反射性心率加快，可与β受体阻断药合用。

**解析**

四点：扩冠解痉、降后负荷、防钙超载、抗血小板。

**知识点**：[钙通道阻滞药](../../knowledge/cards/ccb.md)、[抗心绞痛药](../../knowledge/cards/antianginal.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-007`）

</details>

---

**8. 长期大量使用糖皮质激素的不良反应**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：糖皮质激素不良反应〕
长期大量应用糖皮质激素的不良反应分为长期用药反应和停药反应两类。

**解析**

高频题。

**知识点**：[糖皮质激素不良反应](../../knowledge/cards/gc_adverse.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-008`）

</details>

---

**9. 列举两种喹诺酮类药物，简述抗菌机制以及不良反应**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：喹诺酮类〕
**代表药**

诺氟沙星、环丙沙星、氧氟沙星、左氧氟沙星、莫西沙星（-floxacin 沙星）。

**作用机制**

① 抑制**DNA回旋酶（拓扑异构酶Ⅱ）**——G⁻菌的主要靶点：阻止DNA超螺旋形成，干扰DNA复制；② 抑制**拓扑异构酶Ⅳ**——G⁺菌的主要靶点：干扰子代DNA解环连和分离。最终DNA断裂、细菌死亡（杀菌）。对哺乳动物拓扑异构酶影响很小。

**不良反应**

胃肠道反应；中枢神经系统反应（头痛、失眠、诱发癫痫，与NSAIDs合用加重）；光敏反应；**软骨损害**（关节痛、跟腱炎/断裂 → 18岁以下儿童、孕妇、哺乳期慎用/禁用）；Q-T间期延长；血糖紊乱；过敏。

**解析**

列举诺氟沙星、环丙沙星等；机制 + 不良反应（尤其软骨损害）。

**知识点**：[喹诺酮类](../../knowledge/cards/quinolones.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 21-lin8-makeup-009`）

</details>

---

*本页由 `python tools/bank.py docs` 生成，请勿手改。*
