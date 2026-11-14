# 2024级 药学 药理学 实验

> 来源：[考试| 24药学 药理学实验](https://mp.weixin.qq.com/s?__biz=Mzk0MjQzMzk4Nw==&mid=2247488569&idx=3&sn=98867d5130c4de7875435f1b0d78ca22&chksm=c2c26795f5b5ee83625e5b8bdf482917d13cdd9d9933c88dcf7704bcde0dd96b8fc4d8c6743f)（2026-06-19，B1休息区（fdsy药理学合集））· 原文声明：仅供学习交流，严禁商用  
> 正本：[`bank/exams/24-pharm-lab.yaml`](../../bank/exams/24-pharm-lab.yaml) · 原始回忆：[`bank/raw/24-pharm-lab.md`](../../bank/raw/24-pharm-lab.md)

| 题型 | 分值 |
|---|---|
| 填空题 | 共10分 |
| 简答题 | 共4分 |
| 实验设计题 | 共6分 |

## 填空题

**1. 尼可刹米给家兔注射时的剂量为90mg/kg，现在注射的浓度为25%，2.4kg体重的家兔需注射此种注射液______mL。**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

0.864

**解析**

90×2.4=216 mg；25%=250 mg/ml；216/250

**知识点**：[药理学实验方法](../../knowledge/cards/lab.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-001`）

</details>

---

**2. 热板法实验应选用______性小鼠**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

雌

**解析**

雄鼠受热后阴囊松弛触及热板，易致误判

**知识点**：[药理学实验方法](../../knowledge/cards/lab.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-002`）

</details>

---

**3. 3R原则分别是______、______、______。**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

替代（Replacement）、减少（Reduction）、优化（Refinement）

**知识点**：[药理学实验方法](../../knowledge/cards/lab.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-003`）

</details>

---

**4. 有机磷中毒解救时，应先用______，再用______。**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

阿托品；解磷定（氯解磷定/碘解磷定）

**知识点**：[有机磷酸酯类中毒与解救](../../knowledge/cards/op_poisoning.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-004`）

</details>

---

## 简答题

**5. LD50是什么？测定药物的LD50有什么意义以及主要的影响因素。**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：半数有效量/半数致死量（ED50/LD50/EC50）〕
**标准答案**

**ED₅₀**：量反应中引起50%最大效应的剂量（浓度表示为EC₅₀）；质反应中引起50%实验动物出现阳性反应的剂量。**LD₅₀**：引起50%实验动物死亡的剂量。

**评分要点**

- 量反应/质反应两种定义
- LD₅₀ 意义：评价急性毒性；与ED₅₀合算治疗指数
- LD₅₀ 影响因素：动物种属、品系、性别、体重、年龄；给药途径与速度；溶媒与浓度；环境温度；实验季节与时间

〔引自知识卡：药理学实验方法 · LD₅₀〕
见知识点“半数有效量/半数致死量”。测定意义：评价药物急性毒性大小；结合ED₅₀计算治疗指数，评价安全性；为后续实验和临床剂量提供依据。影响因素：动物种属、品系、性别、年龄、体重、健康状况；给药途径、速度、溶剂和浓度；环境温度、湿度；季节、昼夜节律；分组随机化及剂量设计。

**解析**

三问：定义、意义（急性毒性、治疗指数）、影响因素（动物、给药、环境三方面）。

**知识点**：[半数有效量/半数致死量（ED50/LD50/EC50）](../../knowledge/cards/median_dose.md)、[药理学实验方法](../../knowledge/cards/lab.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-005`）

</details>

---

## 实验设计题

**6. 药品柜中有两瓶药品，分别是吗啡和阿托品，标签模糊辨认不清，请你设计一个药理实验进行鉴别，并阐述设计原理和结果判定。**

<details><summary>答案与解析 · AI 草稿</summary>

**答案**

〔引自知识卡：药理学实验方法 · 鉴别吗啡与阿托品实验设计〕
原理：吗啡激动阿片受体，**缩瞳**（针尖样瞳孔）、镇痛、抑制呼吸；阿托品阻断M受体，**扩瞳**、抑制腺体分泌、加快心率。
方案：取家兔2只（或小鼠），记录正常瞳孔直径（测瞳尺，同一光照条件）、对光反射；分别给予两瓶药物（家兔滴眼或注射），一定时间后再测瞳孔。结果：瞳孔缩小者为吗啡，扩大者为阿托品。
可补充：小鼠热板法/扭体法测痛阈，痛阈明显提高者为吗啡；或观察呼吸频率（吗啡抑制）。设置生理盐水对照，平行操作。

**解析**

实验设计题要写全：原理（缩瞳 vs 扩瞳）、对象与分组、操作、观察指标、结果判定、对照。

**知识点**：[药理学实验方法](../../knowledge/cards/lab.md)、[阿片类镇痛药](../../knowledge/cards/opioids.md)、[M受体阻断药（阿托品/东莨菪碱）](../../knowledge/cards/atropine.md)

**教材出处**：待检索标注（`python tools/annotate.py suggest 24-pharm-lab-006`）

</details>

---

*本页由 `python tools/bank.py docs` 生成，请勿手改。*
